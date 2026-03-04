from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import httpx

from .crypto import KeyPair, generate_key_pair, get_public_key, sign, build_signature_payload
from .errors import (
    AuthenticationError,
    AuthoraError,
    AuthorizationError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    TimeoutError,
    ValidationError,
)
from .permissions import match_any_permission
from .types import (
    Agent,
    AgentVerification,
    Delegation,
    McpProxyResponse,
    PermissionCheckResult,
)

_DEFAULT_BASE_URL = "https://api.authora.dev/api/v1"

import re

_CAMEL_RE = re.compile(r"(?<=[a-z0-9])([A-Z])")
_SNAKE_RE = re.compile(r"_([a-z])")


def _to_camel(name: str) -> str:
    return _SNAKE_RE.sub(lambda m: m.group(1).upper(), name)


def _to_snake(name: str) -> str:
    return _CAMEL_RE.sub(r"_\1", name).lower()


def _keys_to_camel(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {_to_camel(k): _keys_to_camel(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_keys_to_camel(i) for i in obj]
    return obj


def _keys_to_snake(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {_to_snake(k): _keys_to_snake(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_keys_to_snake(i) for i in obj]
    return obj


def _unwrap_response(body: Any) -> Any:
    if isinstance(body, dict) and "data" in body:
        data = body["data"]
        pagination = body.get("pagination") or body.get("meta")
        if isinstance(data, list) and isinstance(pagination, dict):
            return {
                "items": data,
                "total": pagination.get("total", len(data)),
                "page": pagination.get("page"),
                "limit": pagination.get("limit"),
            }
        if isinstance(data, list):
            return {"items": data}
        return data
    return body


def _parse_error_body(body: Any) -> Dict[str, Any]:
    if isinstance(body, dict):
        return {
            "message": body.get("message"),
            "code": body.get("code"),
            "details": body.get("details"),
            "retry_after": body.get("retryAfter") or body.get("retry_after"),
        }
    if isinstance(body, str):
        return {"message": body}
    return {}


def _raise_for_status(status: int, body: Any, method: str, path: str) -> None:
    parsed = _parse_error_body(body)
    prefix = f"{method} {path}"
    if status == 401:
        raise AuthenticationError(
            parsed.get("message") or f"{prefix}: Authentication failed",
            details=parsed.get("details"),
        )
    if status == 403:
        raise AuthorizationError(
            parsed.get("message") or f"{prefix}: Forbidden",
            details=parsed.get("details"),
        )
    if status == 404:
        raise NotFoundError(
            parsed.get("message") or f"{prefix}: Not found",
            details=parsed.get("details"),
        )
    if status == 422:
        raise ValidationError(
            parsed.get("message") or f"{prefix}: Validation failed",
            details=parsed.get("details"),
        )
    if status == 429:
        retry_after = parsed.get("retry_after")
        raise RateLimitError(
            parsed.get("message") or f"{prefix}: Rate limit exceeded",
            retry_after=int(retry_after) if retry_after is not None else None,
            details=parsed.get("details"),
        )
    raise AuthoraError(
        parsed.get("message") or f"{prefix}: Request failed with status {status}",
        status_code=status,
        code=parsed.get("code"),
        details=parsed.get("details"),
    )


def _build_query_string(query: Optional[Dict[str, Any]]) -> Optional[Dict[str, str]]:
    if not query:
        return None
    return {
        _to_camel(k): str(v).lower() if isinstance(v, bool) else str(v)
        for k, v in query.items()
        if v is not None
    }


class _PermissionsCache:
    def __init__(self, ttl: float) -> None:
        self._ttl = ttl
        self._permissions: Optional[List[str]] = None
        self._deny_permissions: Optional[List[str]] = None
        self._fetched_at: float = 0.0

    @property
    def valid(self) -> bool:
        return self._permissions is not None and (time.monotonic() - self._fetched_at) < self._ttl

    def get(self) -> Tuple[List[str], List[str]]:
        return self._permissions or [], self._deny_permissions or []

    def set(self, permissions: List[str], deny_permissions: List[str]) -> None:
        self._permissions = permissions
        self._deny_permissions = deny_permissions
        self._fetched_at = time.monotonic()

    def invalidate(self) -> None:
        self._permissions = None
        self._deny_permissions = None
        self._fetched_at = 0.0


def _handle_response(response: httpx.Response, method: str, path: str) -> Any:
    body: Any = None
    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type:
        body = _keys_to_snake(response.json())
    elif response.text:
        body = response.text
    if not response.is_success:
        _raise_for_status(response.status_code, body, method, path)
    return _unwrap_response(body)


class AuthoraAgent:
    def __init__(
        self,
        agent_id: str,
        private_key: str,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        permissions_cache_ttl: float = 300.0,
        delegation_token: Optional[str] = None,
    ) -> None:
        self._agent_id = agent_id
        self._private_key = private_key
        self._base_url = (base_url or _DEFAULT_BASE_URL).rstrip("/")
        self._client = httpx.Client(
            base_url=self._base_url,
            headers={"Accept": "application/json"},
            timeout=timeout,
        )
        self._cache = _PermissionsCache(permissions_cache_ttl)
        self._delegation_token = delegation_token

    @property
    def agent_id(self) -> str:
        return self._agent_id

    def _sign_headers(self, method: str, path: str, body_str: Optional[str]) -> Dict[str, str]:
        timestamp = (
            datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.")
            + f"{datetime.now(timezone.utc).microsecond // 1000:03d}Z"
        )
        payload = build_signature_payload(method, path, timestamp, body_str)
        signature = sign(payload, self._private_key)
        return {
            "x-authora-agent-id": self._agent_id,
            "x-authora-timestamp": timestamp,
            "x-authora-signature": signature,
        }

    def signed_request(
        self,
        method: str,
        path: str,
        body: Any = None,
        query: Optional[Dict[str, Any]] = None,
    ) -> Any:
        params = _build_query_string(query)
        json_body = _keys_to_camel(body) if body is not None else None
        body_str = (
            json.dumps(json_body, separators=(",", ":"), sort_keys=True)
            if json_body is not None
            else None
        )
        headers = self._sign_headers(method.upper(), path, body_str)
        if json_body is not None:
            headers["Content-Type"] = "application/json"
        try:
            response = self._client.request(
                method.upper(),
                path,
                headers=headers,
                params=params,
                content=body_str.encode("utf-8") if body_str else None,
            )
        except httpx.TimeoutException as exc:
            raise TimeoutError(f"Request to {method} {path} timed out") from exc
        except httpx.HTTPError as exc:
            raise NetworkError(f"Request to {method} {path} failed: {exc}", details=exc) from exc
        return _handle_response(response, method.upper(), path)

    def check_permission(
        self,
        resource: str,
        action: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> PermissionCheckResult:
        body: Dict[str, Any] = {
            "agent_id": self._agent_id,
            "resource": resource,
            "action": action,
        }
        if context is not None:
            body["context"] = context
        data = self.signed_request("POST", "/permissions/check", body=body)
        return PermissionCheckResult.from_dict(data)

    def check_permissions(
        self,
        checks: List[Dict[str, str]],
    ) -> List[PermissionCheckResult]:
        body: Dict[str, Any] = {
            "agent_id": self._agent_id,
            "checks": checks,
        }
        data = self.signed_request("POST", "/permissions/check-batch", body=body)
        raw = data.get("results", []) if isinstance(data, dict) else []
        return [PermissionCheckResult.from_dict(r) for r in raw]

    def fetch_permissions(self) -> Dict[str, Any]:
        data = self.signed_request("GET", f"/agents/{self._agent_id}/permissions")
        permissions: List[str] = []
        deny_permissions: List[str] = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    resource = item.get("resource", "")
                    actions = item.get("actions", [])
                    for action in actions:
                        permissions.append(f"{resource}:{action}")
        elif isinstance(data, dict):
            permissions = data.get("permissions", [])
            deny_permissions = data.get("deny_permissions", [])
        self._cache.set(permissions, deny_permissions)
        return {"permissions": permissions, "deny_permissions": deny_permissions}

    def has_permission(self, resource: str) -> bool:
        if not self._cache.valid:
            self.fetch_permissions()
        permissions, deny_permissions = self._cache.get()
        if match_any_permission(deny_permissions, resource):
            return False
        return match_any_permission(permissions, resource)

    def invalidate_permissions_cache(self) -> None:
        self._cache.invalidate()

    def delegate(
        self,
        target_agent_id: str,
        permissions: List[str],
        constraints: Optional[Dict[str, Any]] = None,
    ) -> Delegation:
        body: Dict[str, Any] = {
            "issuer_agent_id": self._agent_id,
            "target_agent_id": target_agent_id,
            "permissions": permissions,
        }
        if constraints is not None:
            body["constraints"] = constraints
        data = self.signed_request("POST", "/delegations", body=body)
        return Delegation.from_dict(data)

    def call_tool(
        self,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None,
        method: Optional[str] = None,
        id: Optional[Any] = None,
        delegation_token: Optional[str] = None,
    ) -> McpProxyResponse:
        token = delegation_token if delegation_token is not None else self._delegation_token
        timestamp = (
            datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.")
            + f"{datetime.now(timezone.utc).microsecond // 1000:03d}Z"
        )
        mcp_payload = build_signature_payload("POST", "/mcp/proxy", timestamp, None)
        mcp_sig = sign(mcp_payload, self._private_key)
        authora_meta: Dict[str, Any] = {
            "agentId": self._agent_id,
            "signature": mcp_sig,
            "timestamp": timestamp,
        }
        if token is not None:
            authora_meta["delegationToken"] = token
        params: Dict[str, Any] = {"name": tool_name, "_authora": authora_meta}
        if arguments is not None:
            params["arguments"] = arguments
        body: Dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": id or f"{self._agent_id}-{int(time.monotonic() * 1000)}",
            "method": method or "tools/call",
            "params": params,
        }
        body_str = json.dumps(body, separators=(",", ":"), sort_keys=True)
        payload = build_signature_payload("POST", "/mcp/proxy", timestamp, body_str)
        signature = sign(payload, self._private_key)
        headers = {
            "x-authora-agent-id": self._agent_id,
            "x-authora-timestamp": timestamp,
            "x-authora-signature": signature,
            "Content-Type": "application/json",
        }
        try:
            response = self._client.request(
                "POST",
                "/mcp/proxy",
                headers=headers,
                content=body_str.encode("utf-8"),
            )
        except httpx.TimeoutException as exc:
            raise TimeoutError("Request to POST /mcp/proxy timed out") from exc
        except httpx.HTTPError as exc:
            raise NetworkError(f"Request to POST /mcp/proxy failed: {exc}", details=exc) from exc
        body_resp: Any = None
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            body_resp = _keys_to_snake(response.json())
        elif response.text:
            body_resp = response.text
        if not response.is_success:
            _raise_for_status(response.status_code, body_resp, "POST", "/mcp/proxy")
        if isinstance(body_resp, dict) and "data" in body_resp:
            body_resp = body_resp["data"]
        return McpProxyResponse.from_dict(body_resp)

    def rotate_key(self) -> Tuple[Agent, KeyPair]:
        kp = generate_key_pair()
        data = self.signed_request(
            "POST",
            f"/agents/{self._agent_id}/rotate-key",
            body={"public_key": kp.public_key},
        )
        self._private_key = kp.private_key
        return Agent.from_dict(data), kp

    def suspend(self) -> Agent:
        data = self.signed_request("POST", f"/agents/{self._agent_id}/suspend")
        return Agent.from_dict(data)

    def reactivate(self) -> Tuple[Agent, KeyPair]:
        kp = generate_key_pair()
        data = self.signed_request(
            "POST",
            f"/agents/{self._agent_id}/activate",
            body={"public_key": kp.public_key},
        )
        self._private_key = kp.private_key
        return Agent.from_dict(data), kp

    def revoke(self) -> Agent:
        data = self.signed_request("POST", f"/agents/{self._agent_id}/revoke")
        return Agent.from_dict(data)

    def get_identity_document(self) -> AgentVerification:
        data = self.signed_request("GET", f"/agents/{self._agent_id}/verify")
        return AgentVerification.from_dict(data)

    def get_profile(self) -> Agent:
        data = self.signed_request("GET", f"/agents/{self._agent_id}")
        return Agent.from_dict(data)

    def get_public_key(self) -> str:
        return get_public_key(self._private_key)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> AuthoraAgent:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


class AsyncAuthoraAgent:
    def __init__(
        self,
        agent_id: str,
        private_key: str,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        permissions_cache_ttl: float = 300.0,
        delegation_token: Optional[str] = None,
    ) -> None:
        self._agent_id = agent_id
        self._private_key = private_key
        self._base_url = (base_url or _DEFAULT_BASE_URL).rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={"Accept": "application/json"},
            timeout=timeout,
        )
        self._cache = _PermissionsCache(permissions_cache_ttl)
        self._delegation_token = delegation_token

    @property
    def agent_id(self) -> str:
        return self._agent_id

    def _sign_headers(self, method: str, path: str, body_str: Optional[str]) -> Dict[str, str]:
        timestamp = (
            datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.")
            + f"{datetime.now(timezone.utc).microsecond // 1000:03d}Z"
        )
        payload = build_signature_payload(method, path, timestamp, body_str)
        signature = sign(payload, self._private_key)
        return {
            "x-authora-agent-id": self._agent_id,
            "x-authora-timestamp": timestamp,
            "x-authora-signature": signature,
        }

    async def signed_request(
        self,
        method: str,
        path: str,
        body: Any = None,
        query: Optional[Dict[str, Any]] = None,
    ) -> Any:
        params = _build_query_string(query)
        json_body = _keys_to_camel(body) if body is not None else None
        body_str = (
            json.dumps(json_body, separators=(",", ":"), sort_keys=True)
            if json_body is not None
            else None
        )
        headers = self._sign_headers(method.upper(), path, body_str)
        if json_body is not None:
            headers["Content-Type"] = "application/json"
        try:
            response = await self._client.request(
                method.upper(),
                path,
                headers=headers,
                params=params,
                content=body_str.encode("utf-8") if body_str else None,
            )
        except httpx.TimeoutException as exc:
            raise TimeoutError(f"Request to {method} {path} timed out") from exc
        except httpx.HTTPError as exc:
            raise NetworkError(f"Request to {method} {path} failed: {exc}", details=exc) from exc
        return _handle_response(response, method.upper(), path)

    async def check_permission(
        self,
        resource: str,
        action: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> PermissionCheckResult:
        body: Dict[str, Any] = {
            "agent_id": self._agent_id,
            "resource": resource,
            "action": action,
        }
        if context is not None:
            body["context"] = context
        data = await self.signed_request("POST", "/permissions/check", body=body)
        return PermissionCheckResult.from_dict(data)

    async def check_permissions(
        self,
        checks: List[Dict[str, str]],
    ) -> List[PermissionCheckResult]:
        body: Dict[str, Any] = {
            "agent_id": self._agent_id,
            "checks": checks,
        }
        data = await self.signed_request("POST", "/permissions/check-batch", body=body)
        raw = data.get("results", []) if isinstance(data, dict) else []
        return [PermissionCheckResult.from_dict(r) for r in raw]

    async def fetch_permissions(self) -> Dict[str, Any]:
        data = await self.signed_request("GET", f"/agents/{self._agent_id}/permissions")
        permissions: List[str] = []
        deny_permissions: List[str] = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    resource = item.get("resource", "")
                    actions = item.get("actions", [])
                    for action in actions:
                        permissions.append(f"{resource}:{action}")
        elif isinstance(data, dict):
            permissions = data.get("permissions", [])
            deny_permissions = data.get("deny_permissions", [])
        self._cache.set(permissions, deny_permissions)
        return {"permissions": permissions, "deny_permissions": deny_permissions}

    async def has_permission(self, resource: str) -> bool:
        if not self._cache.valid:
            await self.fetch_permissions()
        permissions, deny_permissions = self._cache.get()
        if match_any_permission(deny_permissions, resource):
            return False
        return match_any_permission(permissions, resource)

    def invalidate_permissions_cache(self) -> None:
        self._cache.invalidate()

    async def delegate(
        self,
        target_agent_id: str,
        permissions: List[str],
        constraints: Optional[Dict[str, Any]] = None,
    ) -> Delegation:
        body: Dict[str, Any] = {
            "issuer_agent_id": self._agent_id,
            "target_agent_id": target_agent_id,
            "permissions": permissions,
        }
        if constraints is not None:
            body["constraints"] = constraints
        data = await self.signed_request("POST", "/delegations", body=body)
        return Delegation.from_dict(data)

    async def call_tool(
        self,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None,
        method: Optional[str] = None,
        id: Optional[Any] = None,
        delegation_token: Optional[str] = None,
    ) -> McpProxyResponse:
        token = delegation_token if delegation_token is not None else self._delegation_token
        timestamp = (
            datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.")
            + f"{datetime.now(timezone.utc).microsecond // 1000:03d}Z"
        )
        mcp_payload = build_signature_payload("POST", "/mcp/proxy", timestamp, None)
        mcp_sig = sign(mcp_payload, self._private_key)
        authora_meta: Dict[str, Any] = {
            "agentId": self._agent_id,
            "signature": mcp_sig,
            "timestamp": timestamp,
        }
        if token is not None:
            authora_meta["delegationToken"] = token
        params: Dict[str, Any] = {"name": tool_name, "_authora": authora_meta}
        if arguments is not None:
            params["arguments"] = arguments
        body: Dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": id or f"{self._agent_id}-{int(time.monotonic() * 1000)}",
            "method": method or "tools/call",
            "params": params,
        }
        body_str = json.dumps(body, separators=(",", ":"), sort_keys=True)
        payload = build_signature_payload("POST", "/mcp/proxy", timestamp, body_str)
        signature = sign(payload, self._private_key)
        headers = {
            "x-authora-agent-id": self._agent_id,
            "x-authora-timestamp": timestamp,
            "x-authora-signature": signature,
            "Content-Type": "application/json",
        }
        try:
            response = await self._client.request(
                "POST",
                "/mcp/proxy",
                headers=headers,
                content=body_str.encode("utf-8"),
            )
        except httpx.TimeoutException as exc:
            raise TimeoutError("Request to POST /mcp/proxy timed out") from exc
        except httpx.HTTPError as exc:
            raise NetworkError(f"Request to POST /mcp/proxy failed: {exc}", details=exc) from exc
        body_resp: Any = None
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            body_resp = _keys_to_snake(response.json())
        elif response.text:
            body_resp = response.text
        if not response.is_success:
            _raise_for_status(response.status_code, body_resp, "POST", "/mcp/proxy")
        if isinstance(body_resp, dict) and "data" in body_resp:
            body_resp = body_resp["data"]
        return McpProxyResponse.from_dict(body_resp)

    async def rotate_key(self) -> Tuple[Agent, KeyPair]:
        kp = generate_key_pair()
        data = await self.signed_request(
            "POST",
            f"/agents/{self._agent_id}/rotate-key",
            body={"public_key": kp.public_key},
        )
        self._private_key = kp.private_key
        return Agent.from_dict(data), kp

    async def suspend(self) -> Agent:
        data = await self.signed_request("POST", f"/agents/{self._agent_id}/suspend")
        return Agent.from_dict(data)

    async def reactivate(self) -> Tuple[Agent, KeyPair]:
        kp = generate_key_pair()
        data = await self.signed_request(
            "POST",
            f"/agents/{self._agent_id}/activate",
            body={"public_key": kp.public_key},
        )
        self._private_key = kp.private_key
        return Agent.from_dict(data), kp

    async def revoke(self) -> Agent:
        data = await self.signed_request("POST", f"/agents/{self._agent_id}/revoke")
        return Agent.from_dict(data)

    async def get_identity_document(self) -> AgentVerification:
        data = await self.signed_request("GET", f"/agents/{self._agent_id}/verify")
        return AgentVerification.from_dict(data)

    async def get_profile(self) -> Agent:
        data = await self.signed_request("GET", f"/agents/{self._agent_id}")
        return Agent.from_dict(data)

    def get_public_key(self) -> str:
        return get_public_key(self._private_key)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def close(self) -> None:
        await self.aclose()

    async def __aenter__(self) -> AsyncAuthoraAgent:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()

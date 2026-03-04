"""Low-level HTTP transport for the Authora SDK.

Provides both synchronous and asynchronous HTTP clients built on ``httpx``.
Handles authentication headers, query-string construction, camelCase
conversion, and maps HTTP error responses to typed SDK exceptions.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Optional, Union

import httpx

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

# ---------------------------------------------------------------------------
# Key-case conversion utilities
# ---------------------------------------------------------------------------

_CAMEL_RE = re.compile(r"(?<=[a-z0-9])([A-Z])")
_SNAKE_RE = re.compile(r"_([a-z])")


def _to_camel(name: str) -> str:
    """Convert a snake_case name to camelCase."""
    return _SNAKE_RE.sub(lambda m: m.group(1).upper(), name)


def _to_snake(name: str) -> str:
    """Convert a camelCase name to snake_case."""
    return _CAMEL_RE.sub(r"_\1", name).lower()


def _keys_to_camel(obj: Any) -> Any:
    """Recursively convert all dict keys from snake_case to camelCase."""
    if isinstance(obj, dict):
        return {_to_camel(k): _keys_to_camel(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_keys_to_camel(i) for i in obj]
    return obj


def _keys_to_snake(obj: Any) -> Any:
    """Recursively convert all dict keys from camelCase to snake_case."""
    if isinstance(obj, dict):
        return {_to_snake(k): _keys_to_snake(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_keys_to_snake(i) for i in obj]
    return obj


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

QueryValue = Union[str, int, bool, None]


def _build_params(
    query: Optional[Dict[str, QueryValue]],
) -> Optional[Dict[str, str]]:
    """Build httpx-compatible query parameters, dropping ``None`` values."""
    if not query:
        return None
    return {
        _to_camel(k): str(v).lower() if isinstance(v, bool) else str(v)
        for k, v in query.items()
        if v is not None
    }


def _parse_error_body(body: Any) -> Dict[str, Any]:
    """Extract structured error info from a response body."""
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


def _unwrap_response(body: Any) -> Any:
    """Unwrap the standard backend response envelope.

    The Authora API returns responses in one of these shapes:
    - ``{ "data": T }`` for single entities
    - ``{ "data": [...], "pagination": { "total", "page", "limit" } }`` for lists
    - ``{ "data": [...], "meta": { "total", "page", "limit" } }`` for some lists

    For paginated lists this returns ``{ "items": [...], "total": N, ... }``.
    For single entities this returns the unwrapped ``T``.
    """
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


def _raise_for_status(status: int, body: Any, method: str, path: str) -> None:
    """Map an HTTP error status to the appropriate SDK exception."""
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


# ---------------------------------------------------------------------------
# Synchronous HTTP client
# ---------------------------------------------------------------------------


class SyncHttpClient:
    """Synchronous HTTP transport built on ``httpx.Client``.

    Args:
        base_url: API base URL (trailing slashes are stripped).
        api_key: Bearer token for authentication.
        timeout: Request timeout in seconds.
        headers: Additional default headers.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        # Do NOT set Content-Type as a default header. Sending
        # Content-Type: application/json with an empty body causes Fastify
        # to reject the request (FST_ERR_CTP_EMPTY_JSON_BODY).
        # Content-Type is set per-request only when a body is present.
        default_headers = {
            "Accept": "application/json",
        }
        if headers:
            default_headers.update(headers)
        self._client = httpx.Client(
            base_url=self._base_url,
            headers=default_headers,
            timeout=timeout,
        )

    # -- convenience methods ------------------------------------------------

    def get(
        self,
        path: str,
        *,
        query: Optional[Dict[str, QueryValue]] = None,
        auth: bool = True,
    ) -> Any:
        """Send a GET request and return the parsed JSON response."""
        return self._request("GET", path, query=query, auth=auth)

    def post(
        self,
        path: str,
        *,
        body: Any = None,
        query: Optional[Dict[str, QueryValue]] = None,
        auth: bool = True,
    ) -> Any:
        """Send a POST request and return the parsed JSON response."""
        return self._request("POST", path, body=body, query=query, auth=auth)

    def patch(
        self,
        path: str,
        *,
        body: Any = None,
        query: Optional[Dict[str, QueryValue]] = None,
        auth: bool = True,
    ) -> Any:
        """Send a PATCH request and return the parsed JSON response."""
        return self._request("PATCH", path, body=body, query=query, auth=auth)

    def delete(
        self,
        path: str,
        *,
        query: Optional[Dict[str, QueryValue]] = None,
        auth: bool = True,
    ) -> Any:
        """Send a DELETE request and return the parsed JSON response."""
        return self._request("DELETE", path, query=query, auth=auth)

    def close(self) -> None:
        """Close the underlying httpx client."""
        self._client.close()

    # -- internal -----------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        *,
        body: Any = None,
        query: Optional[Dict[str, QueryValue]] = None,
        auth: bool = True,
    ) -> Any:
        headers: Dict[str, str] = {}
        if auth:
            headers["Authorization"] = f"Bearer {self._api_key}"

        params = _build_params(query)
        json_body = _keys_to_camel(body) if body is not None else None

        # Only set Content-Type when sending a JSON body
        if json_body is not None:
            headers["Content-Type"] = "application/json"

        try:
            response = self._client.request(
                method,
                path,
                headers=headers,
                params=params,
                json=json_body,
            )
        except httpx.TimeoutException as exc:
            raise TimeoutError(f"Request to {method} {path} timed out") from exc
        except httpx.HTTPError as exc:
            raise NetworkError(
                f"Request to {method} {path} failed: {exc}",
                details=exc,
            ) from exc

        return self._handle_response(response, method, path)

    @staticmethod
    def _handle_response(response: httpx.Response, method: str, path: str) -> Any:
        body: Any = None
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            body = _keys_to_snake(response.json())
        elif response.text:
            body = response.text

        if not response.is_success:
            _raise_for_status(response.status_code, body, method, path)

        # Unwrap the standard backend response envelope.
        # The Authora API returns { data: T } or { data: T[], pagination/meta: {...} }.
        return _unwrap_response(body)


# ---------------------------------------------------------------------------
# Asynchronous HTTP client
# ---------------------------------------------------------------------------


class AsyncHttpClient:
    """Asynchronous HTTP transport built on ``httpx.AsyncClient``.

    Args:
        base_url: API base URL (trailing slashes are stripped).
        api_key: Bearer token for authentication.
        timeout: Request timeout in seconds.
        headers: Additional default headers.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        default_headers = {
            "Accept": "application/json",
        }
        if headers:
            default_headers.update(headers)
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers=default_headers,
            timeout=timeout,
        )

    # -- convenience methods ------------------------------------------------

    async def get(
        self,
        path: str,
        *,
        query: Optional[Dict[str, QueryValue]] = None,
        auth: bool = True,
    ) -> Any:
        """Send a GET request and return the parsed JSON response."""
        return await self._request("GET", path, query=query, auth=auth)

    async def post(
        self,
        path: str,
        *,
        body: Any = None,
        query: Optional[Dict[str, QueryValue]] = None,
        auth: bool = True,
    ) -> Any:
        """Send a POST request and return the parsed JSON response."""
        return await self._request("POST", path, body=body, query=query, auth=auth)

    async def patch(
        self,
        path: str,
        *,
        body: Any = None,
        query: Optional[Dict[str, QueryValue]] = None,
        auth: bool = True,
    ) -> Any:
        """Send a PATCH request and return the parsed JSON response."""
        return await self._request("PATCH", path, body=body, query=query, auth=auth)

    async def delete(
        self,
        path: str,
        *,
        query: Optional[Dict[str, QueryValue]] = None,
        auth: bool = True,
    ) -> Any:
        """Send a DELETE request and return the parsed JSON response."""
        return await self._request("DELETE", path, query=query, auth=auth)

    async def close(self) -> None:
        """Close the underlying httpx async client."""
        await self._client.aclose()

    # -- internal -----------------------------------------------------------

    async def _request(
        self,
        method: str,
        path: str,
        *,
        body: Any = None,
        query: Optional[Dict[str, QueryValue]] = None,
        auth: bool = True,
    ) -> Any:
        headers: Dict[str, str] = {}
        if auth:
            headers["Authorization"] = f"Bearer {self._api_key}"

        params = _build_params(query)
        json_body = _keys_to_camel(body) if body is not None else None

        # Only set Content-Type when sending a JSON body
        if json_body is not None:
            headers["Content-Type"] = "application/json"

        try:
            response = await self._client.request(
                method,
                path,
                headers=headers,
                params=params,
                json=json_body,
            )
        except httpx.TimeoutException as exc:
            raise TimeoutError(f"Request to {method} {path} timed out") from exc
        except httpx.HTTPError as exc:
            raise NetworkError(
                f"Request to {method} {path} failed: {exc}",
                details=exc,
            ) from exc

        return self._handle_response(response, method, path)

    @staticmethod
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

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._http import AsyncHttpClient, SyncHttpClient
from ..types import (
    BatchPermissionCheckResult,
    EffectivePermission,
    PermissionCheckResult,
)


class PermissionsResource:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def check(
        self,
        *,
        agent_id: str,
        resource: str,
        action: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> PermissionCheckResult:
        body: Dict[str, Any] = {
            "agent_id": agent_id,
            "resource": resource,
            "action": action,
        }
        if context is not None:
            body["context"] = context

        data = self._http.post("/permissions/check", body=body)
        return PermissionCheckResult.from_dict(data)

    def check_batch(
        self,
        *,
        agent_id: str,
        checks: List[Dict[str, str]],
    ) -> BatchPermissionCheckResult:
        body: Dict[str, Any] = {
            "agent_id": agent_id,
            "checks": checks,
        }
        data = self._http.post("/permissions/check-batch", body=body)
        return BatchPermissionCheckResult.from_dict(data)

    def get_effective(self, agent_id: str) -> List[EffectivePermission]:
        data = self._http.get(f"/agents/{agent_id}/permissions")
        return [EffectivePermission.from_dict(item) for item in data]


class AsyncPermissionsResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def check(
        self,
        *,
        agent_id: str,
        resource: str,
        action: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> PermissionCheckResult:
        body: Dict[str, Any] = {
            "agent_id": agent_id,
            "resource": resource,
            "action": action,
        }
        if context is not None:
            body["context"] = context

        data = await self._http.post("/permissions/check", body=body)
        return PermissionCheckResult.from_dict(data)

    async def check_batch(
        self,
        *,
        agent_id: str,
        checks: List[Dict[str, str]],
    ) -> BatchPermissionCheckResult:
        body: Dict[str, Any] = {
            "agent_id": agent_id,
            "checks": checks,
        }
        data = await self._http.post("/permissions/check-batch", body=body)
        return BatchPermissionCheckResult.from_dict(data)

    async def get_effective(self, agent_id: str) -> List[EffectivePermission]:
        data = await self._http.get(f"/agents/{agent_id}/permissions")
        return [EffectivePermission.from_dict(item) for item in data]

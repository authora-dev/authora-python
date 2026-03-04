from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._http import AsyncHttpClient, SyncHttpClient
from ..types import ApiKey, PaginatedList


class ApiKeysResource:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(
        self,
        *,
        organization_id: str,
        name: str,
        created_by: str,
        scopes: Optional[List[str]] = None,
        expires_in_days: Optional[int] = None,
    ) -> ApiKey:
        body: Dict[str, Any] = {
            "organization_id": organization_id,
            "name": name,
            "created_by": created_by,
        }
        if scopes is not None:
            body["scopes"] = scopes
        if expires_in_days is not None:
            body["expires_in_days"] = expires_in_days
        data = self._http.post("/api-keys", body=body)
        return ApiKey.from_dict(data)

    def list(self, *, organization_id: str) -> PaginatedList[ApiKey]:
        query: Dict[str, Any] = {"organization_id": organization_id}
        data = self._http.get("/api-keys", query=query)
        return PaginatedList.from_dict(data, ApiKey)

    def revoke(self, key_id: str) -> None:
        self._http.delete(f"/api-keys/{key_id}")


class AsyncApiKeysResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(
        self,
        *,
        organization_id: str,
        name: str,
        created_by: str,
        scopes: Optional[List[str]] = None,
        expires_in_days: Optional[int] = None,
    ) -> ApiKey:
        body: Dict[str, Any] = {
            "organization_id": organization_id,
            "name": name,
            "created_by": created_by,
        }
        if scopes is not None:
            body["scopes"] = scopes
        if expires_in_days is not None:
            body["expires_in_days"] = expires_in_days
        data = await self._http.post("/api-keys", body=body)
        return ApiKey.from_dict(data)

    async def list(self, *, organization_id: str) -> PaginatedList[ApiKey]:
        query: Dict[str, Any] = {"organization_id": organization_id}
        data = await self._http.get("/api-keys", query=query)
        return PaginatedList.from_dict(data, ApiKey)

    async def revoke(self, key_id: str) -> None:
        await self._http.delete(f"/api-keys/{key_id}")

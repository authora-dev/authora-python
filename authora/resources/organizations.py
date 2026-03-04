from __future__ import annotations

from typing import Any, Dict, Optional

from .._http import AsyncHttpClient, SyncHttpClient
from ..types import Organization, PaginatedList


class OrganizationsResource:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(self, *, name: str, slug: str) -> Organization:
        body: Dict[str, Any] = {
            "name": name,
            "slug": slug,
        }
        data = self._http.post("/organizations", body=body)
        return Organization.from_dict(data)

    def get(self, org_id: str) -> Organization:
        data = self._http.get(f"/organizations/{org_id}")
        return Organization.from_dict(data)

    def list(
        self,
        *,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> PaginatedList[Organization]:
        query: Dict[str, Any] = {}
        if page is not None:
            query["page"] = page
        if limit is not None:
            query["limit"] = limit
        data = self._http.get("/organizations", query=query)
        return PaginatedList.from_dict(data, Organization)


class AsyncOrganizationsResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(self, *, name: str, slug: str) -> Organization:
        body: Dict[str, Any] = {
            "name": name,
            "slug": slug,
        }
        data = await self._http.post("/organizations", body=body)
        return Organization.from_dict(data)

    async def get(self, org_id: str) -> Organization:
        data = await self._http.get(f"/organizations/{org_id}")
        return Organization.from_dict(data)

    async def list(
        self,
        *,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> PaginatedList[Organization]:
        query: Dict[str, Any] = {}
        if page is not None:
            query["page"] = page
        if limit is not None:
            query["limit"] = limit
        data = await self._http.get("/organizations", query=query)
        return PaginatedList.from_dict(data, Organization)

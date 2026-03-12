from __future__ import annotations

from typing import Any, Dict, Optional

from .._http import AsyncHttpClient, SyncHttpClient
from ..types import PaginatedList, Workspace, WorkspaceStats


class WorkspacesResource:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(
        self,
        *,
        organization_id: str,
        name: str,
        slug: str,
    ) -> Workspace:
        body: Dict[str, Any] = {
            "organization_id": organization_id,
            "name": name,
            "slug": slug,
        }
        data = self._http.post("/workspaces", body=body)
        return Workspace.from_dict(data)

    def get(self, workspace_id: str) -> Workspace:
        data = self._http.get(f"/workspaces/{workspace_id}")
        return Workspace.from_dict(data)

    def list(
        self,
        *,
        organization_id: str,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> PaginatedList[Workspace]:
        query: Dict[str, Any] = {"organization_id": organization_id}
        if page is not None:
            query["page"] = page
        if limit is not None:
            query["limit"] = limit
        data = self._http.get("/workspaces", query=query)
        return PaginatedList.from_dict(data, Workspace)

    def get_stats(self, workspace_id: str) -> WorkspaceStats:
        data = self._http.get(f"/workspaces/{workspace_id}/stats")
        return WorkspaceStats.from_dict(data)

    def update(
        self,
        workspace_id: str,
        *,
        name: Optional[str] = None,
        slug: Optional[str] = None,
    ) -> Workspace:
        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if slug is not None:
            body["slug"] = slug
        data = self._http.patch(f"/workspaces/{workspace_id}", body=body)
        return Workspace.from_dict(data)

    def delete(self, workspace_id: str) -> Workspace:
        data = self._http.delete(f"/workspaces/{workspace_id}")
        return Workspace.from_dict(data)

    def restore(self, workspace_id: str) -> Workspace:
        data = self._http.post(f"/workspaces/{workspace_id}/restore")
        return Workspace.from_dict(data)


class AsyncWorkspacesResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(
        self,
        *,
        organization_id: str,
        name: str,
        slug: str,
    ) -> Workspace:
        body: Dict[str, Any] = {
            "organization_id": organization_id,
            "name": name,
            "slug": slug,
        }
        data = await self._http.post("/workspaces", body=body)
        return Workspace.from_dict(data)

    async def get(self, workspace_id: str) -> Workspace:
        data = await self._http.get(f"/workspaces/{workspace_id}")
        return Workspace.from_dict(data)

    async def list(
        self,
        *,
        organization_id: str,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> PaginatedList[Workspace]:
        query: Dict[str, Any] = {"organization_id": organization_id}
        if page is not None:
            query["page"] = page
        if limit is not None:
            query["limit"] = limit
        data = await self._http.get("/workspaces", query=query)
        return PaginatedList.from_dict(data, Workspace)

    async def get_stats(self, workspace_id: str) -> WorkspaceStats:
        data = await self._http.get(f"/workspaces/{workspace_id}/stats")
        return WorkspaceStats.from_dict(data)

    async def update(
        self,
        workspace_id: str,
        *,
        name: Optional[str] = None,
        slug: Optional[str] = None,
    ) -> Workspace:
        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if slug is not None:
            body["slug"] = slug
        data = await self._http.patch(f"/workspaces/{workspace_id}", body=body)
        return Workspace.from_dict(data)

    async def delete(self, workspace_id: str) -> Workspace:
        data = await self._http.delete(f"/workspaces/{workspace_id}")
        return Workspace.from_dict(data)

    async def restore(self, workspace_id: str) -> Workspace:
        data = await self._http.post(f"/workspaces/{workspace_id}/restore")
        return Workspace.from_dict(data)

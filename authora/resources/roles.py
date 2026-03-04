from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._http import AsyncHttpClient, SyncHttpClient
from ..types import AgentRoleAssignment, PaginatedList, Role


class RolesResource:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(
        self,
        *,
        workspace_id: str,
        name: str,
        permissions: List[str],
        description: Optional[str] = None,
        deny_permissions: Optional[List[str]] = None,
        stage: Optional[str] = None,
        max_session_duration: Optional[int] = None,
    ) -> Role:
        body: Dict[str, Any] = {
            "workspace_id": workspace_id,
            "name": name,
            "permissions": permissions,
        }
        if description is not None:
            body["description"] = description
        if deny_permissions is not None:
            body["deny_permissions"] = deny_permissions
        if stage is not None:
            body["stage"] = stage
        if max_session_duration is not None:
            body["max_session_duration"] = max_session_duration

        data = self._http.post("/roles", body=body)
        return Role.from_dict(data)

    def list(
        self,
        *,
        workspace_id: str,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> PaginatedList[Role]:
        query: Dict[str, Any] = {"workspace_id": workspace_id}
        if page is not None:
            query["page"] = page
        if limit is not None:
            query["limit"] = limit

        data = self._http.get("/roles", query=query)
        return PaginatedList.from_dict(data, Role)

    def get(self, role_id: str) -> Role:
        data = self._http.get(f"/roles/{role_id}")
        return Role.from_dict(data)

    def update(
        self,
        role_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        deny_permissions: Optional[List[str]] = None,
        stage: Optional[str] = None,
        max_session_duration: Optional[int] = None,
    ) -> Role:
        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if permissions is not None:
            body["permissions"] = permissions
        if deny_permissions is not None:
            body["deny_permissions"] = deny_permissions
        if stage is not None:
            body["stage"] = stage
        if max_session_duration is not None:
            body["max_session_duration"] = max_session_duration

        data = self._http.patch(f"/roles/{role_id}", body=body)
        return Role.from_dict(data)

    def delete(self, role_id: str) -> None:
        self._http.delete(f"/roles/{role_id}")

    def assign(
        self,
        agent_id: str,
        *,
        role_id: str,
        granted_by: Optional[str] = None,
        expires_at: Optional[str] = None,
    ) -> AgentRoleAssignment:
        body: Dict[str, Any] = {"role_id": role_id}
        if granted_by is not None:
            body["granted_by"] = granted_by
        if expires_at is not None:
            body["expires_at"] = expires_at

        data = self._http.post(f"/agents/{agent_id}/roles", body=body)
        return AgentRoleAssignment.from_dict(data)

    def unassign(self, agent_id: str, role_id: str) -> None:
        self._http.delete(f"/agents/{agent_id}/roles/{role_id}")

    def list_agent_roles(self, agent_id: str) -> List[AgentRoleAssignment]:
        data = self._http.get(f"/agents/{agent_id}/roles")
        return [AgentRoleAssignment.from_dict(item) for item in data]


class AsyncRolesResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(
        self,
        *,
        workspace_id: str,
        name: str,
        permissions: List[str],
        description: Optional[str] = None,
        deny_permissions: Optional[List[str]] = None,
        stage: Optional[str] = None,
        max_session_duration: Optional[int] = None,
    ) -> Role:
        body: Dict[str, Any] = {
            "workspace_id": workspace_id,
            "name": name,
            "permissions": permissions,
        }
        if description is not None:
            body["description"] = description
        if deny_permissions is not None:
            body["deny_permissions"] = deny_permissions
        if stage is not None:
            body["stage"] = stage
        if max_session_duration is not None:
            body["max_session_duration"] = max_session_duration

        data = await self._http.post("/roles", body=body)
        return Role.from_dict(data)

    async def list(
        self,
        *,
        workspace_id: str,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> PaginatedList[Role]:
        query: Dict[str, Any] = {"workspace_id": workspace_id}
        if page is not None:
            query["page"] = page
        if limit is not None:
            query["limit"] = limit

        data = await self._http.get("/roles", query=query)
        return PaginatedList.from_dict(data, Role)

    async def get(self, role_id: str) -> Role:
        data = await self._http.get(f"/roles/{role_id}")
        return Role.from_dict(data)

    async def update(
        self,
        role_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        deny_permissions: Optional[List[str]] = None,
        stage: Optional[str] = None,
        max_session_duration: Optional[int] = None,
    ) -> Role:
        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if permissions is not None:
            body["permissions"] = permissions
        if deny_permissions is not None:
            body["deny_permissions"] = deny_permissions
        if stage is not None:
            body["stage"] = stage
        if max_session_duration is not None:
            body["max_session_duration"] = max_session_duration

        data = await self._http.patch(f"/roles/{role_id}", body=body)
        return Role.from_dict(data)

    async def delete(self, role_id: str) -> None:
        await self._http.delete(f"/roles/{role_id}")

    async def assign(
        self,
        agent_id: str,
        *,
        role_id: str,
        granted_by: Optional[str] = None,
        expires_at: Optional[str] = None,
    ) -> AgentRoleAssignment:
        body: Dict[str, Any] = {"role_id": role_id}
        if granted_by is not None:
            body["granted_by"] = granted_by
        if expires_at is not None:
            body["expires_at"] = expires_at

        data = await self._http.post(f"/agents/{agent_id}/roles", body=body)
        return AgentRoleAssignment.from_dict(data)

    async def unassign(self, agent_id: str, role_id: str) -> None:
        await self._http.delete(f"/agents/{agent_id}/roles/{role_id}")

    async def list_agent_roles(self, agent_id: str) -> List[AgentRoleAssignment]:
        data = await self._http.get(f"/agents/{agent_id}/roles")
        return [AgentRoleAssignment.from_dict(item) for item in data]

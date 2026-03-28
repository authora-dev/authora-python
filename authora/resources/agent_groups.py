from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._http import AsyncHttpClient, SyncHttpClient
from ..types import AgentGroup, AgentGroupMember, BulkAssignRoleResult, PaginatedList


class AgentGroupsResource:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(
        self,
        *,
        workspace_id: str,
        name: str,
        description: Optional[str] = None,
    ) -> AgentGroup:
        body: Dict[str, Any] = {
            "workspace_id": workspace_id,
            "name": name,
        }
        if description is not None:
            body["description"] = description

        data = self._http.post("/agent-groups", body=body)
        return AgentGroup.from_dict(data)

    def list(self, *, workspace_id: str) -> PaginatedList[AgentGroup]:
        query: Dict[str, Any] = {"workspace_id": workspace_id}
        data = self._http.get("/agent-groups", query=query)
        return PaginatedList.from_dict(data, AgentGroup)

    def get(self, group_id: str) -> AgentGroup:
        data = self._http.get(f"/agent-groups/{group_id}")
        return AgentGroup.from_dict(data)

    def update(
        self,
        group_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> AgentGroup:
        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        data = self._http.patch(f"/agent-groups/{group_id}", body=body)
        return AgentGroup.from_dict(data)

    def delete(self, group_id: str) -> None:
        self._http.delete(f"/agent-groups/{group_id}")

    def add_members(self, group_id: str, agent_ids: List[str]) -> None:
        self._http.post(f"/agent-groups/{group_id}/members", body={"agent_ids": agent_ids})

    def remove_members(self, group_id: str, agent_ids: List[str]) -> None:
        self._http.delete(f"/agent-groups/{group_id}/members", body={"agent_ids": agent_ids})

    def list_members(self, group_id: str) -> List[AgentGroupMember]:
        data = self._http.get(f"/agent-groups/{group_id}/members")
        if isinstance(data, list):
            return [AgentGroupMember.from_dict(item) for item in data]
        items = data.get("items", data.get("data", []))
        return [AgentGroupMember.from_dict(item) for item in items]

    def list_agent_groups(self, agent_id: str) -> List[AgentGroup]:
        data = self._http.get(f"/agents/{agent_id}/groups")
        if isinstance(data, list):
            return [AgentGroup.from_dict(item) for item in data]
        items = data.get("items", data.get("data", []))
        return [AgentGroup.from_dict(item) for item in items]

    def bulk_assign_role(
        self,
        *,
        role_id: str,
        agent_ids: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> BulkAssignRoleResult:
        body: Dict[str, Any] = {"role_id": role_id}
        if agent_ids is not None:
            body["agent_ids"] = agent_ids
        if tags is not None:
            body["tags"] = tags
        data = self._http.post("/agents/bulk/assign-role", body=body)
        return BulkAssignRoleResult.from_dict(data)


class AsyncAgentGroupsResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(
        self,
        *,
        workspace_id: str,
        name: str,
        description: Optional[str] = None,
    ) -> AgentGroup:
        body: Dict[str, Any] = {
            "workspace_id": workspace_id,
            "name": name,
        }
        if description is not None:
            body["description"] = description

        data = await self._http.post("/agent-groups", body=body)
        return AgentGroup.from_dict(data)

    async def list(self, *, workspace_id: str) -> PaginatedList[AgentGroup]:
        query: Dict[str, Any] = {"workspace_id": workspace_id}
        data = await self._http.get("/agent-groups", query=query)
        return PaginatedList.from_dict(data, AgentGroup)

    async def get(self, group_id: str) -> AgentGroup:
        data = await self._http.get(f"/agent-groups/{group_id}")
        return AgentGroup.from_dict(data)

    async def update(
        self,
        group_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> AgentGroup:
        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        data = await self._http.patch(f"/agent-groups/{group_id}", body=body)
        return AgentGroup.from_dict(data)

    async def delete(self, group_id: str) -> None:
        await self._http.delete(f"/agent-groups/{group_id}")

    async def add_members(self, group_id: str, agent_ids: List[str]) -> None:
        await self._http.post(
            f"/agent-groups/{group_id}/members", body={"agent_ids": agent_ids}
        )

    async def remove_members(self, group_id: str, agent_ids: List[str]) -> None:
        await self._http.delete(
            f"/agent-groups/{group_id}/members", body={"agent_ids": agent_ids}
        )

    async def list_members(self, group_id: str) -> List[AgentGroupMember]:
        data = await self._http.get(f"/agent-groups/{group_id}/members")
        if isinstance(data, list):
            return [AgentGroupMember.from_dict(item) for item in data]
        items = data.get("items", data.get("data", []))
        return [AgentGroupMember.from_dict(item) for item in items]

    async def list_agent_groups(self, agent_id: str) -> List[AgentGroup]:
        data = await self._http.get(f"/agents/{agent_id}/groups")
        if isinstance(data, list):
            return [AgentGroup.from_dict(item) for item in data]
        items = data.get("items", data.get("data", []))
        return [AgentGroup.from_dict(item) for item in items]

    async def bulk_assign_role(
        self,
        *,
        role_id: str,
        agent_ids: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> BulkAssignRoleResult:
        body: Dict[str, Any] = {"role_id": role_id}
        if agent_ids is not None:
            body["agent_ids"] = agent_ids
        if tags is not None:
            body["tags"] = tags
        data = await self._http.post("/agents/bulk/assign-role", body=body)
        return BulkAssignRoleResult.from_dict(data)

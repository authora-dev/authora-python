from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._http import AsyncHttpClient, SyncHttpClient
from ..types import Agent, AgentVerification, PaginatedList


class AgentsResource:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(
        self,
        *,
        workspace_id: str,
        name: str,
        created_by: str,
        description: Optional[str] = None,
        expires_in: Optional[int] = None,
        tags: Optional[List[str]] = None,
        framework: Optional[str] = None,
        model_provider: Optional[str] = None,
        model_id: Optional[str] = None,
    ) -> Agent:
        body: Dict[str, Any] = {
            "workspace_id": workspace_id,
            "name": name,
            "created_by": created_by,
        }
        if description is not None:
            body["description"] = description
        if expires_in is not None:
            body["expires_in"] = expires_in
        if tags is not None:
            body["tags"] = tags
        if framework is not None:
            body["framework"] = framework
        if model_provider is not None:
            body["model_provider"] = model_provider
        if model_id is not None:
            body["model_id"] = model_id

        data = self._http.post("/agents", body=body)
        return Agent.from_dict(data)

    def list(
        self,
        *,
        workspace_id: str,
        status: Optional[str] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> PaginatedList[Agent]:
        query: Dict[str, Any] = {"workspace_id": workspace_id}
        if status is not None:
            query["status"] = status
        if page is not None:
            query["page"] = page
        if limit is not None:
            query["limit"] = limit

        data = self._http.get("/agents", query=query)
        return PaginatedList.from_dict(data, Agent)

    def get(self, agent_id: str) -> Agent:
        data = self._http.get(f"/agents/{agent_id}")
        return Agent.from_dict(data)

    def verify(self, agent_id: str) -> AgentVerification:
        data = self._http.get(f"/agents/{agent_id}/verify", auth=False)
        return AgentVerification.from_dict(data)

    def activate(self, agent_id: str, *, public_key: str) -> Agent:
        data = self._http.post(f"/agents/{agent_id}/activate", body={"public_key": public_key})
        return Agent.from_dict(data)

    def suspend(self, agent_id: str) -> Agent:
        data = self._http.post(f"/agents/{agent_id}/suspend")
        return Agent.from_dict(data)

    def revoke(self, agent_id: str) -> Agent:
        data = self._http.post(f"/agents/{agent_id}/revoke")
        return Agent.from_dict(data)

    def rotate_key(self, agent_id: str, *, public_key: str) -> Agent:
        data = self._http.post(f"/agents/{agent_id}/rotate-key", body={"public_key": public_key})
        return Agent.from_dict(data)

    def update(
        self,
        agent_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        framework: Optional[str] = None,
        model_provider: Optional[str] = None,
        model_id: Optional[str] = None,
    ) -> Agent:
        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if tags is not None:
            body["tags"] = tags
        if framework is not None:
            body["framework"] = framework
        if model_provider is not None:
            body["model_provider"] = model_provider
        if model_id is not None:
            body["model_id"] = model_id
        data = self._http.patch(f"/agents/{agent_id}", body=body)
        return Agent.from_dict(data)


class AsyncAgentsResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(
        self,
        *,
        workspace_id: str,
        name: str,
        created_by: str,
        description: Optional[str] = None,
        expires_in: Optional[int] = None,
        tags: Optional[List[str]] = None,
        framework: Optional[str] = None,
        model_provider: Optional[str] = None,
        model_id: Optional[str] = None,
    ) -> Agent:
        body: Dict[str, Any] = {
            "workspace_id": workspace_id,
            "name": name,
            "created_by": created_by,
        }
        if description is not None:
            body["description"] = description
        if expires_in is not None:
            body["expires_in"] = expires_in
        if tags is not None:
            body["tags"] = tags
        if framework is not None:
            body["framework"] = framework
        if model_provider is not None:
            body["model_provider"] = model_provider
        if model_id is not None:
            body["model_id"] = model_id

        data = await self._http.post("/agents", body=body)
        return Agent.from_dict(data)

    async def list(
        self,
        *,
        workspace_id: str,
        status: Optional[str] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> PaginatedList[Agent]:
        query: Dict[str, Any] = {"workspace_id": workspace_id}
        if status is not None:
            query["status"] = status
        if page is not None:
            query["page"] = page
        if limit is not None:
            query["limit"] = limit

        data = await self._http.get("/agents", query=query)
        return PaginatedList.from_dict(data, Agent)

    async def get(self, agent_id: str) -> Agent:
        data = await self._http.get(f"/agents/{agent_id}")
        return Agent.from_dict(data)

    async def verify(self, agent_id: str) -> AgentVerification:
        data = await self._http.get(f"/agents/{agent_id}/verify", auth=False)
        return AgentVerification.from_dict(data)

    async def activate(self, agent_id: str, *, public_key: str) -> Agent:
        data = await self._http.post(
            f"/agents/{agent_id}/activate", body={"public_key": public_key}
        )
        return Agent.from_dict(data)

    async def suspend(self, agent_id: str) -> Agent:
        data = await self._http.post(f"/agents/{agent_id}/suspend")
        return Agent.from_dict(data)

    async def revoke(self, agent_id: str) -> Agent:
        data = await self._http.post(f"/agents/{agent_id}/revoke")
        return Agent.from_dict(data)

    async def rotate_key(self, agent_id: str, *, public_key: str) -> Agent:
        data = await self._http.post(
            f"/agents/{agent_id}/rotate-key", body={"public_key": public_key}
        )
        return Agent.from_dict(data)

    async def update(
        self,
        agent_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        framework: Optional[str] = None,
        model_provider: Optional[str] = None,
        model_id: Optional[str] = None,
    ) -> Agent:
        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if tags is not None:
            body["tags"] = tags
        if framework is not None:
            body["framework"] = framework
        if model_provider is not None:
            body["model_provider"] = model_provider
        if model_id is not None:
            body["model_id"] = model_id
        data = await self._http.patch(f"/agents/{agent_id}", body=body)
        return Agent.from_dict(data)

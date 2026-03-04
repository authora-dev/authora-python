"""Agents resource -- create, list, activate, suspend, revoke, and rotate keys."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._http import AsyncHttpClient, SyncHttpClient
from ..types import Agent, AgentVerification, PaginatedList


class AgentsResource:
    """Manage Authora agents (synchronous).

    Agents represent autonomous software entities that can be granted
    permissions and participate in delegation chains.
    """

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
        """Create a new agent within a workspace.

        Args:
            workspace_id: The workspace to create the agent in.
            name: Human-readable agent name.
            created_by: Identifier of the user creating the agent.
            description: Optional description of the agent.
            expires_in: Optional expiry duration in seconds.
            tags: Optional list of tags.
            framework: Optional AI framework identifier.
            model_provider: Optional model provider name.
            model_id: Optional model identifier.

        Returns:
            The newly created Agent.
        """
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
        """List agents in a workspace with optional filters and pagination.

        Args:
            workspace_id: The workspace to list agents from.
            status: Optional status filter (pending, active, suspended, revoked).
            page: Page number (1-indexed).
            limit: Maximum number of items per page.

        Returns:
            A paginated list of Agent objects.
        """
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
        """Retrieve a single agent by its ID.

        Args:
            agent_id: The unique identifier of the agent.

        Returns:
            The Agent object.
        """
        data = self._http.get(f"/agents/{agent_id}")
        return Agent.from_dict(data)

    def verify(self, agent_id: str) -> AgentVerification:
        """Verify an agent's identity. This endpoint is public (no auth required).

        Args:
            agent_id: The unique identifier of the agent to verify.

        Returns:
            An AgentVerification result.
        """
        data = self._http.get(f"/agents/{agent_id}/verify", auth=False)
        return AgentVerification.from_dict(data)

    def activate(self, agent_id: str, *, public_key: str) -> Agent:
        """Activate a pending agent by providing its public key.

        Args:
            agent_id: The unique identifier of the agent.
            public_key: The agent's public key.

        Returns:
            The activated Agent.
        """
        data = self._http.post(f"/agents/{agent_id}/activate", body={"public_key": public_key})
        return Agent.from_dict(data)

    def suspend(self, agent_id: str) -> Agent:
        """Suspend an active agent, temporarily revoking its access.

        Args:
            agent_id: The unique identifier of the agent.

        Returns:
            The suspended Agent.
        """
        data = self._http.post(f"/agents/{agent_id}/suspend")
        return Agent.from_dict(data)

    def revoke(self, agent_id: str) -> Agent:
        """Permanently revoke an agent, removing all its access.

        Args:
            agent_id: The unique identifier of the agent.

        Returns:
            The revoked Agent.
        """
        data = self._http.post(f"/agents/{agent_id}/revoke")
        return Agent.from_dict(data)

    def rotate_key(self, agent_id: str, *, public_key: str) -> Agent:
        """Rotate an agent's key pair by providing a new public key.

        Args:
            agent_id: The unique identifier of the agent.
            public_key: The new public key.

        Returns:
            The Agent with updated key information.
        """
        data = self._http.post(f"/agents/{agent_id}/rotate-key", body={"public_key": public_key})
        return Agent.from_dict(data)


class AsyncAgentsResource:
    """Manage Authora agents (asynchronous).

    Agents represent autonomous software entities that can be granted
    permissions and participate in delegation chains.
    """

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
        """Create a new agent within a workspace.

        Args:
            workspace_id: The workspace to create the agent in.
            name: Human-readable agent name.
            created_by: Identifier of the user creating the agent.
            description: Optional description of the agent.
            expires_in: Optional expiry duration in seconds.
            tags: Optional list of tags.
            framework: Optional AI framework identifier.
            model_provider: Optional model provider name.
            model_id: Optional model identifier.

        Returns:
            The newly created Agent.
        """
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
        """List agents in a workspace with optional filters and pagination.

        Args:
            workspace_id: The workspace to list agents from.
            status: Optional status filter (pending, active, suspended, revoked).
            page: Page number (1-indexed).
            limit: Maximum number of items per page.

        Returns:
            A paginated list of Agent objects.
        """
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
        """Retrieve a single agent by its ID.

        Args:
            agent_id: The unique identifier of the agent.

        Returns:
            The Agent object.
        """
        data = await self._http.get(f"/agents/{agent_id}")
        return Agent.from_dict(data)

    async def verify(self, agent_id: str) -> AgentVerification:
        """Verify an agent's identity. This endpoint is public (no auth required).

        Args:
            agent_id: The unique identifier of the agent to verify.

        Returns:
            An AgentVerification result.
        """
        data = await self._http.get(f"/agents/{agent_id}/verify", auth=False)
        return AgentVerification.from_dict(data)

    async def activate(self, agent_id: str, *, public_key: str) -> Agent:
        """Activate a pending agent by providing its public key.

        Args:
            agent_id: The unique identifier of the agent.
            public_key: The agent's public key.

        Returns:
            The activated Agent.
        """
        data = await self._http.post(
            f"/agents/{agent_id}/activate", body={"public_key": public_key}
        )
        return Agent.from_dict(data)

    async def suspend(self, agent_id: str) -> Agent:
        """Suspend an active agent, temporarily revoking its access.

        Args:
            agent_id: The unique identifier of the agent.

        Returns:
            The suspended Agent.
        """
        data = await self._http.post(f"/agents/{agent_id}/suspend")
        return Agent.from_dict(data)

    async def revoke(self, agent_id: str) -> Agent:
        """Permanently revoke an agent, removing all its access.

        Args:
            agent_id: The unique identifier of the agent.

        Returns:
            The revoked Agent.
        """
        data = await self._http.post(f"/agents/{agent_id}/revoke")
        return Agent.from_dict(data)

    async def rotate_key(self, agent_id: str, *, public_key: str) -> Agent:
        """Rotate an agent's key pair by providing a new public key.

        Args:
            agent_id: The unique identifier of the agent.
            public_key: The new public key.

        Returns:
            The Agent with updated key information.
        """
        data = await self._http.post(
            f"/agents/{agent_id}/rotate-key", body={"public_key": public_key}
        )
        return Agent.from_dict(data)

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from ._http import AsyncHttpClient, SyncHttpClient
from .agent import AsyncAuthoraAgent, AuthoraAgent
from .crypto import KeyPair, generate_key_pair
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
from .resources.agents import AgentsResource, AsyncAgentsResource
from .resources.audit import AsyncAuditResource, AuditResource
from .resources.delegations import AsyncDelegationsResource, DelegationsResource
from .resources.mcp import AsyncMcpResource, McpResource
from .resources.notifications import AsyncNotificationsResource, NotificationsResource
from .resources.permissions import AsyncPermissionsResource, PermissionsResource
from .resources.policies import AsyncPoliciesResource, PoliciesResource
from .resources.roles import AsyncRolesResource, RolesResource
from .types import Agent, AgentVerification, CreateAgentResult

__version__ = "0.2.0"

__all__ = [
    "__version__",
    "AuthoraClient",
    "AsyncAuthoraClient",
    "AuthoraAgent",
    "AsyncAuthoraAgent",
    "AuthoraError",
    "AuthenticationError",
    "AuthorizationError",
    "NetworkError",
    "NotFoundError",
    "RateLimitError",
    "TimeoutError",
    "ValidationError",
    "generate_key_pair",
    "KeyPair",
    "CreateAgentResult",
]


class AuthoraClient:
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://api.authora.dev/api/v1",
        timeout: float = 30.0,
    ) -> None:
        self._http = SyncHttpClient(api_key=api_key, base_url=base_url, timeout=timeout)
        self._base_url = base_url
        self._timeout = timeout
        self.agents = AgentsResource(self._http)
        self.roles = RolesResource(self._http)
        self.permissions = PermissionsResource(self._http)
        self.delegations = DelegationsResource(self._http)
        self.policies = PoliciesResource(self._http)
        self.mcp = McpResource(self._http)
        self.audit = AuditResource(self._http)
        self.notifications = NotificationsResource(self._http)

    def create_agent(
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
    ) -> CreateAgentResult:
        agent = self.agents.create(
            workspace_id=workspace_id,
            name=name,
            created_by=created_by,
            description=description,
            expires_in=expires_in,
            tags=tags,
            framework=framework,
            model_provider=model_provider,
            model_id=model_id,
        )
        kp = generate_key_pair()
        agent = self.agents.activate(agent.id, public_key=kp.public_key)
        from .types import KeyPair as TypesKeyPair

        return CreateAgentResult(
            agent=agent,
            key_pair=TypesKeyPair(private_key=kp.private_key, public_key=kp.public_key),
        )

    def load_agent(
        self,
        agent_id: str,
        private_key: str,
        *,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        permissions_cache_ttl: float = 300.0,
    ) -> AuthoraAgent:
        return AuthoraAgent(
            agent_id=agent_id,
            private_key=private_key,
            base_url=base_url or self._base_url,
            timeout=timeout,
            permissions_cache_ttl=permissions_cache_ttl,
        )

    def verify_agent(self, agent_id: str) -> AgentVerification:
        return self.agents.verify(agent_id)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> AuthoraClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


class AsyncAuthoraClient:
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://api.authora.dev/api/v1",
        timeout: float = 30.0,
    ) -> None:
        self._http = AsyncHttpClient(api_key=api_key, base_url=base_url, timeout=timeout)
        self._base_url = base_url
        self._timeout = timeout
        self.agents = AsyncAgentsResource(self._http)
        self.roles = AsyncRolesResource(self._http)
        self.permissions = AsyncPermissionsResource(self._http)
        self.delegations = AsyncDelegationsResource(self._http)
        self.policies = AsyncPoliciesResource(self._http)
        self.mcp = AsyncMcpResource(self._http)
        self.audit = AsyncAuditResource(self._http)
        self.notifications = AsyncNotificationsResource(self._http)

    async def create_agent(
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
    ) -> CreateAgentResult:
        agent = await self.agents.create(
            workspace_id=workspace_id,
            name=name,
            created_by=created_by,
            description=description,
            expires_in=expires_in,
            tags=tags,
            framework=framework,
            model_provider=model_provider,
            model_id=model_id,
        )
        kp = generate_key_pair()
        agent = await self.agents.activate(agent.id, public_key=kp.public_key)
        from .types import KeyPair as TypesKeyPair

        return CreateAgentResult(
            agent=agent,
            key_pair=TypesKeyPair(private_key=kp.private_key, public_key=kp.public_key),
        )

    def load_agent(
        self,
        agent_id: str,
        private_key: str,
        *,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        permissions_cache_ttl: float = 300.0,
    ) -> AsyncAuthoraAgent:
        return AsyncAuthoraAgent(
            agent_id=agent_id,
            private_key=private_key,
            base_url=base_url or self._base_url,
            timeout=timeout,
            permissions_cache_ttl=permissions_cache_ttl,
        )

    async def verify_agent(self, agent_id: str) -> AgentVerification:
        return await self.agents.verify(agent_id)

    async def close(self) -> None:
        await self._http.close()

    async def __aenter__(self) -> AsyncAuthoraClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()

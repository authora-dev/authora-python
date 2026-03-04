"""Authora Python SDK -- agent identity and authorization for AI systems.

Usage::

    from authora import AuthoraClient

    client = AuthoraClient(api_key="authora_live_...")
    result = client.permissions.check(
        agent_id="agt_abc",
        resource="files:*",
        action="read",
    )
"""

from __future__ import annotations

from ._http import AsyncHttpClient, SyncHttpClient
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

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "AuthoraClient",
    "AsyncAuthoraClient",
    # Errors
    "AuthoraError",
    "AuthenticationError",
    "AuthorizationError",
    "NetworkError",
    "NotFoundError",
    "RateLimitError",
    "TimeoutError",
    "ValidationError",
]


class AuthoraClient:
    """Synchronous client for the Authora API.

    Args:
        api_key: Bearer token for authentication.
        base_url: API base URL. Defaults to ``https://api.authora.dev/api/v1``.
        timeout: Request timeout in seconds. Defaults to ``30.0``.
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://api.authora.dev/api/v1",
        timeout: float = 30.0,
    ) -> None:
        self._http = SyncHttpClient(api_key=api_key, base_url=base_url, timeout=timeout)
        self.agents = AgentsResource(self._http)
        self.roles = RolesResource(self._http)
        self.permissions = PermissionsResource(self._http)
        self.delegations = DelegationsResource(self._http)
        self.policies = PoliciesResource(self._http)
        self.mcp = McpResource(self._http)
        self.audit = AuditResource(self._http)
        self.notifications = NotificationsResource(self._http)

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._http.close()

    def __enter__(self) -> AuthoraClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


class AsyncAuthoraClient:
    """Asynchronous client for the Authora API.

    Args:
        api_key: Bearer token for authentication.
        base_url: API base URL. Defaults to ``https://api.authora.dev/api/v1``.
        timeout: Request timeout in seconds. Defaults to ``30.0``.
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://api.authora.dev/api/v1",
        timeout: float = 30.0,
    ) -> None:
        self._http = AsyncHttpClient(api_key=api_key, base_url=base_url, timeout=timeout)
        self.agents = AsyncAgentsResource(self._http)
        self.roles = AsyncRolesResource(self._http)
        self.permissions = AsyncPermissionsResource(self._http)
        self.delegations = AsyncDelegationsResource(self._http)
        self.policies = AsyncPoliciesResource(self._http)
        self.mcp = AsyncMcpResource(self._http)
        self.audit = AsyncAuditResource(self._http)
        self.notifications = AsyncNotificationsResource(self._http)

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._http.close()

    async def __aenter__(self) -> AsyncAuthoraClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()

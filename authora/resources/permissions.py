"""Permissions resource -- check, batch-check, and get effective permissions."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._http import AsyncHttpClient, SyncHttpClient
from ..types import (
    BatchPermissionCheckResult,
    EffectivePermission,
    PermissionCheckResult,
)


class PermissionsResource:
    """Check and query agent permissions (synchronous).

    Provides methods to check individual permissions, perform batch checks,
    and retrieve the effective permissions for a given agent.
    """

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
        """Check whether an agent has a specific permission on a resource.

        Args:
            agent_id: The agent to check permissions for.
            resource: The resource pattern to check against.
            action: The action to check.
            context: Optional additional context for the evaluation.

        Returns:
            A PermissionCheckResult indicating whether the action is allowed.
        """
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
        """Check multiple permissions for an agent in a single request.

        Args:
            agent_id: The agent to check permissions for.
            checks: List of dicts, each with ``resource`` and ``action`` keys.

        Returns:
            A BatchPermissionCheckResult with results for each check.
        """
        body: Dict[str, Any] = {
            "agent_id": agent_id,
            "checks": checks,
        }
        data = self._http.post("/permissions/check-batch", body=body)
        return BatchPermissionCheckResult.from_dict(data)

    def get_effective(self, agent_id: str) -> List[EffectivePermission]:
        """Retrieve the effective (resolved) permissions for an agent.

        Returns the combined permissions from all roles, policies,
        and delegations that apply to the agent.

        Args:
            agent_id: The unique identifier of the agent.

        Returns:
            List of EffectivePermission objects.
        """
        data = self._http.get(f"/agents/{agent_id}/permissions")
        return [EffectivePermission.from_dict(item) for item in data]


class AsyncPermissionsResource:
    """Check and query agent permissions (asynchronous).

    Provides methods to check individual permissions, perform batch checks,
    and retrieve the effective permissions for a given agent.
    """

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
        """Check whether an agent has a specific permission on a resource.

        Args:
            agent_id: The agent to check permissions for.
            resource: The resource pattern to check against.
            action: The action to check.
            context: Optional additional context for the evaluation.

        Returns:
            A PermissionCheckResult indicating whether the action is allowed.
        """
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
        """Check multiple permissions for an agent in a single request.

        Args:
            agent_id: The agent to check permissions for.
            checks: List of dicts, each with ``resource`` and ``action`` keys.

        Returns:
            A BatchPermissionCheckResult with results for each check.
        """
        body: Dict[str, Any] = {
            "agent_id": agent_id,
            "checks": checks,
        }
        data = await self._http.post("/permissions/check-batch", body=body)
        return BatchPermissionCheckResult.from_dict(data)

    async def get_effective(self, agent_id: str) -> List[EffectivePermission]:
        """Retrieve the effective (resolved) permissions for an agent.

        Returns the combined permissions from all roles, policies,
        and delegations that apply to the agent.

        Args:
            agent_id: The unique identifier of the agent.

        Returns:
            List of EffectivePermission objects.
        """
        data = await self._http.get(f"/agents/{agent_id}/permissions")
        return [EffectivePermission.from_dict(item) for item in data]

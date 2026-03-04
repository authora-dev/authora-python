"""Delegations resource -- create, get, revoke, verify, and list delegations."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._http import AsyncHttpClient, SyncHttpClient
from ..types import Delegation, DelegationVerification, PaginatedList


class DelegationsResource:
    """Manage permission delegations between agents (synchronous).

    Delegations allow one agent (the issuer) to grant a subset of its
    permissions to another agent (the target).
    """

    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(
        self,
        *,
        issuer_agent_id: str,
        target_agent_id: str,
        permissions: List[str],
        constraints: Optional[Dict[str, Any]] = None,
    ) -> Delegation:
        """Create a new delegation from one agent to another.

        Args:
            issuer_agent_id: The agent granting the delegation.
            target_agent_id: The agent receiving the delegation.
            permissions: List of permission strings to delegate.
            constraints: Optional constraints on the delegation.

        Returns:
            The created Delegation.
        """
        body: Dict[str, Any] = {
            "issuer_agent_id": issuer_agent_id,
            "target_agent_id": target_agent_id,
            "permissions": permissions,
        }
        if constraints is not None:
            body["constraints"] = constraints

        data = self._http.post("/delegations", body=body)
        return Delegation.from_dict(data)

    def get(self, delegation_id: str) -> Delegation:
        """Retrieve a delegation by its ID.

        Args:
            delegation_id: The unique identifier of the delegation.

        Returns:
            The Delegation object.
        """
        data = self._http.get(f"/delegations/{delegation_id}")
        return Delegation.from_dict(data)

    def revoke(self, delegation_id: str) -> Delegation:
        """Revoke an active delegation.

        Args:
            delegation_id: The unique identifier of the delegation to revoke.

        Returns:
            The revoked Delegation.
        """
        data = self._http.post(f"/delegations/{delegation_id}/revoke")
        return Delegation.from_dict(data)

    def verify(self, *, delegation_id: str) -> DelegationVerification:
        """Verify that a delegation is valid and active.

        Args:
            delegation_id: The unique identifier of the delegation to verify.

        Returns:
            A DelegationVerification result.
        """
        data = self._http.post("/delegations/verify", body={"delegation_id": delegation_id})
        return DelegationVerification.from_dict(data)

    def list(self) -> PaginatedList[Delegation]:
        """List all delegations.

        Returns:
            A paginated list of Delegation objects.
        """
        data = self._http.get("/delegations")
        return PaginatedList.from_dict(data, Delegation)

    def list_by_agent(
        self,
        agent_id: str,
        *,
        direction: Optional[str] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> PaginatedList[Delegation]:
        """List delegations for a specific agent (issued or received).

        Args:
            agent_id: The unique identifier of the agent.
            direction: Filter by 'issued' or 'received'.
            page: Page number (1-indexed).
            limit: Maximum number of items per page.

        Returns:
            A paginated list of Delegation objects.
        """
        query: Dict[str, Any] = {}
        if direction is not None:
            query["direction"] = direction
        if page is not None:
            query["page"] = page
        if limit is not None:
            query["limit"] = limit

        data = self._http.get(
            f"/agents/{agent_id}/delegations",
            query=query if query else None,
        )
        return PaginatedList.from_dict(data, Delegation)


class AsyncDelegationsResource:
    """Manage permission delegations between agents (asynchronous).

    Delegations allow one agent (the issuer) to grant a subset of its
    permissions to another agent (the target).
    """

    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(
        self,
        *,
        issuer_agent_id: str,
        target_agent_id: str,
        permissions: List[str],
        constraints: Optional[Dict[str, Any]] = None,
    ) -> Delegation:
        """Create a new delegation from one agent to another.

        Args:
            issuer_agent_id: The agent granting the delegation.
            target_agent_id: The agent receiving the delegation.
            permissions: List of permission strings to delegate.
            constraints: Optional constraints on the delegation.

        Returns:
            The created Delegation.
        """
        body: Dict[str, Any] = {
            "issuer_agent_id": issuer_agent_id,
            "target_agent_id": target_agent_id,
            "permissions": permissions,
        }
        if constraints is not None:
            body["constraints"] = constraints

        data = await self._http.post("/delegations", body=body)
        return Delegation.from_dict(data)

    async def get(self, delegation_id: str) -> Delegation:
        """Retrieve a delegation by its ID.

        Args:
            delegation_id: The unique identifier of the delegation.

        Returns:
            The Delegation object.
        """
        data = await self._http.get(f"/delegations/{delegation_id}")
        return Delegation.from_dict(data)

    async def revoke(self, delegation_id: str) -> Delegation:
        """Revoke an active delegation.

        Args:
            delegation_id: The unique identifier of the delegation to revoke.

        Returns:
            The revoked Delegation.
        """
        data = await self._http.post(f"/delegations/{delegation_id}/revoke")
        return Delegation.from_dict(data)

    async def verify(self, *, delegation_id: str) -> DelegationVerification:
        """Verify that a delegation is valid and active.

        Args:
            delegation_id: The unique identifier of the delegation to verify.

        Returns:
            A DelegationVerification result.
        """
        data = await self._http.post("/delegations/verify", body={"delegation_id": delegation_id})
        return DelegationVerification.from_dict(data)

    async def list(self) -> PaginatedList[Delegation]:
        """List all delegations.

        Returns:
            A paginated list of Delegation objects.
        """
        data = await self._http.get("/delegations")
        return PaginatedList.from_dict(data, Delegation)

    async def list_by_agent(
        self,
        agent_id: str,
        *,
        direction: Optional[str] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> PaginatedList[Delegation]:
        """List delegations for a specific agent (issued or received).

        Args:
            agent_id: The unique identifier of the agent.
            direction: Filter by 'issued' or 'received'.
            page: Page number (1-indexed).
            limit: Maximum number of items per page.

        Returns:
            A paginated list of Delegation objects.
        """
        query: Dict[str, Any] = {}
        if direction is not None:
            query["direction"] = direction
        if page is not None:
            query["page"] = page
        if limit is not None:
            query["limit"] = limit

        data = await self._http.get(
            f"/agents/{agent_id}/delegations",
            query=query if query else None,
        )
        return PaginatedList.from_dict(data, Delegation)

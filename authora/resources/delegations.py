from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._http import AsyncHttpClient, SyncHttpClient
from ..types import Delegation, DelegationVerification, PaginatedList


class DelegationsResource:
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
        data = self._http.get(f"/delegations/{delegation_id}")
        return Delegation.from_dict(data)

    def revoke(self, delegation_id: str) -> Delegation:
        data = self._http.post(f"/delegations/{delegation_id}/revoke")
        return Delegation.from_dict(data)

    def verify(self, *, delegation_id: str) -> DelegationVerification:
        data = self._http.post("/delegations/verify", body={"delegation_id": delegation_id})
        return DelegationVerification.from_dict(data)

    def list(self) -> PaginatedList[Delegation]:
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
        data = await self._http.get(f"/delegations/{delegation_id}")
        return Delegation.from_dict(data)

    async def revoke(self, delegation_id: str) -> Delegation:
        data = await self._http.post(f"/delegations/{delegation_id}/revoke")
        return Delegation.from_dict(data)

    async def verify(self, *, delegation_id: str) -> DelegationVerification:
        data = await self._http.post("/delegations/verify", body={"delegation_id": delegation_id})
        return DelegationVerification.from_dict(data)

    async def list(self) -> PaginatedList[Delegation]:
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

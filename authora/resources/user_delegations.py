from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._http import AsyncHttpClient, SyncHttpClient
from ..types import (
    UserDelegationGrant,
    UserDelegationOrgList,
    UserDelegationToken,
    VerifyUserDelegationTokenResult,
)


class UserDelegationsResource:
    """Manage user-to-agent delegation grants."""

    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(
        self,
        *,
        user_id: str,
        user_email: str,
        user_idp_subject: str,
        user_idp_provider: str,
        agent_id: str,
        agent_org_id: str,
        user_org_id: str,
        user_workspace_id: str,
        requested_scopes: List[str],
        granted_scopes: List[str],
        max_duration_seconds: int,
        consent_method: str,
        platform_signature: str,
        expires_at: str,
        trust_relationship_id: Optional[str] = None,
        max_uses: Optional[int] = None,
        no_redelegation: Optional[bool] = None,
        renewal_interval_sec: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> UserDelegationGrant:
        body: Dict[str, Any] = {
            "user_id": user_id,
            "user_email": user_email,
            "user_idp_subject": user_idp_subject,
            "user_idp_provider": user_idp_provider,
            "agent_id": agent_id,
            "agent_org_id": agent_org_id,
            "user_org_id": user_org_id,
            "user_workspace_id": user_workspace_id,
            "requested_scopes": requested_scopes,
            "granted_scopes": granted_scopes,
            "max_duration_seconds": max_duration_seconds,
            "consent_method": consent_method,
            "platform_signature": platform_signature,
            "expires_at": expires_at,
        }
        if trust_relationship_id is not None:
            body["trust_relationship_id"] = trust_relationship_id
        if max_uses is not None:
            body["max_uses"] = max_uses
        if no_redelegation is not None:
            body["no_redelegation"] = no_redelegation
        if renewal_interval_sec is not None:
            body["renewal_interval_sec"] = renewal_interval_sec
        if reason is not None:
            body["reason"] = reason

        data = self._http.post("/user-delegations", body=body)
        return UserDelegationGrant.from_dict(data)

    def get(self, grant_id: str) -> UserDelegationGrant:
        data = self._http.get(f"/user-delegations/{grant_id}")
        return UserDelegationGrant.from_dict(data)

    def list_by_user(
        self, user_id: str, *, status: Optional[str] = None
    ) -> List[UserDelegationGrant]:
        query: Dict[str, Any] = {}
        if status is not None:
            query["status"] = status
        data = self._http.get(
            f"/user-delegations/by-user/{user_id}",
            query=query if query else None,
        )
        return [UserDelegationGrant.from_dict(g) for g in data]

    def list_by_agent(
        self, agent_id: str, *, status: Optional[str] = None
    ) -> List[UserDelegationGrant]:
        query: Dict[str, Any] = {}
        if status is not None:
            query["status"] = status
        data = self._http.get(
            f"/user-delegations/by-agent/{agent_id}",
            query=query if query else None,
        )
        return [UserDelegationGrant.from_dict(g) for g in data]

    def list_by_org(
        self,
        org_id: str,
        *,
        status: Optional[str] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> UserDelegationOrgList:
        query: Dict[str, Any] = {}
        if status is not None:
            query["status"] = status
        if page is not None:
            query["page"] = page
        if limit is not None:
            query["limit"] = limit
        data = self._http.get(
            f"/user-delegations/by-org/{org_id}",
            query=query if query else None,
        )
        return UserDelegationOrgList.from_dict(data)

    def revoke(
        self, grant_id: str, *, revoked_by: str, reason: Optional[str] = None
    ) -> UserDelegationGrant:
        body: Dict[str, Any] = {"revoked_by": revoked_by}
        if reason is not None:
            body["reason"] = reason
        data = self._http.post(f"/user-delegations/{grant_id}/revoke", body=body)
        return UserDelegationGrant.from_dict(data)

    def issue_token(
        self,
        grant_id: str,
        *,
        agent_full_id: str,
        audience: Optional[Any] = None,
        lifetime_seconds: Optional[int] = None,
    ) -> UserDelegationToken:
        body: Dict[str, Any] = {"agent_full_id": agent_full_id}
        if audience is not None:
            body["audience"] = audience
        if lifetime_seconds is not None:
            body["lifetime_seconds"] = lifetime_seconds
        data = self._http.post(f"/user-delegations/{grant_id}/token", body=body)
        return UserDelegationToken.from_dict(data)

    def refresh_token(
        self,
        grant_id: str,
        *,
        agent_full_id: str,
        current_token: Optional[str] = None,
        audience: Optional[Any] = None,
    ) -> UserDelegationToken:
        body: Dict[str, Any] = {"agent_full_id": agent_full_id}
        if current_token is not None:
            body["current_token"] = current_token
        if audience is not None:
            body["audience"] = audience
        data = self._http.post(f"/user-delegations/{grant_id}/refresh", body=body)
        return UserDelegationToken.from_dict(data)

    def verify_token(
        self, token: str, *, audience: Optional[str] = None
    ) -> VerifyUserDelegationTokenResult:
        body: Dict[str, Any] = {"token": token}
        if audience is not None:
            body["audience"] = audience
        data = self._http.post("/user-delegations/tokens/verify", body=body)
        return VerifyUserDelegationTokenResult.from_dict(data)


class AsyncUserDelegationsResource:
    """Manage user-to-agent delegation grants (async)."""

    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(
        self,
        *,
        user_id: str,
        user_email: str,
        user_idp_subject: str,
        user_idp_provider: str,
        agent_id: str,
        agent_org_id: str,
        user_org_id: str,
        user_workspace_id: str,
        requested_scopes: List[str],
        granted_scopes: List[str],
        max_duration_seconds: int,
        consent_method: str,
        platform_signature: str,
        expires_at: str,
        trust_relationship_id: Optional[str] = None,
        max_uses: Optional[int] = None,
        no_redelegation: Optional[bool] = None,
        renewal_interval_sec: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> UserDelegationGrant:
        body: Dict[str, Any] = {
            "user_id": user_id,
            "user_email": user_email,
            "user_idp_subject": user_idp_subject,
            "user_idp_provider": user_idp_provider,
            "agent_id": agent_id,
            "agent_org_id": agent_org_id,
            "user_org_id": user_org_id,
            "user_workspace_id": user_workspace_id,
            "requested_scopes": requested_scopes,
            "granted_scopes": granted_scopes,
            "max_duration_seconds": max_duration_seconds,
            "consent_method": consent_method,
            "platform_signature": platform_signature,
            "expires_at": expires_at,
        }
        if trust_relationship_id is not None:
            body["trust_relationship_id"] = trust_relationship_id
        if max_uses is not None:
            body["max_uses"] = max_uses
        if no_redelegation is not None:
            body["no_redelegation"] = no_redelegation
        if renewal_interval_sec is not None:
            body["renewal_interval_sec"] = renewal_interval_sec
        if reason is not None:
            body["reason"] = reason

        data = await self._http.post("/user-delegations", body=body)
        return UserDelegationGrant.from_dict(data)

    async def get(self, grant_id: str) -> UserDelegationGrant:
        data = await self._http.get(f"/user-delegations/{grant_id}")
        return UserDelegationGrant.from_dict(data)

    async def list_by_user(
        self, user_id: str, *, status: Optional[str] = None
    ) -> List[UserDelegationGrant]:
        query: Dict[str, Any] = {}
        if status is not None:
            query["status"] = status
        data = await self._http.get(
            f"/user-delegations/by-user/{user_id}",
            query=query if query else None,
        )
        return [UserDelegationGrant.from_dict(g) for g in data]

    async def list_by_agent(
        self, agent_id: str, *, status: Optional[str] = None
    ) -> List[UserDelegationGrant]:
        query: Dict[str, Any] = {}
        if status is not None:
            query["status"] = status
        data = await self._http.get(
            f"/user-delegations/by-agent/{agent_id}",
            query=query if query else None,
        )
        return [UserDelegationGrant.from_dict(g) for g in data]

    async def list_by_org(
        self,
        org_id: str,
        *,
        status: Optional[str] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> UserDelegationOrgList:
        query: Dict[str, Any] = {}
        if status is not None:
            query["status"] = status
        if page is not None:
            query["page"] = page
        if limit is not None:
            query["limit"] = limit
        data = await self._http.get(
            f"/user-delegations/by-org/{org_id}",
            query=query if query else None,
        )
        return UserDelegationOrgList.from_dict(data)

    async def revoke(
        self, grant_id: str, *, revoked_by: str, reason: Optional[str] = None
    ) -> UserDelegationGrant:
        body: Dict[str, Any] = {"revoked_by": revoked_by}
        if reason is not None:
            body["reason"] = reason
        data = await self._http.post(f"/user-delegations/{grant_id}/revoke", body=body)
        return UserDelegationGrant.from_dict(data)

    async def issue_token(
        self,
        grant_id: str,
        *,
        agent_full_id: str,
        audience: Optional[Any] = None,
        lifetime_seconds: Optional[int] = None,
    ) -> UserDelegationToken:
        body: Dict[str, Any] = {"agent_full_id": agent_full_id}
        if audience is not None:
            body["audience"] = audience
        if lifetime_seconds is not None:
            body["lifetime_seconds"] = lifetime_seconds
        data = await self._http.post(f"/user-delegations/{grant_id}/token", body=body)
        return UserDelegationToken.from_dict(data)

    async def refresh_token(
        self,
        grant_id: str,
        *,
        agent_full_id: str,
        current_token: Optional[str] = None,
        audience: Optional[Any] = None,
    ) -> UserDelegationToken:
        body: Dict[str, Any] = {"agent_full_id": agent_full_id}
        if current_token is not None:
            body["current_token"] = current_token
        if audience is not None:
            body["audience"] = audience
        data = await self._http.post(f"/user-delegations/{grant_id}/refresh", body=body)
        return UserDelegationToken.from_dict(data)

    async def verify_token(
        self, token: str, *, audience: Optional[str] = None
    ) -> VerifyUserDelegationTokenResult:
        body: Dict[str, Any] = {"token": token}
        if audience is not None:
            body["audience"] = audience
        data = await self._http.post("/user-delegations/tokens/verify", body=body)
        return VerifyUserDelegationTokenResult.from_dict(data)

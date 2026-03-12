from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._http import AsyncHttpClient, SyncHttpClient


class ApprovalsResource:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(self, **kwargs: Any) -> Dict[str, Any]:
        return self._http.post("/approvals", json=kwargs)

    def list(
        self,
        *,
        status: Optional[str] = None,
        risk_level: Optional[str] = None,
        agent_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        if risk_level is not None:
            params["riskLevel"] = risk_level
        if agent_id is not None:
            params["agentId"] = agent_id
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        return self._http.get("/approvals", params=params)

    def get(self, challenge_id: str) -> Dict[str, Any]:
        return self._http.get(f"/approvals/{challenge_id}")

    def get_status(self, challenge_id: str) -> Dict[str, Any]:
        return self._http.get(f"/approvals/{challenge_id}/status")

    def stats(self) -> Dict[str, Any]:
        return self._http.get("/approvals/stats")

    def decide(self, challenge_id: str, **kwargs: Any) -> Dict[str, Any]:
        return self._http.post(f"/approvals/{challenge_id}/decide", json=kwargs)

    def bulk_decide(self, **kwargs: Any) -> Dict[str, Any]:
        return self._http.post("/approvals/bulk-decide", json=kwargs)

    def suggestions(self, challenge_id: str) -> List[Dict[str, Any]]:
        return self._http.post(f"/approvals/{challenge_id}/suggestions")

    def get_settings(self) -> Dict[str, Any]:
        return self._http.get("/approvals/settings")

    def update_settings(self, **kwargs: Any) -> Dict[str, Any]:
        return self._http.patch("/approvals/settings", json=kwargs)

    def test_ai(self, **kwargs: Any) -> Dict[str, Any]:
        return self._http.post("/approvals/settings/test-ai", json=kwargs)

    def list_patterns(
        self,
        *,
        status: Optional[str] = None,
        ready_only: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        if ready_only is not None:
            params["readyOnly"] = ready_only
        return self._http.get("/approvals/patterns", params=params)

    def dismiss_pattern(self, pattern_id: str) -> None:
        self._http.post(f"/approvals/patterns/{pattern_id}/dismiss")

    def create_policy_from_pattern(self, pattern_id: str) -> Dict[str, Any]:
        return self._http.post(f"/approvals/patterns/{pattern_id}/create-policy")

    def list_escalation_rules(self) -> List[Dict[str, Any]]:
        return self._http.get("/approvals/escalation-rules")

    def get_escalation_rule(self, rule_id: str) -> Dict[str, Any]:
        return self._http.get(f"/approvals/escalation-rules/{rule_id}")

    def create_escalation_rule(self, **kwargs: Any) -> Dict[str, Any]:
        return self._http.post("/approvals/escalation-rules", json=kwargs)

    def update_escalation_rule(self, rule_id: str, **kwargs: Any) -> Dict[str, Any]:
        return self._http.patch(f"/approvals/escalation-rules/{rule_id}", json=kwargs)

    def delete_escalation_rule(self, rule_id: str) -> None:
        self._http.delete(f"/approvals/escalation-rules/{rule_id}")

    def get_vapid_key(self) -> Dict[str, Any]:
        return self._http.get("/approvals/push/vapid-key")

    def subscribe_push(self, *, endpoint: str, keys: Dict[str, str]) -> None:
        self._http.post("/approvals/push/subscribe", json={"endpoint": endpoint, "keys": keys})

    def unsubscribe_push(self, *, endpoint: str) -> None:
        self._http.post("/approvals/push/unsubscribe", json={"endpoint": endpoint})

    def list_webhooks(self) -> List[Dict[str, Any]]:
        return self._http.get("/approvals/webhooks")

    def create_webhook(self, **kwargs: Any) -> Dict[str, Any]:
        return self._http.post("/approvals/webhooks", json=kwargs)

    def update_webhook(self, webhook_id: str, **kwargs: Any) -> Dict[str, Any]:
        return self._http.patch(f"/approvals/webhooks/{webhook_id}", json=kwargs)

    def delete_webhook(self, webhook_id: str) -> None:
        self._http.delete(f"/approvals/webhooks/{webhook_id}")


class AsyncApprovalsResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(self, **kwargs: Any) -> Dict[str, Any]:
        return await self._http.post("/approvals", json=kwargs)

    async def list(
        self,
        *,
        status: Optional[str] = None,
        risk_level: Optional[str] = None,
        agent_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        if risk_level is not None:
            params["riskLevel"] = risk_level
        if agent_id is not None:
            params["agentId"] = agent_id
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        return await self._http.get("/approvals", params=params)

    async def get(self, challenge_id: str) -> Dict[str, Any]:
        return await self._http.get(f"/approvals/{challenge_id}")

    async def stats(self) -> Dict[str, Any]:
        return await self._http.get("/approvals/stats")

    async def decide(self, challenge_id: str, **kwargs: Any) -> Dict[str, Any]:
        return await self._http.post(f"/approvals/{challenge_id}/decide", json=kwargs)

    async def bulk_decide(self, **kwargs: Any) -> Dict[str, Any]:
        return await self._http.post("/approvals/bulk-decide", json=kwargs)

    async def suggestions(self, challenge_id: str) -> List[Dict[str, Any]]:
        return await self._http.post(f"/approvals/{challenge_id}/suggestions")

    async def get_settings(self) -> Dict[str, Any]:
        return await self._http.get("/approvals/settings")

    async def update_settings(self, **kwargs: Any) -> Dict[str, Any]:
        return await self._http.patch("/approvals/settings", json=kwargs)

    async def list_patterns(self, **kwargs: Any) -> List[Dict[str, Any]]:
        return await self._http.get("/approvals/patterns", params=kwargs)

    async def dismiss_pattern(self, pattern_id: str) -> None:
        await self._http.post(f"/approvals/patterns/{pattern_id}/dismiss")

    async def list_escalation_rules(self) -> List[Dict[str, Any]]:
        return await self._http.get("/approvals/escalation-rules")

    async def create_escalation_rule(self, **kwargs: Any) -> Dict[str, Any]:
        return await self._http.post("/approvals/escalation-rules", json=kwargs)

    async def list_webhooks(self) -> List[Dict[str, Any]]:
        return await self._http.get("/approvals/webhooks")

    async def create_webhook(self, **kwargs: Any) -> Dict[str, Any]:
        return await self._http.post("/approvals/webhooks", json=kwargs)

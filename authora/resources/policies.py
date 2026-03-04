from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._http import AsyncHttpClient, SyncHttpClient
from ..types import (
    PaginatedList,
    Policy,
    PolicyEvaluationResult,
    PolicySimulationResult,
)


class PoliciesResource:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def create(
        self,
        *,
        workspace_id: str,
        name: str,
        effect: str,
        principals: List[str],
        resources: List[str],
        description: Optional[str] = None,
        actions: Optional[List[str]] = None,
        conditions: Optional[Dict[str, Any]] = None,
        priority: Optional[int] = None,
        enabled: Optional[bool] = None,
    ) -> Policy:
        body: Dict[str, Any] = {
            "workspace_id": workspace_id,
            "name": name,
            "effect": effect,
            "principals": principals,
            "resources": resources,
        }
        if description is not None:
            body["description"] = description
        if actions is not None:
            body["actions"] = actions
        if conditions is not None:
            body["conditions"] = conditions
        if priority is not None:
            body["priority"] = priority
        if enabled is not None:
            body["enabled"] = enabled

        data = self._http.post("/policies", body=body)
        return Policy.from_dict(data)

    def list(self, *, workspace_id: str) -> PaginatedList[Policy]:
        data = self._http.get("/policies", query={"workspace_id": workspace_id})
        return PaginatedList.from_dict(data, Policy)

    def update(
        self,
        policy_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        effect: Optional[str] = None,
        principals: Optional[List[str]] = None,
        resources: Optional[List[str]] = None,
        actions: Optional[List[str]] = None,
        conditions: Optional[Dict[str, Any]] = None,
        priority: Optional[int] = None,
        enabled: Optional[bool] = None,
    ) -> Policy:
        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if effect is not None:
            body["effect"] = effect
        if principals is not None:
            body["principals"] = principals
        if resources is not None:
            body["resources"] = resources
        if actions is not None:
            body["actions"] = actions
        if conditions is not None:
            body["conditions"] = conditions
        if priority is not None:
            body["priority"] = priority
        if enabled is not None:
            body["enabled"] = enabled

        data = self._http.patch(f"/policies/{policy_id}", body=body)
        return Policy.from_dict(data)

    def delete(self, policy_id: str) -> None:
        self._http.delete(f"/policies/{policy_id}")

    def simulate(
        self,
        *,
        workspace_id: str,
        agent_id: str,
        resource: str,
        action: str,
    ) -> PolicySimulationResult:
        body: Dict[str, Any] = {
            "workspace_id": workspace_id,
            "agent_id": agent_id,
            "resource": resource,
            "action": action,
        }
        data = self._http.post("/policies/simulate", body=body)
        return PolicySimulationResult.from_dict(data)

    def evaluate(
        self,
        *,
        workspace_id: str,
        agent_id: str,
        resource: str,
        action: str,
    ) -> PolicyEvaluationResult:
        body: Dict[str, Any] = {
            "workspace_id": workspace_id,
            "agent_id": agent_id,
            "resource": resource,
            "action": action,
        }
        data = self._http.post("/policies/evaluate", body=body)
        return PolicyEvaluationResult.from_dict(data)


class AsyncPoliciesResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def create(
        self,
        *,
        workspace_id: str,
        name: str,
        effect: str,
        principals: List[str],
        resources: List[str],
        description: Optional[str] = None,
        actions: Optional[List[str]] = None,
        conditions: Optional[Dict[str, Any]] = None,
        priority: Optional[int] = None,
        enabled: Optional[bool] = None,
    ) -> Policy:
        body: Dict[str, Any] = {
            "workspace_id": workspace_id,
            "name": name,
            "effect": effect,
            "principals": principals,
            "resources": resources,
        }
        if description is not None:
            body["description"] = description
        if actions is not None:
            body["actions"] = actions
        if conditions is not None:
            body["conditions"] = conditions
        if priority is not None:
            body["priority"] = priority
        if enabled is not None:
            body["enabled"] = enabled

        data = await self._http.post("/policies", body=body)
        return Policy.from_dict(data)

    async def list(self, *, workspace_id: str) -> PaginatedList[Policy]:
        data = await self._http.get("/policies", query={"workspace_id": workspace_id})
        return PaginatedList.from_dict(data, Policy)

    async def update(
        self,
        policy_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        effect: Optional[str] = None,
        principals: Optional[List[str]] = None,
        resources: Optional[List[str]] = None,
        actions: Optional[List[str]] = None,
        conditions: Optional[Dict[str, Any]] = None,
        priority: Optional[int] = None,
        enabled: Optional[bool] = None,
    ) -> Policy:
        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if effect is not None:
            body["effect"] = effect
        if principals is not None:
            body["principals"] = principals
        if resources is not None:
            body["resources"] = resources
        if actions is not None:
            body["actions"] = actions
        if conditions is not None:
            body["conditions"] = conditions
        if priority is not None:
            body["priority"] = priority
        if enabled is not None:
            body["enabled"] = enabled

        data = await self._http.patch(f"/policies/{policy_id}", body=body)
        return Policy.from_dict(data)

    async def delete(self, policy_id: str) -> None:
        await self._http.delete(f"/policies/{policy_id}")

    async def simulate(
        self,
        *,
        workspace_id: str,
        agent_id: str,
        resource: str,
        action: str,
    ) -> PolicySimulationResult:
        body: Dict[str, Any] = {
            "workspace_id": workspace_id,
            "agent_id": agent_id,
            "resource": resource,
            "action": action,
        }
        data = await self._http.post("/policies/simulate", body=body)
        return PolicySimulationResult.from_dict(data)

    async def evaluate(
        self,
        *,
        workspace_id: str,
        agent_id: str,
        resource: str,
        action: str,
    ) -> PolicyEvaluationResult:
        body: Dict[str, Any] = {
            "workspace_id": workspace_id,
            "agent_id": agent_id,
            "resource": resource,
            "action": action,
        }
        data = await self._http.post("/policies/evaluate", body=body)
        return PolicyEvaluationResult.from_dict(data)

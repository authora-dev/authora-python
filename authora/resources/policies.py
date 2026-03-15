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

    def attach_to_target(
        self, *, policy_id: str, target_type: str, target_id: str
    ) -> Dict[str, Any]:
        """Attach a policy to an agent or MCP server."""
        return self._http.post(
            "/policies/attachments",
            body={"policyId": policy_id, "targetType": target_type, "targetId": target_id},
        )

    def detach_from_target(self, *, policy_id: str, target_type: str, target_id: str) -> None:
        """Detach a policy from an agent or MCP server."""
        self._http.post(
            "/policies/detach",
            body={"policyId": policy_id, "targetType": target_type, "targetId": target_id},
        )

    def detach_by_id(self, attachment_id: str) -> None:
        """Detach a policy attachment by its ID."""
        self._http.delete(f"/policies/attachments/{attachment_id}")

    def list_attachments(self, *, target_type: str, target_id: str) -> Dict[str, Any]:
        """List all policies attached to a specific agent or MCP server."""
        return self._http.get(
            "/policies/attachments", query={"targetType": target_type, "targetId": target_id}
        )

    def list_policy_targets(self, policy_id: str) -> Dict[str, Any]:
        """List all targets a policy is attached to."""
        return self._http.get(f"/policies/{policy_id}/attachments")

    def add_permission(
        self,
        *,
        policy_id: str,
        resources: Optional[List[str]] = None,
        actions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Add resources/actions to an existing policy."""
        return self._http.post(
            "/policies/add-permission",
            body={"policyId": policy_id, "resources": resources or [], "actions": actions or []},
        )

    def remove_permission(
        self,
        *,
        policy_id: str,
        resources: Optional[List[str]] = None,
        actions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Remove resources/actions from a policy."""
        return self._http.post(
            "/policies/remove-permission",
            body={"policyId": policy_id, "resources": resources or [], "actions": actions or []},
        )


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

    async def attach_to_target(
        self, *, policy_id: str, target_type: str, target_id: str
    ) -> Dict[str, Any]:
        """Attach a policy to an agent or MCP server."""
        return await self._http.post(
            "/policies/attachments",
            body={"policyId": policy_id, "targetType": target_type, "targetId": target_id},
        )

    async def detach_from_target(
        self, *, policy_id: str, target_type: str, target_id: str
    ) -> None:
        """Detach a policy from an agent or MCP server."""
        await self._http.post(
            "/policies/detach",
            body={"policyId": policy_id, "targetType": target_type, "targetId": target_id},
        )

    async def detach_by_id(self, attachment_id: str) -> None:
        """Detach a policy attachment by its ID."""
        await self._http.delete(f"/policies/attachments/{attachment_id}")

    async def list_attachments(self, *, target_type: str, target_id: str) -> Dict[str, Any]:
        """List all policies attached to a specific agent or MCP server."""
        return await self._http.get(
            "/policies/attachments", query={"targetType": target_type, "targetId": target_id}
        )

    async def list_policy_targets(self, policy_id: str) -> Dict[str, Any]:
        """List all targets a policy is attached to."""
        return await self._http.get(f"/policies/{policy_id}/attachments")

    async def add_permission(
        self,
        *,
        policy_id: str,
        resources: Optional[List[str]] = None,
        actions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Add resources/actions to an existing policy."""
        return await self._http.post(
            "/policies/add-permission",
            body={"policyId": policy_id, "resources": resources or [], "actions": actions or []},
        )

    async def remove_permission(
        self,
        *,
        policy_id: str,
        resources: Optional[List[str]] = None,
        actions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Remove resources/actions from a policy."""
        return await self._http.post(
            "/policies/remove-permission",
            body={"policyId": policy_id, "resources": resources or [], "actions": actions or []},
        )

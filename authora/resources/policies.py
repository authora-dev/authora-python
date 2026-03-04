"""Policies resource -- create, list, update, delete, simulate, and evaluate."""

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
    """Manage authorization policies (synchronous).

    Policies define fine-grained access control rules that determine
    whether agents can perform specific actions on resources.
    """

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
        """Create a new policy in a workspace.

        Args:
            workspace_id: The workspace to create the policy in.
            name: Human-readable policy name.
            effect: Policy effect ('allow' or 'deny').
            principals: Agent patterns this policy applies to.
            resources: Resource patterns this policy governs.
            description: Optional policy description.
            actions: Optional list of action strings.
            conditions: Optional condition expressions.
            priority: Optional evaluation priority (higher = evaluated first).
            enabled: Whether the policy is active (defaults to True on the server).

        Returns:
            The newly created Policy.
        """
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
        """List policies in a workspace.

        Args:
            workspace_id: The workspace to list policies from.

        Returns:
            A paginated list of Policy objects.
        """
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
        """Update an existing policy. Only provided fields are modified.

        Args:
            policy_id: The unique identifier of the policy to update.
            name: New policy name.
            description: New description.
            effect: Updated effect.
            principals: Updated principal patterns.
            resources: Updated resource patterns.
            actions: Updated action list.
            conditions: Updated conditions.
            priority: Updated priority.
            enabled: Updated enabled state.

        Returns:
            The updated Policy.
        """
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
        """Delete a policy by its ID.

        Args:
            policy_id: The unique identifier of the policy to delete.
        """
        self._http.delete(f"/policies/{policy_id}")

    def simulate(
        self,
        *,
        workspace_id: str,
        agent_id: str,
        resource: str,
        action: str,
    ) -> PolicySimulationResult:
        """Simulate a policy evaluation without enforcing the result.

        Useful for testing policy configurations before they go live.

        Args:
            workspace_id: The workspace context.
            agent_id: The agent to simulate for.
            resource: The resource to simulate access to.
            action: The action to simulate.

        Returns:
            A PolicySimulationResult showing which policies would match.
        """
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
        """Evaluate policies for a given agent, resource, and action.

        Args:
            workspace_id: The workspace context.
            agent_id: The agent to evaluate for.
            resource: The resource to evaluate access to.
            action: The action to evaluate.

        Returns:
            A PolicyEvaluationResult.
        """
        body: Dict[str, Any] = {
            "workspace_id": workspace_id,
            "agent_id": agent_id,
            "resource": resource,
            "action": action,
        }
        data = self._http.post("/policies/evaluate", body=body)
        return PolicyEvaluationResult.from_dict(data)


class AsyncPoliciesResource:
    """Manage authorization policies (asynchronous).

    Policies define fine-grained access control rules that determine
    whether agents can perform specific actions on resources.
    """

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
        """Create a new policy in a workspace.

        Args:
            workspace_id: The workspace to create the policy in.
            name: Human-readable policy name.
            effect: Policy effect ('allow' or 'deny').
            principals: Agent patterns this policy applies to.
            resources: Resource patterns this policy governs.
            description: Optional policy description.
            actions: Optional list of action strings.
            conditions: Optional condition expressions.
            priority: Optional evaluation priority (higher = evaluated first).
            enabled: Whether the policy is active (defaults to True on the server).

        Returns:
            The newly created Policy.
        """
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
        """List policies in a workspace.

        Args:
            workspace_id: The workspace to list policies from.

        Returns:
            A paginated list of Policy objects.
        """
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
        """Update an existing policy. Only provided fields are modified.

        Args:
            policy_id: The unique identifier of the policy to update.
            name: New policy name.
            description: New description.
            effect: Updated effect.
            principals: Updated principal patterns.
            resources: Updated resource patterns.
            actions: Updated action list.
            conditions: Updated conditions.
            priority: Updated priority.
            enabled: Updated enabled state.

        Returns:
            The updated Policy.
        """
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
        """Delete a policy by its ID.

        Args:
            policy_id: The unique identifier of the policy to delete.
        """
        await self._http.delete(f"/policies/{policy_id}")

    async def simulate(
        self,
        *,
        workspace_id: str,
        agent_id: str,
        resource: str,
        action: str,
    ) -> PolicySimulationResult:
        """Simulate a policy evaluation without enforcing the result.

        Useful for testing policy configurations before they go live.

        Args:
            workspace_id: The workspace context.
            agent_id: The agent to simulate for.
            resource: The resource to simulate access to.
            action: The action to simulate.

        Returns:
            A PolicySimulationResult showing which policies would match.
        """
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
        """Evaluate policies for a given agent, resource, and action.

        Args:
            workspace_id: The workspace context.
            agent_id: The agent to evaluate for.
            resource: The resource to evaluate access to.
            action: The action to evaluate.

        Returns:
            A PolicyEvaluationResult.
        """
        body: Dict[str, Any] = {
            "workspace_id": workspace_id,
            "agent_id": agent_id,
            "resource": resource,
            "action": action,
        }
        data = await self._http.post("/policies/evaluate", body=body)
        return PolicyEvaluationResult.from_dict(data)

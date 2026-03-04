"""Data models for the Authora SDK.

All models are plain dataclasses with a ``from_dict`` classmethod that
gracefully ignores unknown keys returned by the API.  Field names use
snake_case; the HTTP layer handles camelCase <-> snake_case conversion.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

T = TypeVar("T")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
    """Instantiate *cls* from *data*, ignoring unknown keys."""
    known = {f.name for f in fields(cls)}  # type: ignore[arg-type]
    return cls(**{k: v for k, v in data.items() if k in known})  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Common / shared
# ---------------------------------------------------------------------------


@dataclass
class PaginatedList(Generic[T]):
    """Standard paginated list response.

    Attributes:
        items: List of result objects.
        total: Total number of matching items across all pages.
        page: Current page number (1-indexed), when available.
        limit: Maximum items per page, when available.
    """

    items: List[T]
    total: int
    page: Optional[int] = None
    limit: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any], item_cls: Type[T]) -> "PaginatedList[T]":
        """Build a PaginatedList from a raw dict, deserializing each item."""
        raw_items = data.get("items", [])
        items = [_from_dict(item_cls, i) for i in raw_items]
        return cls(
            items=items,
            total=data.get("total", len(items)),
            page=data.get("page"),
            limit=data.get("limit"),
        )


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------


@dataclass
class Agent:
    """An autonomous software entity registered with Authora.

    Attributes:
        id: Unique agent identifier.
        workspace_id: Workspace the agent belongs to.
        name: Human-readable name.
        status: Current lifecycle status.
        created_by: Identifier of the user who created the agent.
        created_at: ISO-8601 creation timestamp.
        updated_at: ISO-8601 last-update timestamp.
    """

    id: str
    workspace_id: str
    name: str
    status: str
    created_by: str
    created_at: str
    updated_at: str
    description: Optional[str] = None
    public_key: Optional[str] = None
    api_key_hash: Optional[str] = None
    expires_at: Optional[str] = None
    tags: Optional[List[str]] = None
    framework: Optional[str] = None
    model_provider: Optional[str] = None
    model_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Agent":
        return _from_dict(cls, data)


@dataclass
class AgentVerification:
    """Result of verifying an agent's identity.

    Attributes:
        valid: Whether the agent identity is valid.
        agent: The full agent object, when valid.
    """

    valid: bool
    agent: Optional[Agent] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentVerification":
        agent_data = data.get("agent")
        return cls(
            valid=data.get("valid", False),
            agent=Agent.from_dict(agent_data) if agent_data else None,
        )


# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------


@dataclass
class Role:
    """A named set of permissions that can be assigned to agents.

    Attributes:
        id: Unique role identifier.
        workspace_id: Workspace the role belongs to.
        name: Human-readable role name.
        permissions: List of allowed permission strings.
        created_at: ISO-8601 creation timestamp.
        updated_at: ISO-8601 last-update timestamp.
    """

    id: str
    workspace_id: str
    name: str
    permissions: List[str]
    created_at: str
    updated_at: str
    description: Optional[str] = None
    deny_permissions: Optional[List[str]] = None
    stage: Optional[str] = None
    max_session_duration: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Role":
        return _from_dict(cls, data)


@dataclass
class AgentRoleAssignment:
    """Record of a role assigned to an agent.

    Attributes:
        agent_id: The agent the role is assigned to.
        role_id: The role that is assigned.
        assigned_at: ISO-8601 timestamp when the assignment was created.
    """

    agent_id: str
    role_id: str
    assigned_at: str
    granted_by: Optional[str] = None
    expires_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentRoleAssignment":
        return _from_dict(cls, data)


# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------


@dataclass
class PermissionCheckResult:
    """Result of a single permission check.

    Attributes:
        allowed: Whether the action is permitted.
        reason: Human-readable explanation, if provided.
        matched_policies: IDs of policies that contributed to the decision.
    """

    allowed: bool
    reason: Optional[str] = None
    matched_policies: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PermissionCheckResult":
        return _from_dict(cls, data)


@dataclass
class BatchPermissionCheckResult:
    """Result of a batch permission check.

    Attributes:
        results: Ordered list of results corresponding to each check in the batch.
    """

    results: List[PermissionCheckResult]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BatchPermissionCheckResult":
        raw = data.get("results", [])
        return cls(results=[PermissionCheckResult.from_dict(r) for r in raw])


@dataclass
class EffectivePermission:
    """A resolved permission for an agent.

    Attributes:
        resource: The resource pattern this permission applies to.
        actions: Allowed actions on the resource.
        source: Where the permission originates from (role name, policy, etc.).
    """

    resource: str
    actions: List[str]
    source: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EffectivePermission":
        return _from_dict(cls, data)


# ---------------------------------------------------------------------------
# Delegations
# ---------------------------------------------------------------------------


@dataclass
class Delegation:
    """A permission delegation from one agent to another.

    Attributes:
        id: Unique delegation identifier.
        issuer_agent_id: The agent granting the delegation.
        target_agent_id: The agent receiving the delegation.
        permissions: List of delegated permission strings.
        status: Current delegation status (active, revoked, expired).
        created_at: ISO-8601 creation timestamp.
        updated_at: ISO-8601 last-update timestamp.
    """

    id: str
    issuer_agent_id: str
    target_agent_id: str
    permissions: List[str]
    status: str
    created_at: str
    updated_at: str
    constraints: Optional[Dict[str, Any]] = None
    expires_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Delegation":
        return _from_dict(cls, data)


@dataclass
class DelegationVerification:
    """Result of verifying a delegation.

    Attributes:
        valid: Whether the delegation is valid and active.
        delegation: The full delegation object, when valid.
    """

    valid: bool
    delegation: Optional[Delegation] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DelegationVerification":
        deleg_data = data.get("delegation")
        return cls(
            valid=data.get("valid", False),
            delegation=Delegation.from_dict(deleg_data) if deleg_data else None,
        )


# ---------------------------------------------------------------------------
# Policies
# ---------------------------------------------------------------------------


@dataclass
class Policy:
    """An authorization policy defining access control rules.

    Attributes:
        id: Unique policy identifier.
        workspace_id: Workspace the policy belongs to.
        name: Human-readable policy name.
        effect: Whether the policy allows or denies access.
        principals: Patterns matching the agents this policy applies to.
        resources: Patterns matching the resources this policy governs.
        created_at: ISO-8601 creation timestamp.
        updated_at: ISO-8601 last-update timestamp.
    """

    id: str
    workspace_id: str
    name: str
    effect: str
    principals: List[str]
    resources: List[str]
    created_at: str
    updated_at: str
    description: Optional[str] = None
    actions: Optional[List[str]] = None
    conditions: Optional[Dict[str, Any]] = None
    priority: Optional[int] = None
    enabled: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Policy":
        return _from_dict(cls, data)


@dataclass
class PolicySimulationResult:
    """Result of simulating a policy evaluation.

    Attributes:
        allowed: Whether the simulated action would be permitted.
        matched_policies: Policies that matched during simulation.
        reason: Human-readable explanation, if provided.
    """

    allowed: bool
    matched_policies: List[Dict[str, Any]] = field(default_factory=list)
    reason: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PolicySimulationResult":
        return cls(
            allowed=data.get("allowed", False),
            matched_policies=data.get("matched_policies", []),
            reason=data.get("reason"),
        )


@dataclass
class PolicyEvaluationResult:
    """Result of evaluating policies for an agent action.

    Attributes:
        allowed: Whether the action is permitted.
        effect: The final policy effect (allow or deny).
        matched_policies: IDs of policies that contributed to the decision.
        reason: Human-readable explanation, if provided.
    """

    allowed: bool
    effect: str
    matched_policies: List[str] = field(default_factory=list)
    reason: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PolicyEvaluationResult":
        return _from_dict(cls, data)


# ---------------------------------------------------------------------------
# MCP Servers
# ---------------------------------------------------------------------------


@dataclass
class McpServer:
    """A registered MCP (Model Context Protocol) server.

    Attributes:
        id: Unique server identifier.
        workspace_id: Workspace the server belongs to.
        name: Human-readable server name.
        url: Server endpoint URL.
        created_at: ISO-8601 creation timestamp.
        updated_at: ISO-8601 last-update timestamp.
    """

    id: str
    workspace_id: str
    name: str
    url: str
    created_at: str
    updated_at: str
    description: Optional[str] = None
    transport: Optional[str] = None
    version: Optional[str] = None
    auth_config: Optional[Dict[str, Any]] = None
    connection_timeout: Optional[int] = None
    max_retries: Optional[int] = None
    status: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "McpServer":
        return _from_dict(cls, data)


@dataclass
class McpTool:
    """A tool registered for an MCP server.

    Attributes:
        id: Unique tool identifier.
        server_id: The MCP server this tool belongs to.
        name: Tool name.
        created_at: ISO-8601 creation timestamp.
    """

    id: str
    server_id: str
    name: str
    created_at: str
    description: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "McpTool":
        return _from_dict(cls, data)


@dataclass
class McpProxyResponse:
    """A JSON-RPC 2.0 response from an MCP proxy call.

    Attributes:
        jsonrpc: JSON-RPC version string (always "2.0").
        result: The successful result payload, if any.
        error: The error object, if the call failed.
        id: Correlation identifier matching the request.
    """

    jsonrpc: str
    result: Any = None
    error: Optional[Dict[str, Any]] = None
    id: Any = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "McpProxyResponse":
        return _from_dict(cls, data)


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------


@dataclass
class AuditEvent:
    """A recorded audit event.

    Attributes:
        id: Unique event identifier.
        type: Event type string.
        timestamp: ISO-8601 event timestamp.
    """

    id: str
    type: str
    timestamp: str
    org_id: Optional[str] = None
    workspace_id: Optional[str] = None
    agent_id: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    result: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditEvent":
        return _from_dict(cls, data)


@dataclass
class AuditReport:
    """A generated audit report.

    Attributes:
        id: Unique report identifier.
        org_id: Organization the report covers.
        date_from: Start of the reporting period (ISO-8601).
        date_to: End of the reporting period (ISO-8601).
        generated_at: When the report was generated (ISO-8601).
    """

    id: str
    org_id: str
    date_from: str
    date_to: str
    generated_at: str
    summary: Optional[Dict[str, Any]] = None
    url: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditReport":
        return _from_dict(cls, data)


@dataclass
class AuditMetrics:
    """Aggregated audit metrics.

    Attributes:
        total_events: Total number of events in the queried period.
        events_by_type: Breakdown of events by type.
        events_by_result: Breakdown of events by result.
    """

    total_events: int
    events_by_type: Dict[str, int] = field(default_factory=dict)
    events_by_result: Dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditMetrics":
        return cls(
            total_events=data.get("total_events", 0),
            events_by_type=data.get("events_by_type", {}),
            events_by_result=data.get("events_by_result", {}),
        )


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------


@dataclass
class Notification:
    """A user notification.

    Attributes:
        id: Unique notification identifier.
        organization_id: Organization the notification belongs to.
        type: Notification type string.
        title: Short title.
        message: Notification body text.
        read: Whether the notification has been read.
        created_at: ISO-8601 creation timestamp.
    """

    id: str
    organization_id: str
    type: str
    title: str
    message: str
    read: bool
    created_at: str
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Notification":
        return _from_dict(cls, data)


@dataclass
class UnreadCountResult:
    """Result containing the unread notification count.

    Attributes:
        count: Number of unread notifications.
    """

    count: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UnreadCountResult":
        return cls(count=data.get("count", 0))


# ---------------------------------------------------------------------------
# Webhooks
# ---------------------------------------------------------------------------


@dataclass
class Webhook:
    """A webhook subscription.

    Attributes:
        id: Unique webhook identifier.
        organization_id: Organization the webhook belongs to.
        url: Delivery URL.
        event_types: Event types the webhook subscribes to.
        secret: Shared secret for signature verification.
        created_at: ISO-8601 creation timestamp.
        updated_at: ISO-8601 last-update timestamp.
    """

    id: str
    organization_id: str
    url: str
    event_types: List[str]
    secret: str
    created_at: str
    updated_at: str
    enabled: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Webhook":
        return _from_dict(cls, data)


# ---------------------------------------------------------------------------
# Alerts
# ---------------------------------------------------------------------------


@dataclass
class Alert:
    """An alert rule.

    Attributes:
        id: Unique alert identifier.
        organization_id: Organization the alert belongs to.
        name: Human-readable alert name.
        event_types: Event types that trigger the alert.
        conditions: Conditions that must be met for the alert to fire.
        channels: Delivery channels for the alert.
        created_at: ISO-8601 creation timestamp.
        updated_at: ISO-8601 last-update timestamp.
    """

    id: str
    organization_id: str
    name: str
    event_types: List[str]
    conditions: Dict[str, Any]
    channels: List[Dict[str, Any]]
    created_at: str
    updated_at: str
    enabled: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Alert":
        return _from_dict(cls, data)


# ---------------------------------------------------------------------------
# API Keys
# ---------------------------------------------------------------------------


@dataclass
class ApiKey:
    """An API key for programmatic access.

    Attributes:
        id: Unique key identifier.
        organization_id: Organization the key belongs to.
        name: Human-readable key name.
        created_by: Identifier of the user who created the key.
        created_at: ISO-8601 creation timestamp.
    """

    id: str
    organization_id: str
    name: str
    created_by: str
    created_at: str
    key: Optional[str] = None
    key_prefix: Optional[str] = None
    scopes: Optional[List[str]] = None
    expires_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ApiKey":
        return _from_dict(cls, data)


# ---------------------------------------------------------------------------
# Organizations
# ---------------------------------------------------------------------------


@dataclass
class Organization:
    """A top-level organization.

    Attributes:
        id: Unique organization identifier.
        name: Organization name.
        slug: URL-safe slug.
        created_at: ISO-8601 creation timestamp.
        updated_at: ISO-8601 last-update timestamp.
    """

    id: str
    name: str
    slug: str
    created_at: str
    updated_at: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Organization":
        return _from_dict(cls, data)


# ---------------------------------------------------------------------------
# Workspaces
# ---------------------------------------------------------------------------


@dataclass
class Workspace:
    """A workspace within an organization.

    Attributes:
        id: Unique workspace identifier.
        organization_id: Parent organization identifier.
        name: Workspace name.
        slug: URL-safe slug.
        created_at: ISO-8601 creation timestamp.
        updated_at: ISO-8601 last-update timestamp.
    """

    id: str
    organization_id: str
    name: str
    slug: str
    created_at: str
    updated_at: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Workspace":
        return _from_dict(cls, data)

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

T = TypeVar("T")


def _from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
    known = {f.name for f in fields(cls)}  # type: ignore[arg-type]
    return cls(**{k: v for k, v in data.items() if k in known})  # type: ignore[return-value]


@dataclass
class PaginatedList(Generic[T]):
    items: List[T]
    total: int
    page: Optional[int] = None
    limit: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any], item_cls: Type[T]) -> "PaginatedList[T]":
        raw_items = data.get("items", [])
        items = [_from_dict(item_cls, i) for i in raw_items]
        return cls(
            items=items,
            total=data.get("total", len(items)),
            page=data.get("page"),
            limit=data.get("limit"),
        )


@dataclass
class Agent:
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
    valid: bool
    agent: Optional[Agent] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentVerification":
        agent_data = data.get("agent")
        return cls(
            valid=data.get("valid", False),
            agent=Agent.from_dict(agent_data) if agent_data else None,
        )


@dataclass
class Role:
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
    is_builtin: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Role":
        return _from_dict(cls, data)


@dataclass
class AgentRoleAssignment:
    agent_id: str
    role_id: str
    assigned_at: str
    granted_by: Optional[str] = None
    expires_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentRoleAssignment":
        return _from_dict(cls, data)


@dataclass
class PermissionCheckResult:
    allowed: bool
    reason: Optional[str] = None
    matched_policies: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PermissionCheckResult":
        return _from_dict(cls, data)


@dataclass
class BatchPermissionCheckResult:
    results: List[PermissionCheckResult]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BatchPermissionCheckResult":
        raw = data.get("results", [])
        return cls(results=[PermissionCheckResult.from_dict(r) for r in raw])


@dataclass
class EffectivePermission:
    resource: str
    actions: List[str]
    source: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EffectivePermission":
        return _from_dict(cls, data)


@dataclass
class Delegation:
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
    valid: bool
    delegation: Optional[Delegation] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DelegationVerification":
        deleg_data = data.get("delegation")
        return cls(
            valid=data.get("valid", False),
            delegation=Delegation.from_dict(deleg_data) if deleg_data else None,
        )


@dataclass
class PolicyPrincipals:
    roles: Optional[List[str]] = None
    agents: Optional[List[str]] = None
    workspaces: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, data: Any) -> "PolicyPrincipals":
        if isinstance(data, dict):
            return cls(
                roles=data.get("roles"),
                agents=data.get("agents"),
                workspaces=data.get("workspaces"),
            )
        return cls()


@dataclass
class Policy:
    id: str
    workspace_id: str
    name: str
    effect: str
    principals: PolicyPrincipals
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
        raw_principals = data.get("principals", {})
        principals = PolicyPrincipals.from_dict(raw_principals)
        known = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in data.items() if k in known and k != "principals"}
        return cls(principals=principals, **filtered)


@dataclass
class PolicySimulationResult:
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
    allowed: Optional[bool] = None
    effect: Optional[str] = None
    matched_policies: List[str] = field(default_factory=list)
    reason: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PolicyEvaluationResult":
        return _from_dict(cls, data)


@dataclass
class McpServer:
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
    id: str
    name: str
    created_at: str
    server_id: Optional[str] = None
    mcp_server_id: Optional[str] = None
    description: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "McpTool":
        obj = _from_dict(cls, data)
        if obj.server_id is None and obj.mcp_server_id is not None:
            object.__setattr__(obj, "server_id", obj.mcp_server_id)
        return obj


@dataclass
class McpProxyResponse:
    jsonrpc: str
    result: Any = None
    error: Optional[Dict[str, Any]] = None
    id: Any = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "McpProxyResponse":
        return _from_dict(cls, data)


@dataclass
class AuditEvent:
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


@dataclass
class Notification:
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
    count: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UnreadCountResult":
        return cls(count=data.get("count", 0))


@dataclass
class Webhook:
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


@dataclass
class Alert:
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


@dataclass
class ApiKey:
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


@dataclass
class Organization:
    id: str
    name: str
    slug: str
    created_at: str
    updated_at: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Organization":
        return _from_dict(cls, data)


@dataclass
class Workspace:
    id: str
    organization_id: str
    name: str
    slug: str
    created_at: str
    updated_at: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Workspace":
        return _from_dict(cls, data)


@dataclass
class KeyPair:
    private_key: str
    public_key: str


@dataclass
class EffectivePermissions:
    agent_id: str
    permissions: List[str]
    deny_permissions: List[str]


@dataclass
class DelegationConstraints:
    max_depth: Optional[int] = None
    expires_at: Optional[str] = None
    single_use: Optional[bool] = None
    allowed_targets: Optional[List[str]] = None


@dataclass
class CreateAgentResult:
    agent: Agent
    key_pair: KeyPair


@dataclass
class McpToolContext:
    agent_id: str
    timestamp: str
    delegation_token: Optional[str] = None
    verified: bool = False

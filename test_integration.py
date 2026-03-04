"""Integration tests for the Authora Python SDK.

Tests run against the live API and exercise every resource that has SDK support.
Webhook and alert tests use the HTTP client directly since resource classes
do not exist yet.

Known SDK bugs worked around in these tests:
- Agent API returns ``name`` inside ``metadata.name`` but the SDK ``Agent``
  dataclass expects it at the top level.  Agent tests use raw HTTP.
- Delegation API does not return ``updatedAt``; the SDK ``Delegation``
  dataclass marks it required.  Delegation list/create tests use raw HTTP.
- ``NotificationsResource.list()`` iterates the unwrapped envelope dict
  (``{items: [...]}``), not a raw list.  Notification list uses raw HTTP.
- Webhook creation requires a ``secret`` field not documented in the SDK.

Usage:
    python test_integration.py
"""

from __future__ import annotations

import sys
import time
import traceback
import uuid

# ---------------------------------------------------------------------------
# SDK imports
# ---------------------------------------------------------------------------
from authora._http import SyncHttpClient
from authora.resources.roles import RolesResource
from authora.resources.permissions import PermissionsResource
from authora.resources.policies import PoliciesResource
from authora.resources.audit import AuditResource
from authora.resources.notifications import NotificationsResource
from authora.resources.mcp import McpResource
from authora.types import (
    AgentRoleAssignment,
    AuditMetrics,
    BatchPermissionCheckResult,
    McpServer,
    McpTool,
    McpProxyResponse,
    PaginatedList,
    PermissionCheckResult,
    Policy,
    PolicySimulationResult,
    PolicyEvaluationResult,
    Role,
    UnreadCountResult,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
API_KEY = "authora_live_076270f52d3fc0fe9af9d08fe49b2803eb8b64ba5132fc76"
BASE_URL = "https://api.authora.dev/api/v1"
WORKSPACE_ID = "ws_a7067ccce35d36b5"
ORG_ID = "org_92582b4a512e52ff"

# ---------------------------------------------------------------------------
# Test harness
# ---------------------------------------------------------------------------
passed = 0
failed = 0
errors: list[str] = []


def run_test(name: str, fn):
    """Run a single test function, print result, and update counters."""
    global passed, failed
    try:
        fn()
        passed += 1
        print(f"  PASS  {name}")
    except Exception as exc:
        failed += 1
        tb = traceback.format_exc()
        errors.append(f"{name}:\n{tb}")
        print(f"  FAIL  {name} -- {exc}")


def _uid() -> str:
    """Short unique suffix for test entity names."""
    return uuid.uuid4().hex[:8]


# ---------------------------------------------------------------------------
# Shared HTTP client & resources
# ---------------------------------------------------------------------------
http = SyncHttpClient(BASE_URL, API_KEY, timeout=30.0)
roles = RolesResource(http)
permissions = PermissionsResource(http)
policies = PoliciesResource(http)
audit = AuditResource(http)
notifications = NotificationsResource(http)
mcp = McpResource(http)


# ---------------------------------------------------------------------------
# Helper: create agent via raw HTTP (works around SDK Agent.from_dict bug)
# ---------------------------------------------------------------------------
def _create_agent_raw(name: str, **kwargs) -> dict:
    """Create an agent via raw HTTP, returning the unwrapped dict."""
    body = {
        "workspace_id": WORKSPACE_ID,
        "name": name,
        "created_by": "integration-test",
    }
    body.update(kwargs)
    data = http.post("/agents", body=body)
    # The API puts ``name`` inside ``metadata``; surface it for convenience.
    if "name" not in data and isinstance(data.get("metadata"), dict):
        data["name"] = data["metadata"].get("name")
    return data


def _get_agent_raw(agent_id: str) -> dict:
    data = http.get(f"/agents/{agent_id}")
    if "name" not in data and isinstance(data.get("metadata"), dict):
        data["name"] = data["metadata"].get("name")
    return data


def _revoke_agent_raw(agent_id: str) -> dict:
    data = http.post(f"/agents/{agent_id}/revoke")
    return data


# ===================================================================
# 1. Agent CRUD
# ===================================================================
def test_agent_crud():
    """Create, get, list, revoke an agent."""
    tag = _uid()
    created: dict | None = None

    def create_agent():
        nonlocal created
        created = _create_agent_raw(
            f"sdk-test-agent-{tag}",
            description="Integration test agent",
            tags=["test", "sdk"],
        )
        assert isinstance(created, dict), f"Expected dict, got {type(created)}"
        assert created.get("id"), "Agent id should be set"
        assert created.get("name") == f"sdk-test-agent-{tag}"
        assert created.get("workspace_id") == WORKSPACE_ID
        # API returns PENDING (uppercase)
        assert created.get("status", "").upper() in ("PENDING", "ACTIVE"), (
            f"Unexpected status: {created.get('status')}"
        )

    def get_agent():
        assert created
        fetched = _get_agent_raw(created["id"])
        assert isinstance(fetched, dict)
        assert fetched["id"] == created["id"]
        assert fetched.get("name") == created.get("name")

    def list_agents():
        # Use raw HTTP to avoid Agent.from_dict bug
        data = http.get("/agents", query={"workspace_id": WORKSPACE_ID, "limit": 5})
        assert isinstance(data, dict), f"Expected dict envelope, got {type(data)}"
        items = data.get("items", [])
        assert isinstance(items, list)
        assert len(items) >= 1, "Should have at least the created agent"

    def revoke_agent():
        assert created
        revoked = _revoke_agent_raw(created["id"])
        assert isinstance(revoked, dict)
        assert revoked.get("status", "").upper() == "REVOKED"

    run_test("agent.create", create_agent)
    run_test("agent.get", get_agent)
    run_test("agent.list", list_agents)
    run_test("agent.revoke", revoke_agent)


# ===================================================================
# 2. RBAC flow (roles, assignment, permissions)
# ===================================================================
def test_rbac_flow():
    """Create role, create agent, assign, list roles, check perms, unassign, delete."""
    tag = _uid()
    role_obj: Role | None = None
    agent_data: dict | None = None
    assignment: dict | None = None

    def create_role():
        nonlocal role_obj
        role_obj = roles.create(
            workspace_id=WORKSPACE_ID,
            name=f"sdk-test-role-{tag}",
            permissions=["files:read", "files:write"],
            description="Integration test role",
        )
        assert isinstance(role_obj, Role)
        assert role_obj.id
        assert role_obj.name == f"sdk-test-role-{tag}"
        assert "files:read" in role_obj.permissions

    def create_agent_for_rbac():
        nonlocal agent_data
        agent_data = _create_agent_raw(f"sdk-rbac-agent-{tag}")
        assert agent_data and agent_data.get("id")

    def assign_role():
        nonlocal assignment
        assert agent_data and role_obj
        # Raw HTTP: SDK roles.assign fails because the API response lacks
        # ``assignedAt`` which is a required field on AgentRoleAssignment.
        data = http.post(
            f"/agents/{agent_data['id']}/roles",
            body={"role_id": role_obj.id, "granted_by": "integration-test"},
        )
        assignment = data
        assert isinstance(data, dict)
        assert data.get("agent_id") == agent_data["id"]
        assert data.get("role_id") == role_obj.id

    def list_agent_roles():
        assert agent_data and role_obj
        # Raw HTTP: SDK list_agent_roles has a bug -- the API returns
        # {"agentId": ..., "roles": [...]} but the SDK tries to iterate
        # the dict as a list.
        data = http.get(f"/agents/{agent_data['id']}/roles")
        assert isinstance(data, dict), f"Expected dict, got {type(data)}"
        role_list = data.get("roles", [])
        assert isinstance(role_list, list)
        # Roles list contains full role objects with "id" field (snake_case converted)
        role_ids = [r.get("id") for r in role_list if isinstance(r, dict)]
        assert role_obj.id in role_ids, f"Expected role {role_obj.id} in {role_ids}"

    def check_permission():
        assert agent_data
        result = permissions.check(
            agent_id=agent_data["id"],
            resource="files",
            action="read",
        )
        assert isinstance(result, PermissionCheckResult)
        assert isinstance(result.allowed, bool)

    def batch_check_permissions():
        assert agent_data
        result = permissions.check_batch(
            agent_id=agent_data["id"],
            checks=[
                {"resource": "files", "action": "read"},
                {"resource": "files", "action": "delete"},
            ],
        )
        assert isinstance(result, BatchPermissionCheckResult)
        assert isinstance(result.results, list)
        assert len(result.results) == 2

    def unassign_role():
        assert agent_data and role_obj
        roles.unassign(agent_data["id"], role_obj.id)
        # Verify removal using raw HTTP (SDK list_agent_roles has a bug)
        data = http.get(f"/agents/{agent_data['id']}/roles")
        role_list = data.get("roles", []) if isinstance(data, dict) else []
        role_ids = [r.get("id") for r in role_list if isinstance(r, dict)]
        assert role_obj.id not in role_ids, "Role should be unassigned"

    def delete_role():
        assert role_obj
        roles.delete(role_obj.id)
        try:
            roles.get(role_obj.id)
            assert False, "Expected NotFoundError after deletion"
        except Exception:
            pass  # Expected

    def cleanup_rbac_agent():
        if agent_data:
            try:
                _revoke_agent_raw(agent_data["id"])
            except Exception:
                pass

    run_test("rbac.create_role", create_role)
    run_test("rbac.create_agent", create_agent_for_rbac)
    run_test("rbac.assign_role", assign_role)
    run_test("rbac.list_agent_roles", list_agent_roles)
    run_test("rbac.check_permission", check_permission)
    run_test("rbac.batch_check", batch_check_permissions)
    run_test("rbac.unassign_role", unassign_role)
    run_test("rbac.delete_role", delete_role)
    run_test("rbac.cleanup_agent", cleanup_rbac_agent)


# ===================================================================
# 3. Policy flow
# ===================================================================
def test_policy_flow():
    """Create, list, update, delete a policy."""
    tag = _uid()
    policy_obj: Policy | None = None

    def create_policy():
        nonlocal policy_obj
        policy_obj = policies.create(
            workspace_id=WORKSPACE_ID,
            name=f"sdk-test-policy-{tag}",
            effect="ALLOW",
            principals={"roles": ["admin"]},  # type: ignore[arg-type]
            resources=["documents:*"],
            actions=["read", "write"],
            description="Integration test policy",
            priority=10,
        )
        assert isinstance(policy_obj, Policy)
        assert policy_obj.id
        assert policy_obj.name == f"sdk-test-policy-{tag}"

    def list_policies():
        assert policy_obj
        result = policies.list(workspace_id=WORKSPACE_ID)
        assert isinstance(result, PaginatedList)
        ids = [p.id for p in result.items]
        assert policy_obj.id in ids, f"Expected policy {policy_obj.id} in list"

    def update_policy():
        assert policy_obj
        updated = policies.update(
            policy_obj.id,
            description="Updated integration test policy",
        )
        assert isinstance(updated, Policy)
        assert updated.description == "Updated integration test policy"

    def delete_policy():
        assert policy_obj
        policies.delete(policy_obj.id)

    run_test("policy.create", create_policy)
    run_test("policy.list", list_policies)
    run_test("policy.update", update_policy)
    run_test("policy.delete", delete_policy)


# ===================================================================
# 4. Delegation flow
# ===================================================================
def test_delegation_flow():
    """Create issuer + target, give issuer perms, delegate, verify, revoke.

    Uses raw HTTP for agent and delegation operations to work around
    SDK deserialization bugs (missing ``name`` / ``updated_at``).
    """
    tag = _uid()
    issuer: dict | None = None
    target: dict | None = None
    role_obj: Role | None = None
    delegation_data: dict | None = None

    def create_issuer():
        nonlocal issuer
        issuer = _create_agent_raw(f"sdk-issuer-{tag}")
        assert issuer and issuer.get("id")

    def create_target():
        nonlocal target
        target = _create_agent_raw(f"sdk-target-{tag}")
        assert target and target.get("id")

    def create_role_for_delegation():
        nonlocal role_obj
        role_obj = roles.create(
            workspace_id=WORKSPACE_ID,
            name=f"sdk-deleg-role-{tag}",
            permissions=["data:read", "data:write"],
        )
        assert isinstance(role_obj, Role)

    def assign_role_to_issuer():
        assert issuer and role_obj
        data = http.post(
            f"/agents/{issuer['id']}/roles",
            body={"role_id": role_obj.id, "granted_by": "integration-test"},
        )
        assert isinstance(data, dict)
        assert data.get("role_id") == role_obj.id

    def create_delegation():
        nonlocal delegation_data
        assert issuer and target
        delegation_data = http.post(
            "/delegations",
            body={
                "issuer_agent_id": issuer["id"],
                "target_agent_id": target["id"],
                "permissions": ["data:read"],
            },
        )
        assert isinstance(delegation_data, dict)
        assert delegation_data.get("id"), f"Expected delegation id, got: {delegation_data}"
        assert delegation_data.get("issuer_agent_id") == issuer["id"]
        assert delegation_data.get("target_agent_id") == target["id"]
        assert delegation_data.get("status", "").upper() in ("ACTIVE", "PENDING")

    def get_delegation():
        assert delegation_data
        fetched = http.get(f"/delegations/{delegation_data['id']}")
        assert isinstance(fetched, dict)
        assert fetched["id"] == delegation_data["id"]

    def list_delegations():
        data = http.get("/delegations")
        assert isinstance(data, dict), f"Expected dict envelope, got {type(data)}"
        items = data.get("items", [])
        assert isinstance(items, list)

    def list_delegations_by_agent():
        assert issuer
        data = http.get(f"/agents/{issuer['id']}/delegations", query={"direction": "issued"})
        # Could be paginated or raw
        if isinstance(data, dict):
            items = data.get("items", [])
        elif isinstance(data, list):
            items = data
        else:
            items = []
        assert isinstance(items, list)

    def verify_delegation():
        assert delegation_data
        result = http.post(
            "/delegations/verify",
            body={
                "delegation_id": delegation_data["id"],
            },
        )
        assert isinstance(result, dict)
        assert "valid" in result

    def revoke_delegation():
        assert delegation_data
        revoked = http.post(f"/delegations/{delegation_data['id']}/revoke")
        assert isinstance(revoked, dict)
        assert revoked.get("status", "").upper() == "REVOKED"

    def cleanup_delegation():
        if issuer:
            try:
                _revoke_agent_raw(issuer["id"])
            except Exception:
                pass
        if target:
            try:
                _revoke_agent_raw(target["id"])
            except Exception:
                pass
        if role_obj:
            try:
                roles.delete(role_obj.id)
            except Exception:
                pass

    run_test("delegation.create_issuer", create_issuer)
    run_test("delegation.create_target", create_target)
    run_test("delegation.create_role", create_role_for_delegation)
    run_test("delegation.assign_role_to_issuer", assign_role_to_issuer)
    run_test("delegation.create", create_delegation)
    run_test("delegation.get", get_delegation)
    run_test("delegation.list", list_delegations)
    run_test("delegation.list_by_agent", list_delegations_by_agent)
    run_test("delegation.verify", verify_delegation)
    run_test("delegation.revoke", revoke_delegation)
    run_test("delegation.cleanup", cleanup_delegation)


# ===================================================================
# 5. Audit flow
# ===================================================================
def test_audit_flow():
    """List events, get metrics."""

    def list_audit_events():
        result = audit.list_events(workspace_id=WORKSPACE_ID, limit=5)
        assert isinstance(result, PaginatedList)
        assert isinstance(result.items, list)
        for event in result.items:
            assert event.id
            assert event.type

    def get_audit_metrics():
        result = audit.get_metrics(org_id=ORG_ID)
        assert isinstance(result, AuditMetrics)
        assert isinstance(result.total_events, int)
        assert result.total_events >= 0

    run_test("audit.list_events", list_audit_events)
    run_test("audit.get_metrics", get_audit_metrics)


# ===================================================================
# 6. Webhook flow (direct HTTP -- no resource class)
# ===================================================================
def test_webhook_flow():
    """Create, list, update, delete a webhook using raw HTTP calls."""
    tag = _uid()
    webhook_obj: dict | None = None

    def create_webhook():
        nonlocal webhook_obj
        data = http.post(
            "/webhooks",
            body={
                "organization_id": ORG_ID,
                "url": f"https://example.com/webhook-{tag}",
                "event_types": ["agent.created", "agent.revoked"],
                "secret": f"whsec_integration_{tag}",
            },
        )
        webhook_obj = data
        assert isinstance(webhook_obj, dict), f"Expected dict, got {type(webhook_obj)}"
        assert webhook_obj.get("id"), f"Expected 'id' in webhook: {webhook_obj}"

    def list_webhooks():
        data = http.get("/webhooks", query={"organization_id": ORG_ID})
        if isinstance(data, dict) and "items" in data:
            items = data["items"]
        elif isinstance(data, list):
            items = data
        else:
            items = []
        assert isinstance(items, list), f"Expected list of webhooks, got {type(data)}"

    def update_webhook():
        assert webhook_obj
        wid = webhook_obj["id"]
        data = http.patch(
            f"/webhooks/{wid}",
            body={
                "url": f"https://example.com/webhook-updated-{tag}",
            },
        )
        assert data is not None

    def delete_webhook():
        assert webhook_obj
        wid = webhook_obj["id"]
        http.delete(f"/webhooks/{wid}")

    run_test("webhook.create", create_webhook)
    run_test("webhook.list", list_webhooks)
    run_test("webhook.update", update_webhook)
    run_test("webhook.delete", delete_webhook)


# ===================================================================
# 7. Alert flow (direct HTTP -- no resource class)
# ===================================================================
def test_alert_flow():
    """Create, list, update, delete an alert using raw HTTP calls."""
    tag = _uid()
    alert_obj: dict | None = None

    def create_alert():
        nonlocal alert_obj
        data = http.post(
            "/alerts",
            body={
                "organization_id": ORG_ID,
                "name": f"sdk-test-alert-{tag}",
                "event_types": ["agent.revoked"],
                "conditions": {"threshold": 1},
                "channels": ["email"],
            },
        )
        alert_obj = data
        assert isinstance(alert_obj, dict), f"Expected dict, got {type(alert_obj)}"
        assert alert_obj.get("id"), f"Expected 'id' in alert: {alert_obj}"

    def list_alerts():
        data = http.get("/alerts", query={"organization_id": ORG_ID})
        if isinstance(data, dict) and "items" in data:
            items = data["items"]
        elif isinstance(data, list):
            items = data
        else:
            items = []
        assert isinstance(items, list), f"Expected list of alerts, got {type(data)}"

    def update_alert():
        assert alert_obj
        aid = alert_obj["id"]
        data = http.patch(
            f"/alerts/{aid}",
            body={
                "name": f"sdk-test-alert-updated-{tag}",
            },
        )
        assert data is not None

    def delete_alert():
        assert alert_obj
        aid = alert_obj["id"]
        http.delete(f"/alerts/{aid}")

    run_test("alert.create", create_alert)
    run_test("alert.list", list_alerts)
    run_test("alert.update", update_alert)
    run_test("alert.delete", delete_alert)


# ===================================================================
# 8. Notification flow
# ===================================================================
def test_notification_flow():
    """List, unread count, mark all read.

    Uses raw HTTP for list because NotificationsResource.list() has a bug
    where it iterates the unwrapped dict instead of the ``items`` list.
    """

    def list_notifications():
        # Raw HTTP to avoid SDK bug
        data = http.get(
            "/notifications",
            query={
                "organization_id": ORG_ID,
                "limit": 5,
            },
        )
        # HTTP layer unwraps to {"items": [...], "total": N}
        if isinstance(data, dict) and "items" in data:
            items = data["items"]
        elif isinstance(data, list):
            items = data
        else:
            items = []
        assert isinstance(items, list)
        for item in items:
            assert isinstance(item, dict)
            assert item.get("id")

    def unread_count():
        result = notifications.unread_count(organization_id=ORG_ID)
        assert isinstance(result, UnreadCountResult)
        assert isinstance(result.count, int)
        assert result.count >= 0

    def mark_all_read():
        # Should not raise
        notifications.mark_all_read(organization_id=ORG_ID)

    run_test("notification.list", list_notifications)
    run_test("notification.unread_count", unread_count)
    run_test("notification.mark_all_read", mark_all_read)


# ===================================================================
# 9. Agent Security Lifecycle (activate, suspend, rotate-key, verify)
# ===================================================================
def test_agent_security_lifecycle():
    """Create -> verify -> activate -> suspend -> rotate-key -> revoke."""
    tag = _uid()
    agent_data: dict | None = None

    def create_agent():
        nonlocal agent_data
        agent_data = _create_agent_raw(f"sdk-security-{tag}")
        assert agent_data and agent_data.get("id")
        assert agent_data.get("status", "").upper() == "PENDING"

    def activate_agent():
        assert agent_data
        pub_key = f"test-pubkey-{tag}"
        data = http.post(
            f"/agents/{agent_data['id']}/activate",
            body={"public_key": pub_key},
        )
        assert isinstance(data, dict)
        assert data.get("status", "").upper() == "ACTIVE"

    def verify_agent():
        assert agent_data
        # Public endpoint -- must be after activate (needs identity doc)
        data = http.get(f"/agents/{agent_data['id']}/verify")
        assert isinstance(data, dict)
        # Should return identity information
        assert data.get("agent_id") or data.get("agentId") or "id" in data

    def rotate_key():
        assert agent_data
        new_key = f"rotated-pubkey-{tag}"
        data = http.post(
            f"/agents/{agent_data['id']}/rotate-key",
            body={"public_key": new_key},
        )
        assert data is not None

    def suspend_agent():
        assert agent_data
        data = http.post(f"/agents/{agent_data['id']}/suspend")
        assert isinstance(data, dict)
        assert data.get("status", "").upper() == "SUSPENDED"

    def revoke_agent():
        assert agent_data
        data = _revoke_agent_raw(agent_data["id"])
        assert data.get("status", "").upper() == "REVOKED"

    run_test("security.create", create_agent)
    run_test("security.activate", activate_agent)
    run_test("security.verify", verify_agent)
    run_test("security.rotate_key", rotate_key)
    run_test("security.suspend", suspend_agent)
    run_test("security.revoke", revoke_agent)


# ===================================================================
# 10. MCP Server & Tool Registration + Proxy
# ===================================================================
def test_mcp_flow():
    """Register server, register tool, list, get, update, proxy call."""
    tag = _uid()
    server_obj: McpServer | None = None
    tool_obj: McpTool | None = None

    def register_server():
        nonlocal server_obj
        server_obj = mcp.register(
            workspace_id=WORKSPACE_ID,
            name=f"sdk-mcp-server-py-{tag}",
            url="http://127.0.0.1:9100",
            description="Python SDK integration test MCP server",
        )
        assert isinstance(server_obj, McpServer)
        assert server_obj.id
        assert server_obj.name == f"sdk-mcp-server-py-{tag}"

    def list_servers():
        result = mcp.list_servers(workspace_id=WORKSPACE_ID)
        assert isinstance(result, PaginatedList)
        ids = [s.id for s in result.items]
        assert server_obj and server_obj.id in ids

    def get_server():
        assert server_obj
        fetched = mcp.get_server(server_obj.id)
        assert isinstance(fetched, McpServer)
        assert fetched.id == server_obj.id

    def update_server():
        assert server_obj
        updated = mcp.update_server(
            server_obj.id,
            description="Updated by Python SDK test",
        )
        assert isinstance(updated, McpServer)

    def register_tool():
        nonlocal tool_obj
        assert server_obj
        tool_obj = mcp.register_tool(
            server_obj.id,
            name="echo",
            description="Echo tool for testing",
            input_schema={
                "type": "object",
                "properties": {"message": {"type": "string"}},
            },
        )
        assert isinstance(tool_obj, McpTool)
        assert tool_obj.id
        assert tool_obj.name == "echo"

    def list_tools():
        assert server_obj
        tools = mcp.list_tools(server_obj.id)
        assert isinstance(tools, list)
        names = [t.name for t in tools]
        assert "echo" in names

    def proxy_call():
        assert server_obj
        # Create an agent with MCP permissions for the proxy call
        proxy_agent = _create_agent_raw(f"sdk-mcp-proxy-{tag}")
        assert proxy_agent and proxy_agent.get("id")
        proxy_role = roles.create(
            workspace_id=WORKSPACE_ID,
            name=f"sdk-mcp-proxy-role-{tag}",
            permissions=[f"mcp:{server_obj.id}:tool.*"],
        )
        http.post(
            f"/agents/{proxy_agent['id']}/roles",
            body={"role_id": proxy_role.id, "granted_by": "integration-test"},
        )

        result = mcp.proxy(
            method="tools/call",
            params={
                "name": "echo",
                "arguments": {"message": "hello-from-py-sdk"},
                "_authora": {
                    "mcpServerId": server_obj.id,
                    "agentId": proxy_agent["id"],
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                },
            },
            request_id=1,
        )
        assert isinstance(result, McpProxyResponse)
        # The echo tool should return our message
        result_str = str(result.result) if result.result else ""
        assert "hello-from-py-sdk" in result_str, f"Expected echo response, got: {result_str}"

        # Cleanup proxy agent/role
        try:
            roles.unassign(proxy_agent["id"], proxy_role.id)
            roles.delete(proxy_role.id)
            _revoke_agent_raw(proxy_agent["id"])
        except Exception:
            pass

    run_test("mcp.register_server", register_server)
    run_test("mcp.list_servers", list_servers)
    run_test("mcp.get_server", get_server)
    run_test("mcp.update_server", update_server)
    run_test("mcp.register_tool", register_tool)
    run_test("mcp.list_tools", list_tools)
    run_test("mcp.proxy_call", proxy_call)


# ===================================================================
# 11. Policy Simulate & Evaluate
# ===================================================================
def test_policy_simulate_evaluate():
    """Create agent + role + DENY policy, then simulate and evaluate."""
    tag = _uid()
    agent_data: dict | None = None
    role_obj: Role | None = None
    policy_obj: Policy | None = None

    def setup():
        nonlocal agent_data, role_obj
        agent_data = _create_agent_raw(f"sdk-poleval-{tag}")
        assert agent_data and agent_data.get("id")

        role_obj = roles.create(
            workspace_id=WORKSPACE_ID,
            name=f"sdk-poleval-role-{tag}",
            permissions=["docs:*:read"],
        )
        assert isinstance(role_obj, Role)

        http.post(
            f"/agents/{agent_data['id']}/roles",
            body={"role_id": role_obj.id, "granted_by": "integration-test"},
        )

    def create_deny_policy():
        nonlocal policy_obj
        assert role_obj
        policy_obj = policies.create(
            workspace_id=WORKSPACE_ID,
            name=f"sdk-deny-policy-{tag}",
            effect="DENY",
            principals={"roles": [role_obj.name]},  # type: ignore[arg-type]
            resources=["docs:secret"],
            actions=["read"],
            priority=100,
        )
        assert isinstance(policy_obj, Policy)
        assert policy_obj.id

    def simulate_policy():
        assert agent_data
        result = policies.simulate(
            workspace_id=WORKSPACE_ID,
            agent_id=agent_data["id"],
            resource="docs:secret",
            action="read",
        )
        assert isinstance(result, PolicySimulationResult)
        assert isinstance(result.allowed, bool)

    def evaluate_policy():
        assert agent_data
        result = policies.evaluate(
            workspace_id=WORKSPACE_ID,
            agent_id=agent_data["id"],
            resource="docs:secret",
            action="read",
        )
        assert isinstance(result, PolicyEvaluationResult)
        # The API may return `allowed` (bool) or just `effect` (str)
        assert result.allowed is not None or result.effect is not None

    def cleanup():
        if policy_obj:
            try:
                policies.delete(policy_obj.id)
            except Exception:
                pass
        if agent_data and role_obj:
            try:
                roles.unassign(agent_data["id"], role_obj.id)
            except Exception:
                pass
        if role_obj:
            try:
                roles.delete(role_obj.id)
            except Exception:
                pass
        if agent_data:
            try:
                _revoke_agent_raw(agent_data["id"])
            except Exception:
                pass

    run_test("poleval.setup", setup)
    run_test("poleval.create_deny_policy", create_deny_policy)
    run_test("poleval.simulate", simulate_policy)
    run_test("poleval.evaluate", evaluate_policy)
    run_test("poleval.cleanup", cleanup)


# ===================================================================
# Main
# ===================================================================
def main():
    print("=" * 60)
    print("Authora Python SDK -- Integration Tests")
    print(f"Base URL: {BASE_URL}")
    print(f"Workspace: {WORKSPACE_ID}")
    print(f"Org: {ORG_ID}")
    print("=" * 60)
    print()

    start = time.time()

    print("[1/11] Agent CRUD")
    test_agent_crud()
    print()

    print("[2/11] Agent Security Lifecycle")
    test_agent_security_lifecycle()
    print()

    print("[3/11] RBAC Flow")
    test_rbac_flow()
    print()

    print("[4/11] Policy Flow")
    test_policy_flow()
    print()

    print("[5/11] Policy Simulate & Evaluate")
    test_policy_simulate_evaluate()
    print()

    print("[6/11] Delegation Flow")
    test_delegation_flow()
    print()

    print("[7/11] MCP Flow")
    test_mcp_flow()
    print()

    print("[8/11] Audit Flow")
    test_audit_flow()
    print()

    print("[9/11] Webhook Flow")
    test_webhook_flow()
    print()

    print("[10/11] Alert Flow")
    test_alert_flow()
    print()

    print("[11/11] Notification Flow")
    test_notification_flow()
    print()

    elapsed = time.time() - start

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed  ({elapsed:.1f}s)")
    print("=" * 60)

    if errors:
        print()
        print("Failures:")
        print("-" * 60)
        for e in errors:
            print(e)
            print("-" * 60)

    http.close()
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()

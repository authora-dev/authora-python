# authora

Authorization for AI agents -- identity, permissions, and delegation management.

## Quick Start

```python
# pip install authora
from authora import AuthoraClient

client = AuthoraClient(api_key="authora_live_...")

# Create an agent
agent = client.agents.create(
    workspace_id="ws_...", name="my-agent", created_by="usr_...",
)

# Check a permission
result = client.permissions.check(
    agent_id="agt_abc", resource="files:reports/*", action="read",
)
if result.allowed:
    print("Access granted")
```

## Installation

```bash
pip install authora
```

## Getting Credentials

**Automatic (IDE agents):** If you use Claude Code, Cursor, or OpenCode, credentials are created automatically on first run via browser sign-in. See [self-onboarding instructions](https://authora.dev/llms-onboard.txt).

**Manual:** Sign up at [authora.dev/get-started](https://authora.dev/get-started), then find your credentials:

| Value | Format | Where to find it |
|---|---|---|
| **API Key** | `authora_live_...` | [Dashboard](https://client.authora.dev) > API Keys |
| **Workspace ID** | `ws_...` | [Dashboard](https://client.authora.dev) > Settings |
| **User ID** | `usr_...` | [Dashboard](https://client.authora.dev) > Settings |
| **Organization ID** | `org_...` | [Dashboard](https://client.authora.dev) > Settings |

**Environment variables (Docker/CI):** Set `AUTHORA_API_KEY`, `AUTHORA_AGENT_ID`, `AUTHORA_ORG_ID`, `AUTHORA_WORKSPACE_ID`.

The `created_by` parameter used when creating agents or API keys is your **User ID** (`usr_...`).

## Features

- Sync and async clients built on [httpx](https://www.python-httpx.org/)
- Full type annotations with `py.typed` marker
- Python 3.9+
- Typed error hierarchy for precise exception handling

## Usage

### Synchronous

```python
from authora import AuthoraClient

client = AuthoraClient(
    api_key="authora_live_...",     # from Account > API Keys
    # base_url="https://api.authora.dev/api/v1",  # default
    # timeout=30.0,                                 # default (seconds)
)

# Create a role
role = client.roles.create(
    workspace_id="ws_...",          # from Account > Profile
    name="data-reader",
    permissions=["data:read", "metadata:read"],
)

# Check a permission
result = client.permissions.check(
    agent_id="agt_abc",
    resource="files:reports/*",
    action="read",
)
if result.allowed:
    print("Access granted")
```

### Asynchronous

```python
from authora import AsyncAuthoraClient

async def main():
    client = AsyncAuthoraClient(api_key="authora_live_...")

    agents = await client.agents.list(workspace_id="ws_456")
    for agent in agents.items:
        print(f"{agent.id}: {agent.status}")
```

## Edge Endpoints

For high-availability scenarios, Authora provides an edge proxy at `https://edge.authora.dev` powered by Cloudflare Workers. Agent identity verification, JWT validation, and public key lookups are served from globally distributed edge caches with 24-hour survivability if the origin is unreachable. The edge proxy runs in parallel with the primary API -- no client changes required.

## Resources

All resources are available on both `AuthoraClient` (sync) and `AsyncAuthoraClient` (async):

| Resource          | Attribute              | Methods |
|-------------------|------------------------|---------|
| Agents            | `client.agents`        | create, list, get, verify, activate, suspend, revoke, rotate_key |
| Roles             | `client.roles`         | create, list, get, update, delete, assign, unassign, list_agent_roles |
| Permissions       | `client.permissions`   | check, check_batch, get_effective |
| Delegations       | `client.delegations`   | create, get, revoke, verify, list, list_by_agent |
| Policies          | `client.policies`      | create, list, update, delete, simulate, evaluate, attach_to_target, detach_from_target, list_attachments, list_policy_targets, add_permission, remove_permission |
| MCP               | `client.mcp`           | register_server, list_servers, get_server, update_server, list_tools, register_tool, proxy |
| Audit             | `client.audit`         | list_events, get_event, create_report, get_metrics |
| Notifications     | `client.notifications` | list, unread_count, mark_read, mark_all_read |
| Webhooks          | `client.webhooks`      | create, list, update, delete |
| Alerts            | `client.alerts`        | create, list, update, delete |
| API Keys          | `client.api_keys`      | create, list, revoke |
| Organizations     | `client.organizations` | create, get, list |
| Workspaces        | `client.workspaces`    | create, get, list |
| Approvals         | `client.approvals`     | create, list, get, decide, bulk_decide, stats, settings, update_settings, list_escalation_rules, get_escalation_rule, create_escalation_rule, update_escalation_rule, delete_escalation_rule, list_patterns, dismiss_pattern, create_policy_from_pattern, list_webhooks, create_webhook, update_webhook, delete_webhook |
| Credits           | `client.credits`       | balance, transactions, checkout |
| User Delegations  | `client.user_delegations` | create, get, list_by_user, list_by_agent, list_by_org, revoke, issue_token, refresh_token, verify_token, create_trust, get_trust, list_trust, approve_trust, suspend_trust, revoke_trust, get_settings, update_settings |

## Error Handling

All API errors inherit from `AuthoraError`:

```python
from authora import AuthoraClient
from authora.errors import (
    AuthoraError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    NetworkError,
    TimeoutError,
)

client = AuthoraClient(api_key="authora_live_...")

try:
    agent = client.agents.get("agt_nonexistent")
except NotFoundError:
    print("Agent not found")
except AuthenticationError:
    print("Bad API key")
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after}s")
except AuthoraError as e:
    print(f"API error {e.status_code}: {e.message}")
```

| Class                 | HTTP Status | Description                          |
|-----------------------|-------------|--------------------------------------|
| `AuthoraError`        | any         | Base class for all API errors        |
| `AuthenticationError` | 401         | Invalid or missing API key           |
| `AuthorizationError`  | 403         | Insufficient permissions             |
| `NotFoundError`       | 404         | Requested resource does not exist    |
| `ValidationError`     | 422         | Request validation failed            |
| `RateLimitError`      | 429         | Too many requests; has `retry_after` |
| `TimeoutError`        | 408         | Request exceeded the timeout         |
| `NetworkError`        | 0           | Network/connectivity failure         |

## Agent Runtime

The `AuthoraAgent` (sync) and `AsyncAuthoraAgent` (async) classes provide a full agent runtime with Ed25519 signed requests, client-side permission caching, delegation, and MCP tool calls.

```python
from authora import AuthoraClient

client = AuthoraClient(api_key="authora_live_...")

# Create + activate an agent (generates Ed25519 keypair locally)
result = client.create_agent(
    workspace_id="ws_...",          # from Account > Profile
    name="data-processor",
    created_by="usr_...",           # your User ID
)
agent, key_pair = result.agent, result.key_pair

# Load the agent runtime
runtime = client.load_agent(agent_id=agent.id, private_key=key_pair.private_key)

# All requests are Ed25519-signed automatically
profile = runtime.get_profile()
doc = runtime.get_identity_document()

# Server-side permission check
result = runtime.check_permission("files:read", "read")
if result.allowed:
    print("Access granted")

# Client-side cached check (deny-first, 5-minute TTL)
if runtime.has_permission("mcp:server1:tool.query"):
    result = runtime.call_tool(tool_name="query", arguments={"sql": "SELECT 1"})

# Delegate permissions
delegation = runtime.delegate(
    target_agent_id="agent_...",
    permissions=["files:read"],
    constraints={"expires_in": "1h"},
)

# Key rotation
updated_agent, new_key_pair = runtime.rotate_key()

# Lifecycle
runtime.suspend()
reactivated_agent, fresh_key_pair = runtime.reactivate()
runtime.revoke()
```

### Async Agent Runtime

```python
from authora import AsyncAuthoraClient

async def main():
    client = AsyncAuthoraClient(api_key="authora_live_...")
    result = await client.create_agent(
        workspace_id="ws_...",      # from Account > Profile
        name="async-agent",
        created_by="usr_...",       # your User ID
    )
    runtime = await client.load_agent(
        agent_id=result.agent.id,
        private_key=result.key_pair.private_key,
    )
    profile = await runtime.get_profile()
    allowed = await runtime.has_permission("files:read")
```

## Cryptography

Ed25519 key generation, signing, and verification via PyNaCl.

```python
from authora import generate_key_pair
from authora.crypto import sign, verify, build_signature_payload, sha256_hash

# Generate Ed25519 keypair (base64url encoded)
key_pair = generate_key_pair()
print(key_pair.private_key, key_pair.public_key)

# Sign and verify
signature = sign("hello world", key_pair.private_key)
valid = verify("hello world", signature, key_pair.public_key)

# Build canonical signature payload for HTTP requests
payload = build_signature_payload("POST", "/api/v1/agents", "2025-01-01T00:00:00.000Z", "{}")
```

## Requirements

- Python 3.9+
- [httpx](https://www.python-httpx.org/) >= 0.25.0
- [PyNaCl](https://pynacl.readthedocs.io/) >= 1.5.0

## License

MIT

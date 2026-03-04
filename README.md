# authora

Official Python SDK for the [Authora](https://authora.dev) platform -- agent identity, authorization, and delegation management for AI systems.

- Sync and async clients built on [httpx](https://www.python-httpx.org/)
- Full type annotations with `py.typed` marker
- Python 3.9+
- Typed error hierarchy for precise exception handling

## Installation

```bash
pip install authora
```

## Quick Start

### Synchronous

```python
from authora import AuthoraClient

client = AuthoraClient(
    api_key="authora_live_...",
    # base_url="https://api.authora.dev/api/v1",  # default
    # timeout=30.0,                                 # default (seconds)
)

# Create a role
role = client.roles.create(
    workspace_id="ws_456",
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

## Resources

All resources are available on both `AuthoraClient` (sync) and `AsyncAuthoraClient` (async):

| Resource          | Attribute              | Methods |
|-------------------|------------------------|---------|
| Agents            | `client.agents`        | create, list, get, verify, activate, suspend, revoke, rotate_key |
| Roles             | `client.roles`         | create, list, get, update, delete, assign, unassign, list_agent_roles |
| Permissions       | `client.permissions`   | check, check_batch, get_effective |
| Delegations       | `client.delegations`   | create, get, revoke, verify, list, list_by_agent |
| Policies          | `client.policies`      | create, list, update, delete, simulate, evaluate |
| MCP               | `client.mcp`           | register_server, list_servers, get_server, update_server, list_tools, register_tool, proxy |
| Audit             | `client.audit`         | list_events, get_event, create_report, get_metrics |
| Notifications     | `client.notifications` | list, unread_count, mark_read, mark_all_read |
| Webhooks          | `client.webhooks`      | create, list, update, delete |
| Alerts            | `client.alerts`        | create, list, update, delete |
| API Keys          | `client.api_keys`      | create, list, revoke |
| Organizations     | `client.organizations` | create, get, list |
| Workspaces        | `client.workspaces`    | create, get, list |

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

## Requirements

- Python 3.9+
- [httpx](https://www.python-httpx.org/) >= 0.25.0

## License

MIT

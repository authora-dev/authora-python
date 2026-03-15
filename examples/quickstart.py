import os
from authora import AuthoraClient

client = AuthoraClient(api_key=os.environ["AUTHORA_API_KEY"])

agent = client.agents.create(name="my-agent", workspace_id="ws_...")
print(f"Created agent: {agent.id}")

roles = client.roles.list(workspace_id=agent.workspace_id)
print(f"Available roles: {len(roles.data)}")

client.agents.suspend(agent.id)
print("Agent suspended")

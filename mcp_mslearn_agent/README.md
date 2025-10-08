# Minimal Microsoft Learn MCP Demo (Azure AI Foundry Agents)

Two small scripts that show how to use the **Microsoft Learn MCP tool** from an Azure AI Foundry Agent:
- `create_agent.py` — creates an agent with an MCP tool.
- `ask_agent.py` — simple chat loop that streams the agent's reply and prints basic tool activity.

## Setup

### 1) 

```bash
pip install -r requirements.txt
cp .env.sample .env
# Fill in PROJECT_ENDPOINT and MODEL_DEPLOYMENT_NAME
```

### 2) Create the agent

```bash
python create_agent.py
```

This writes the new agent id to `./.agent_id`.

### 3) Chat with the agent

```bash
python ask_agent.py
```

- Type questions like:
  - `Find docs on Azure Functions triggers and bindings.`
  - `Show the Learn article that explains Azure Cosmos DB indexing.`
  - `What’s the difference between Standard and Premium for Azure App Service? Include links.`
- The console shows:
  - streaming assistant tokens (so you see the reply as it's generated),
  - basic run/step events,
  - basic MCP tool call details (server label + tool name).

### Auth

- No auth is required for the Microsoft Learn MCP server. 
- Comments in `ask_agent.py` highliught where auth headers would be added in a way that does not persist auth tokens on the agent if they were required. 

### Notes

- Auth headers are added **at run time** via `tool_resources`; they are **not persisted** on the agent.
- `create_agent.py` always creates a fresh agent (intentionally no idempotency to keep the demo simple).
- `ask_agent.py` reads `./.agent_id` (or AGENT_ID env var) and runs a small REPL.


## Troubleshooting (quick fixes)

- **Tool appears unused**  
  The model may decide not to call a tool for vague prompts. Ask explicitly for documentation (e.g., “Search Microsoft Learn for <topic> and summarize with links.”).

- **Agent not found**  
  Run `create_agent.py` again to make a fresh agent and refresh `./.agent_id`.

## Docs

- [Azure AI Agents SDK: Create an agent with MCP](https://github.com/Azure/azure-sdk-for-python/tree/azure-ai-agents_1.2.0b3/sdk/ai/azure-ai-agents#create-agent-with-mcp)
- [Azure AI Agents SDK reference](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-agents-readme?view=azure-python)
- [Azure AI Foundry - Connect to Model Context Protocol servers (preview)](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/model-context-protocol)
- [Azure AI Foundry - Code Samples: Hot to use the MCP tool (preview)](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/model-context-protocol-samples?pivots=python)
- [Microsoft Learn MCP Server](https://learn.microsoft.com/en-us/training/support/mcp)
# MCP Microsoft Learn Agent (v2 — Azure AI Foundry Agents)

A minimal demo connecting an Azure AI Foundry Agent to the [Microsoft Learn MCP server](https://learn.microsoft.com/training/support/mcp) using the GA v2 SDK (`azure-ai-projects>=2.0.0`).

The agent can search and retrieve Microsoft Learn documentation via MCP tools — no authentication required for the MCP server.

## What This Demo Shows

- Creating a Foundry agent with an MCP tool (`MCPTool` + `PromptAgentDefinition`)
- Streaming responses via the OpenAI Responses API (`responses.create` with `stream=True`)
- Visible MCP tool call events in the terminal
- Conversation continuity via `previous_response_id` chaining

## Prerequisites

- Python 3.11+
- An Azure AI Foundry project with:
  - A deployed model (e.g., `gpt-4.1`, `gpt-5-mini`)
  - Public network access enabled (required for MCP tools)
- Azure CLI logged in (`az login`) or other credential for `DefaultAzureCredential`

## Setup

### 1. Install dependencies

```bash
# (recommended) Create a virtual environment
python -m venv .venv && source .venv/bin/activate

pip install -r requirements.txt
cp .env.sample .env
# Fill in PROJECT_ENDPOINT and MODEL_DEPLOYMENT_NAME
```

> **Note:** Only public network access is supported with MCP tools at this time. Your Foundry resource must allow public network access.

### 2. Create the agent

```bash
python create_agent.py
```

This creates a versioned agent in your Foundry project and writes the agent name to `.agent_name`.

### 3. Chat with the agent

```bash
python ask_agent.py
```

Try these prompts:
- `Find docs on Azure Functions triggers and bindings`
- `What is Azure Cosmos DB indexing? Include links.`
- `Search Microsoft Learn for Azure App Service deployment options`

The console shows:
- Streaming assistant tokens (reply appears as it's generated)
- MCP tool call indicators (server label + tool name)

### 4. Cleanup

Exit the interactive loop with `/exit`, then:

```bash
deactivate  # Exit virtual environment
```

## How It Works

### Agent Creation (`create_agent.py`)

Creates an agent with the Microsoft Learn MCP tool using the GA v2 SDK:

```python
from azure.ai.projects.models import PromptAgentDefinition, MCPTool

tools = [
    MCPTool(
        server_label="learn",
        server_url="https://learn.microsoft.com/api/mcp",
        require_approval="never",  # read-only, no auth needed
    ),
]

agent = project.agents.create_version(
    agent_name="mcp-mslearn-demo-agent",
    definition=PromptAgentDefinition(model=model, instructions=instructions, tools=tools),
)
```

### Interactive Chat (`ask_agent.py`)

Uses the OpenAI Responses API via `project.get_openai_client()`:

```python
response = openai_client.responses.create(
    input=user_input,
    extra_body={"agent_reference": {"name": agent_name, "type": "agent_reference"}},
    stream=True,
)
```

Conversation continuity is maintained with `previous_response_id` — each response chains to the previous one.

### Auth

- **Azure AI Foundry**: `DefaultAzureCredential` (Azure CLI, managed identity, etc.)
- **Microsoft Learn MCP server**: No auth required — it's a public endpoint
- No approval flow needed — `require_approval="never"` is set at agent creation

## Looking for the Original?

The v1 version of this demo (from the walkthrough video) is preserved at [`archive/v1/mcp_mslearn_agent/`](../archive/v1/mcp_mslearn_agent/).

### Changes from v1

| Aspect | v1 | v2 |
|--------|----|----|
| SDK | `azure-ai-agents` (separate package, deprecated) | `azure-ai-projects>=2.0.0` (GA, unified) |
| Agent creation | `project.agents.create_agent()` + `McpTool` | `project.agents.create_version()` + `PromptAgentDefinition` + `MCPTool` |
| Conversation | Threads + Runs + `AgentEventHandler` | OpenAI Responses API (`responses.create`) |
| Agent reference | `.agent_id` file | `.agent_name` file |
| Streaming | `AgentEventHandler.on_message_delta` | Response stream events |

## Troubleshooting

- **Tool appears unused**: The model may skip tools for vague prompts. Ask explicitly for documentation (e.g., "Search Microsoft Learn for `<topic>` and summarize with links.")
- **Agent not found**: Run `create_agent.py` again to create a fresh agent and refresh `.agent_name`.
- **Network errors**: Ensure your Foundry resource has public network access enabled.

## Related Docs

- [Azure AI Foundry — Connect to MCP servers](https://learn.microsoft.com/azure/ai-foundry/agents/how-to/tools/model-context-protocol)
- [Azure AI Foundry — MCP tool code samples](https://learn.microsoft.com/azure/ai-foundry/agents/how-to/tools/model-context-protocol-samples?pivots=python)
- [Microsoft Learn MCP Server](https://learn.microsoft.com/training/support/mcp)
- [Azure AI Projects SDK reference](https://learn.microsoft.com/python/api/overview/azure/ai-projects-readme?view=azure-python)

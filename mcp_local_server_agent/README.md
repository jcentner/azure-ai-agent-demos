# MCP Local Server Agent (v2 — Azure AI Foundry Agents)

A demo connecting an Azure AI Foundry Agent to a **local MCP server** (Chinook SQLite database) using the GA v2 SDK (`azure-ai-projects>=2.0.0`). The agent can query, insert, update, and inspect a music store database through natural language.

## What This Demo Shows

- Running a **custom MCP server** locally (FastMCP + Starlette + SQLite)
- Exposing it to Azure via **ngrok** (HTTPS tunnel)
- Creating a Foundry agent that connects to your local MCP server
- **MCP approval flow** — agent requests approval before calling tools (auto-approved for demo)
- Optional **Foundry project connection** auth (bearer token stored in Foundry, not in code)
- Streaming responses via the OpenAI Responses API

## Architecture

```
Azure AI Agent ⇄ https://<sub>.ngrok.app ⇄ Local MCP Server (localhost:8787/mcp)
                                              └─ Chinook SQLite database
```

The MCP server exposes 8 tools, 1 resource, and 1 prompt:

| MCP Tools | Description |
|-----------|-------------|
| `list_tables` | Table names and row counts |
| `get_table_info` | Column types, PKs, foreign keys |
| `run_sql` | Read-only SELECT queries |
| `run_sql_write` | INSERT/UPDATE/DELETE/REPLACE |
| `insert_customer` | Add a customer (with email validation) |
| `update_customer_email` | Update customer email |
| `top_customers` | Top N customers by invoice total |
| `create_invoice` | Create invoice with line items |

## Prerequisites

- Python 3.11+
- [ngrok](https://ngrok.com/) (free account is fine)
- An Azure AI Foundry project with:
  - A deployed model (e.g., `gpt-4.1`, `gpt-4.1-mini`)
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

### 2. Start the MCP server

```bash
cd mcp_local_server_agent
python -m server.app
# expect: "Starting MCP server on http://127.0.0.1:8787/mcp"
```

Optional: Set `LOCAL_MCP_TOKEN=your-demo-token` in `.env` to enable bearer auth.

### 3. Expose with ngrok

In a separate terminal:

```bash
ngrok http 8787
# Copy the HTTPS forwarding URL (e.g., https://<sub>.ngrok.app)
```

Set the URL in `.env`:

```bash
MCP_SERVER_URL=https://<sub>.ngrok.app/mcp
```

> **Important:** Include the `/mcp` path in the URL.

### 4. (Optional) Set up auth via Foundry project connection

If you set `LOCAL_MCP_TOKEN` on your server, store the same token in a Foundry project connection:

1. Go to Azure AI Foundry portal → your project → **Connected resources**
2. Create a **Custom** connection with your bearer token
3. Set `MCP_CONNECTION_NAME=<connection-name>` in `.env`

This follows the credential isolation pattern (ADR-002) — credentials are stored in Foundry, not in code.

### 5. Create the agent

```bash
python create_agent.py
```

This creates a versioned agent in your Foundry project and writes the agent name to `.agent_name`.

### 6. Chat with the agent

```bash
python ask_agent.py
```

Try these prompts:
- `List all tables in the database`
- `Show the top 5 customers by spending`
- `Create a new customer named Test User with email test@example.com`
- `Run a SQL query to find all albums by AC/DC`

The console shows:
- Streaming assistant tokens
- MCP tool call indicators (server label + tool name)
- Approval events (auto-approved for demo)

### 7. Cleanup

Exit the interactive loop with `/exit`, stop the MCP server (`Ctrl+C`), stop ngrok.

## How It Works

### MCP Server (`server/`)

A local [FastMCP](https://github.com/modelcontextprotocol/python-sdk) server using Streamable HTTP transport:

```python
# server/app.py
mcp = FastMCP(name="Chinook SQLite MCP Server")
surface_tools.register(mcp, db)    # 8 tools
surface_schema.register(mcp, db)   # 1 resource (schema://current)
surface_prompt.register(mcp)       # 1 prompt
app = mcp.streamable_http_app()    # Starlette app at /mcp
```

The database uses a working copy of `chinook.db` — reset on each restart (unless `PERSIST_WORKING_COPY=true`).

### Agent Creation (`create_agent.py`)

```python
MCPTool(
    server_label="chinook",
    server_url=server_url,          # ngrok HTTPS URL
    require_approval="always",      # approval flow for write operations
    project_connection_id=conn,     # optional: Foundry connection with bearer token
)
```

### Interactive Chat (`ask_agent.py`)

Uses the same OpenAI Responses API pattern as the enterprise agent:
- `responses.create()` with `agent_reference` in `extra_body`
- Response chaining via `previous_response_id`
- MCP approval loop: detect `mcp_approval_request` → send `mcp_approval_response` → stream continuation

## Looking for the Original?

The v1 version of this demo is preserved at [`archive/v1/mcp_local_server_agent/`](../archive/v1/mcp_local_server_agent/).

### Changes from v1

| Aspect | v1 | v2 |
|--------|----|----|
| SDK | `azure-ai-agents` (separate package, deprecated) | `azure-ai-projects>=2.0.0` (GA, unified) |
| Agent creation | `project.agents.create_agent()` + `McpTool` | `project.agents.create_version()` + `PromptAgentDefinition` + `MCPTool` |
| Conversation | Threads + Runs + `AgentEventHandler` | OpenAI Responses API (`responses.create`) |
| Agent reference | `.agent_id` file | `.agent_name` file |
| Auth | Runtime header injection (`mcp.update_headers()`) | Foundry project connection (`project_connection_id`) |
| Layout | Nested `agent/` + `server/` subdirs | Flat agent scripts + `server/` subdir |

## Configuration

All config is via environment variables (loaded from `.env` by `python-dotenv`):

| Variable | Required | Description |
|----------|----------|-------------|
| `PROJECT_ENDPOINT` | Yes | Azure AI Foundry project endpoint |
| `MODEL_DEPLOYMENT_NAME` | Yes | Model deployment name |
| `MCP_SERVER_URL` | Yes (for agent) | Public ngrok URL to your MCP server |
| `AGENT_NAME` | No | Agent name (default: `mcp-local-chinook-demo`) |
| `MCP_CONNECTION_NAME` | No | Foundry connection name for MCP auth |
| `LOCAL_MCP_TOKEN` | No | Bearer token for MCP server auth |
| `PORT` | No | MCP server port (default: 8787) |
| `DB_BASE_PATH` | No | Path to Chinook DB (default: `server/db/chinook.db`) |
| `PERSIST_WORKING_COPY` | No | Keep DB changes across restarts (default: false) |

## Troubleshooting

- **MCP tools not called**: Ask explicitly (e.g., "Use the MCP tools to list all tables").
- **Agent not found**: Run `create_agent.py` again to create a fresh agent.
- **401 from MCP server**: Set `MCP_CONNECTION_NAME` in `.env` with a Foundry connection that holds your `LOCAL_MCP_TOKEN`.
- **ngrok URL changed**: Recreate the agent (`create_agent.py`) — the MCP server URL is stored on the agent definition.
- **Server can't find chinook.db**: Run from the `mcp_local_server_agent/` directory, or set `DB_BASE_PATH` explicitly.

## Related Docs

- [Azure AI Foundry — Connect to MCP servers](https://learn.microsoft.com/azure/ai-foundry/agents/how-to/tools/model-context-protocol)
- [Azure AI Foundry — MCP tool code samples](https://learn.microsoft.com/azure/ai-foundry/agents/how-to/tools/model-context-protocol-samples?pivots=python)
- [Model Context Protocol — Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Chinook Database](https://github.com/lerocha/chinook-database)

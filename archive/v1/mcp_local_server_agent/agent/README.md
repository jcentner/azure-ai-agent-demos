# Azure AI Foundry Agent for local MCP Server

Two small scripts that show how to use a **local MCP server** (SQLite Chinook) from an **Azure AI Foundry Agent**:
- `create_agent.py` — creates an agent (no secrets persisted).
- `ask_agent.py` — simple chat loop that streams the agent’s reply and prints basic tool activity.

> Prerequisite: run the local MCP server first (see `../server/README.md`) and, if running the agent from Azure or any remote environment, expose it via **ngrok** and set `MCP_SERVER_URL` to the public **HTTPS** URL ending with `/mcp`.

---

## Setup

~~~bash
# install only the agent deps, if you did not already install ../requirements.txt 
pip install -r agent/requirements.txt

# copy env and fill values at demo root (../.env)
cp .env.sample .env
# Required:
#   PROJECT_ENDPOINT
#   MODEL_DEPLOYMENT_NAME
# Recommended: 
#   MCP_SERVER_URL   (https://<your>.ngrok.app/mcp — must be reachable from Azure)
# Optional:
#   LOCAL_MCP_TOKEN  (if your MCP server enforces Bearer auth)
#   AGENT_NAME
~~~

**Environment variables (used by these scripts):**

| Name | Required | Example | Notes |
|---|:---:|---|---|
| `PROJECT_ENDPOINT` | ✓ | `https://<proj>.<region>.models.ai.azure.com` | Your Azure AI Foundry project endpoint |
| `MODEL_DEPLOYMENT_NAME` | ✓ | `gpt-4o` | Model deployment to back the agent |
| `MCP_SERVER_URL` | ✓ (in Azure) | `https://<sub>.ngrok.app/mcp` | Must be publicly reachable; **include `/mcp`** |
| `LOCAL_MCP_TOKEN` | — | `your-demo-token` | If your MCP server requires Bearer auth |
| `AGENT_NAME` | — | `mcp_local_server_agent` | Display name for the created agent |
| `AGENT_ID` | — | (read from .agent_id) | Optional override for `ask_agent.py` |

> These scripts auto-load `.env`.

---

## 1) Create the agent

~~~bash
python agent/create_agent.py
~~~

- Writes the new agent id to `./.agent_id`.
- If `MCP_SERVER_URL` is **unset**, the script prints an error (localhost isn't reachable by Azure), pauses, and proceeds with an intentionally invalid URL to let you observe failure behavior. Set a real public URL to make tool calls succeed.

---

## 2) Chat with the agent

~~~bash
python agent/ask_agent.py
~~~

- Try prompts like:
  - `List the top 5 customers by total spend`
  - `Create a customer named Alice Example (alice@example.com), then show their last invoice`
  - `Insert an invoice for customer 1 with one item (track 5, price 0.99, quantity 2)`
  - `Describe the schema of the invoices table`

- The console shows:
  - streaming assistant tokens (so you see the reply as it’s generated),
  - basic run/step events,
  - basic MCP tool call details (server label + tool name).

### Auth (for the MCP server)
- If `LOCAL_MCP_TOKEN` is set, the scripts attach `Authorization: Bearer <token>` **at run time** for MCP calls.
- If not set and your server requires auth, MCP calls will fail with `401`.

### Notes
- MCP headers are added **at run time** via `tool_resources`; they are **not persisted** on the agent.
- `create_agent.py` always creates a fresh agent (no idempotency to keep the demo simple).
- `MCP_SERVER_URL` must be externally reachable from where the agent runs (Azure). **`http://localhost:8787/mcp` will not work** from Azure—use your **ngrok HTTPS URL** ending with `/mcp`.

---

## Troubleshooting (quick fixes)

- **“Connection error / 404” when using ngrok**  
  Ensure your Inspector/Agent URL **includes `/mcp`** (e.g., `https://<sub>.ngrok.app/mcp`).  
  Your server logs should show `POST /mcp ...` (not `POST /`).

- **“Unauthorized” / 401**  
  Set `LOCAL_MCP_TOKEN` in `.env` and restart the script(s). Your MCP server will then accept the `Authorization: Bearer <token>` header.

- **Tool appears unused**  
  Models may skip tools if the prompt is vague. Ask explicitly (e.g., “Use the database tool to list tables, then show the first 3 customers”).

- **ngrok 502 / connection failed**  
  Verify the server is running on your machine at `http://localhost:8787/mcp`, and that you’re connecting to the **HTTPS** ngrok URL with the **`/mcp`** suffix. Do not tunnel the Inspector; tunnel the server port only.

- **Localhost won’t work in Azure**  
  Set `MCP_SERVER_URL` to your **public** MCP endpoint (e.g., `https://<sub>.ngrok.app/mcp`). The scripts warn and pause if it’s missing, then proceed with an invalid URL so you can see failure behavior.

- **Agent not found**  
  Re-run `create_agent.py` to create a fresh agent and refresh `./.agent_id`.

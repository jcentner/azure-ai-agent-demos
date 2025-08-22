# Local MCP Inspector → Local MCP Server → ngrok → Azure AI Agent

This repo teaches you how to:
1) run a **local MCP server** for a sample sqlite database,
2) inspect it with the **MCP Inspector**,
3) publish it via **ngrok** (HTTPS), and
4) point an **Azure AI Foundry Agent** at that published MCP endpoint to use the tools.

---

## Repository map

```
mcp-local-inspector-ngrok-to-azure-agent/
├─ README.md                   # ← this file
├─ .env.sample                 # shared env for server+agent (copy to .env)
├─ requirements.txt            # aggregates agent/ and server/ requirements
├─ server/                     # local MCP server (Streamable HTTP at /mcp)
│  ├─ README.md
│  ├─ db/
│  ├─ surface/
│  ├─ prompts/                 # (kept for reference; consolidated in surface/)
│  ├─ resources/               # (kept for reference; consolidated in surface/)
│  ├─ app.py, auth.py, config.py, errors.py, logging.py, requirements.txt
│  └─ schema-diagram.png       # (optional helper image)
├─ inspector/                  # MCP Inspector usage
│  └─ README.md
├─ agent/                      # Azure AI Foundry Agent demo
│  ├─ README.md
│  ├─ create_agent.py
│  ├─ ask_agent.py
│  └─ requirements.txt
└─ docs/
   ├─ architecture.md          # flows & diagrams
   ├─ protocol-cheatsheet.md   # MCP calls and tips
   └─ images/                  # (optional: architecture.svg/png, sequence diagrams)
```

---

## Goals (and non-goals)

**Goals**
- Understand the **MCP protocol** by running and inspecting a server.
- Learn the **Streamable HTTP** transport shape.
- Safely demo **read/write** with a working copy of `chinook.db`.
- Connect a **remote** Azure AI Agent to a **local** MCP server via **ngrok**.

**Non-goals**
- Production hardening (mTLS, IP allowlists, rotation, multi-tenant routing).
- Exhaustive DB tooling (we focus on a minimal, well-documented sample).

---

## Architecture at a glance

**Flow A (local learning loop):**  
Inspector ⇄ MCP Server (`http://localhost:8787/mcp`)

**Flow B (end-to-end with Azure):**  
Azure AI Agent ⇄ `https://<sub>.ngrok.app` ⇄ MCP Server (`/mcp`)

See `docs/architecture.md` for a diagram and sequence details.

---

## Prerequisites

- **Python 3.11+**
- **Node.js 22+** (for `npx` MCP Inspector)
- **ngrok** (a free account is fine)
- Azure access: **PROJECT_ENDPOINT** + a **MODEL_DEPLOYMENT_NAME** in your Azure AI Foundry project (basic environment is fine) 

> Supported models: [Models supported by Azure AI Foundry Agent Service](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/model-region-support?tabs=global-standard)

---

## Quickstart

> Each component has its own README with full step-by-step instructions.

### A) Local learning loop (no Azure)

1) **Install**

~~~bash
# (recommended) python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.sample .env
~~~

2) **Run the server**  
See `server/README.md` for details.
~~~bash
python -m server.app
# expect: "Starting MCP server on http://0.0.0.0:8787/mcp"
~~~

3) **Use the Inspector**  
See `inspector/README.md` to install Node+`npx` and connect:
- Transport: **Streamable HTTP**
- URL: `http://localhost:8787/mcp`

4) **Try tools** in the Inspector: `list_tables`, `top_customers`, `run_sql`, etc.

---

### B) End-to-end (Azure Agent uses your local server via ngrok)

1) **Run the server** (as above).

2) **Expose with ngrok** (see the ngrok section in `server/README.md`):
~~~bash
ngrok http 8787
# copy the HTTPS forwarding URL (e.g., https://<sub>.ngrok.app)
~~~

3) **Configure agent env**
~~~bash
# in .env
PROJECT_ENDPOINT=https://<proj>.<region>.models.ai.azure.com
MODEL_DEPLOYMENT_NAME=<deployment-name>
MCP_SERVER_URL=https://<sub>.ngrok.app/mcp
LOCAL_MCP_TOKEN=your-demo-token    # enables server auth (recommended; agent picks this up automatically)
~~~

4) **Create the agent**  
See `agent/README.md` for details.
~~~bash
python agent/create_agent.py
# writes ./.agent_id and shows the MCP URL attached to the agent
~~~

5) **Chat**  
~~~bash
python agent/ask_agent.py
~~~
- Type: “list top customers”, “create a new customer…”, and so on.
- The console streams tokens and prints tool call steps (with verbose details).

---

## Configuration model

- Use a **single repo-root `.env`** (copied from `.env.sample`).  
  Both server and agent automatically load it via **python-dotenv**.
- With a free ngrok account, the `MCP_SERVER_URL` will change on each run. If needed, **recreate the agent** (`create_agent.py`) — the MCP tool URL is persisted on the agent.

---

## Security notes

- **Do not tunnel the Inspector;** tunnel only the server port (8787).
- Set `LOCAL_MCP_TOKEN` if you expose the server; clients must then send `Authorization: Bearer <token>`.
- Agent scripts attach auth headers **at run time** rather than persist them.

---

## Troubleshooting (triage)

| Symptom | Likely cause | Quick fix |
|---|---|---|
| Inspector CLI errors on `??`/`?.` | Old Node versopm | [Install Node **22+**](https://nodejs.org/en/download/) (recommend nvm), re-run Inspector |
| Server logs `POST /` → **404** | Missing `/mcp` | Use `…/mcp` path in the Inspector/Agent URL |
| Agent 404 but Inspector OK | Agent’s persisted tool URL may be wrong | Set `MCP_SERVER_URL=…/mcp`, **recreate agent** |
| 401 Unauthorized | Missing token | Set `LOCAL_MCP_TOKEN` and client header |

---

## Extending the demo

- Add a new MCP tool (e.g., parameterized report) or a read-only approval mode path.
- Swap SQLite for another backend (Postgres, REST proxy) while keeping the MCP interface.
- Hardening, observability, and other production requirements 

---

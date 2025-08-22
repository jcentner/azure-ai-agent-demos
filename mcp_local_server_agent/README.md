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
- **ngrok** (free account ok)
- Azure access: **PROJECT_ENDPOINT** + a **MODEL_DEPLOYMENT_NAME** in your Azure AI Foundry project
- Note: **localhost URLs do not work from Azure** — use your **ngrok HTTPS URL** ending with `/mcp`.

---

## Quickstart

> Each component has its own README with full step-by-step instructions. Start here, then dive deeper.

### A) Local learning loop (no Azure yet)

1) **Install**
~~~bash
pip install -r requirements.txt
cp .env.sample .env
# Fill in at least: PROJECT_ENDPOINT, MODEL_DEPLOYMENT_NAME (used later for agent)
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
MCP_SERVER_URL=https://<sub>.ngrok.app/mcp
LOCAL_MCP_TOKEN=your-demo-token    # if server requires Bearer auth (recommended)
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
- Type: “list top customers”, “create a new customer…”, etc.
- The console streams tokens and prints tool call steps (with verbose details).

---

## Configuration model

- Use a **single repo-root `.env`** (copied from `.env.sample`).  
  Both server and agent automatically load it via **python-dotenv** — no `source` needed.
- Common variables (see component READMEs for full tables):
  - `PROJECT_ENDPOINT`, `MODEL_DEPLOYMENT_NAME`, `MCP_SERVER_URL`, `LOCAL_MCP_TOKEN`, `PORT`, `MCP_PATH=/mcp`.
- Changing `MCP_SERVER_URL` after agent creation? **Recreate the agent** (`create_agent.py`) — the MCP tool URL is **persisted** on the agent.

---

## Security notes

- **Do not tunnel the Inspector;** tunnel only the server port (8787).
- Set `LOCAL_MCP_TOKEN` if you expose the server; clients must send `Authorization: Bearer <token>`.
- Agent scripts attach headers **at run time** (not persisted).

---

## Troubleshooting (triage)

| Symptom | Likely cause | Quick fix |
|---|---|---|
| Inspector CLI errors on `??`/`?.` | Old Node | Install Node **22+**, re-run Inspector |
| Server logs `POST /` → **404** | Missing `/mcp` | Use `…/mcp` path (Inspector/Agent URL) |
| `POST /mcp/` → **404** | Trailing slash mismatch | Use `…/mcp`; server also accepts `/mcp/` if you applied the redirect delta |
| `Task group is not initialized` | Lifespan not wired to inner app | Ensure `Starlette(..., lifespan=inner.lifespan)` |
| Agent 404 but Inspector OK | Agent’s persisted tool URL wrong | Set `MCP_SERVER_URL=…/mcp`, **recreate agent** |
| 401 Unauthorized | Missing token | Set `LOCAL_MCP_TOKEN` and client header |
| “no such table: …” | Chinook variant name mismatch | Use updated `server/surface/tools.py` (auto-detects snake_case vs singular) |
| Tool calls not visible in console | Minimal handler | Use enhanced logging in `agent/ask_agent.py` (prints tool name/args/output/error) |

---

## Extending the demo

- Add a new MCP tool (e.g., parameterized report) or a read-only approval mode path.
- Swap SQLite for another backend (Postgres, REST proxy) while keeping the MCP interface.
- Hardening: TLS termination, IP allowlists, reserved ngrok domains, CI smoke tests across endpoints.

---

## License & contributions

- MIT (or your org’s standard)—add your license file at repo root.
- PRs welcome: keep deltas focused, update READMEs alongside code, and preserve copy/paste-safe fences (outer quad, inner `~~~`).

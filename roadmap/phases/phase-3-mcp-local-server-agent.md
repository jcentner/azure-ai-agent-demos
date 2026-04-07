# Phase 3: MCP Local Server Agent v2 Rewrite

## Goal

Port the v1 MCP Local Server Agent demo to the GA v2 SDK (`azure-ai-projects>=2.0.0`). This demo is unique: it includes a custom MCP server (Chinook SQLite) alongside the agent scripts.

## Key Differences from Other Demos

- **Custom MCP server** — The demo includes its own `server/` subdirectory (vision lock exception to flat layout)
- **Auth is optional** — `MCP_CONNECTION_NAME` is optional; if set, uses Foundry project connection for bearer token auth
- **Write operations** — Server exposes INSERT/UPDATE/DELETE tools, so `require_approval="always"` with auto-approval loop
- **Requires ngrok** — Azure agent can't reach localhost; ngrok tunnels the local server

## V1 → V2 Changes

### Server (minimal changes)
- Server code is pure MCP protocol (FastMCP + Starlette + SQLite) — port nearly verbatim
- Restructure: agent scripts move from `agent/` to demo root (flat layout)
- Adjust default paths in config.py

### Agent scripts (full rewrite)
- `create_agent.py`: `PromptAgentDefinition` + `MCPTool` + `create_version()`, optional `project_connection_id`
- `ask_agent.py`: OpenAI Responses API streaming, MCP approval flow (auto-approve), `previous_response_id` chaining
- `.agent_name` file instead of `.agent_id`

## Deliverables

1. `mcp_local_server_agent/server/` — MCP server (ported from v1, minimal changes)
2. `mcp_local_server_agent/create_agent.py` — V2 agent creation
3. `mcp_local_server_agent/ask_agent.py` — V2 interactive REPL with approval flow
4. `mcp_local_server_agent/.env.sample` — All required/optional env vars
5. `mcp_local_server_agent/requirements.txt` — Combined server + agent dependencies
6. `mcp_local_server_agent/README.md` — Complete setup and walkthrough
7. `mcp_local_server_agent/tests/test_agent_config.py` — Structural tests

## Success Criteria

- All structural tests pass
- Server code compiles and follows MCP protocol correctly
- Agent code follows GA SDK patterns (consistent with enterprise agent)
- README has complete setup for both local-only and Azure+ngrok flows
- Self-contained demo directory (ADR-004, with vision lock server exception)

# Azure AI Agent Demos — Current State

**Phase Status**: Complete

## What Exists

- `.github/` — Copilot agents, prompts, hooks, and instructions for autonomous development
- `docs/vision/VISION-LOCK.md` — Vision lock v1.3 — credential isolation pattern, GA SDK
- `docs/architecture/decisions/` — 4 ADRs (two-script pattern, project connection auth, GA v2 SDK, flat layout)
- `.github/skills/azure-docs-research/` — Skill for grounding answers in official MS docs
- `docs/` — Architecture overview, glossary, tech debt tracker, reference docs
- `roadmap/phases/` — Phase 1 (complete), Phase 2 (complete), Phase 3 (complete), Phase 4 (complete)
- `AGENTS.md` — Cross-agent instructions
- `enterprise_github_agent/` — Complete v2 demo: validated GA SDK patterns, project connection auth, typed MCP approvals, 42 passing tests
- `mcp_mslearn_agent/` — Complete v2 demo: public MS Learn MCP server, no auth, auto-approved, 41 passing tests
- `mcp_local_server_agent/` — Complete v2 demo: custom MCP server (Chinook SQLite), approval flow, optional project connection auth, 84 passing tests
- `archive/v1/` — Complete, working v1 demos preserved for reference
- `pyproject.toml` — pytest importlib mode for test isolation across demos

## Current Phase

Phase 4: Cross-Cutting Polish — **COMPLETE**

## Next Action

Begin Phase 5: Fabric Data Agent — natural language queries against Fabric lakehouse via `MicrosoftFabricPreviewTool`.

## Blocked / Unresolved

Nothing blocked. Live testing of all agents requires an Azure AI Foundry project with a model deployment — cannot be automated without credentials.

## Decisions Made

- **Phase 0 complete** — Vision lock synthesized, now tracked in git
- **Phase 1 complete** — Enterprise GitHub Agent validated and fixed for GA SDK
- **Phase 2 complete** — MCP MS Learn Agent ported to v2, 41 tests passing
- **Phase 3 complete** — MCP Local Server Agent ported to v2, 84 tests passing (167 total)
- **Project docs tracked in git** — Removed docs/, roadmap/, AGENTS.md from .gitignore
- ADR-001: Two-script demo pattern (create + ask)
- ADR-002: MCP credentials via Foundry project connections (NOT runtime header injection)
- ADR-003: GA V2 SDK with both response-chaining and Conversations API patterns
- ADR-004: Flat demo directory layout (server/ exception for MCP server demos)
- **extra_body key is `agent_reference`** — All official Python samples use `{"agent_reference": {...}}`
- **MCP auth via project_connection_id** — `McpApprovalResponse` does NOT support headers
- **Public MCP servers use require_approval="never"** — No approval flow needed for read-only public endpoints (MS Learn)
- **Write MCP servers use require_approval="always"** — Approval flow with auto-approve for demos
- **Optional project_connection_id** — Local server demo makes MCP_CONNECTION_NAME optional (no auth needed for local dev)
- **FK pragmas on every connection** — Fixed from v1: PRAGMA foreign_keys=ON in Database.connect() not just at startup
- **pytest importlib mode** — Added pyproject.toml to handle same-named test files across demo directories

## Files Modified This Session

- `mcp_local_server_agent/server/` — Ported: FastMCP server (app, config, auth, db, surface tools/schema/prompt)
- `mcp_local_server_agent/create_agent.py` — Created: v2 agent creation with MCPTool + optional project_connection_id
- `mcp_local_server_agent/ask_agent.py` — Created: v2 REPL with OpenAI Responses API + MCP approval flow
- `mcp_local_server_agent/.env.sample` — Created: server + agent config
- `mcp_local_server_agent/requirements.txt` — Created: combined server + agent deps
- `mcp_local_server_agent/README.md` — Replaced stub with complete setup (local + ngrok + Azure flows)
- `mcp_local_server_agent/tests/test_agent_config.py` — Created: 84 structural + server unit tests
- `roadmap/phases/phase-3-mcp-local-server-agent.md` — Created: Phase 3 plan

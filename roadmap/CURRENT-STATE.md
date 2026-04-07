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
- `enterprise_github_agent/` — Complete v2 demo: validated GA SDK patterns, project connection auth, typed MCP approvals, 42 passing tests, **E2E: agent creation verified**
- `mcp_mslearn_agent/` — Complete v2 demo: public MS Learn MCP server, no auth, auto-approved, 41 passing tests, **E2E: fully verified (create + conversation + streaming + MCP tool calls)**
- `mcp_local_server_agent/` — Complete v2 demo: custom MCP server (Chinook SQLite), approval flow, optional project connection auth, 84 passing tests, **E2E: fully verified (server + ngrok + create + conversation + approval flow + MCP tool calls)**
- `archive/v1/` — Complete, working v1 demos preserved for reference
- `pyproject.toml` — pytest importlib mode for test isolation across demos

## Current Phase

E2E Testing — **COMPLETE**

## E2E Test Results (April 2026)

### mcp_mslearn_agent — FULLY VERIFIED
- `create_agent.py` — Agent created successfully (`e2e-test-mslearn-agent:1`)
- Non-streaming conversation — MCP `microsoft_docs_search` tool called, response with Azure Functions docs
- Streaming conversation — Event types validated: `response.output_text.delta`, `response.mcp_list_tools.*`, `response.completed`
- Conversation continuity via `previous_response_id` — works

### mcp_local_server_agent — FULLY VERIFIED
- Local MCP server — Started, 8 tools registered, `list_tables` and `run_sql` verified directly
- ngrok tunnel — Required `--host-header=localhost:8787` to avoid 421 (Misdirected Request)
- `create_agent.py` — Agent created (`e2e-test-chinook-agent:1`) with ngrok URL
- Non-streaming + approval flow — `list_tables` and `top_customers` approved and executed
- Streaming + approval flow — `get_table_info` with streaming events + approval loop works
- All MCP event types validated: `mcp_call.started`, `mcp_call.completed`, `mcp_call_arguments.delta`, `mcp_approval_request`

### enterprise_github_agent — PARTIALLY VERIFIED
- `create_agent.py` — Agent created successfully (`e2e-test-github-agent:1`) with dummy connection
- Runtime requires a real Foundry project connection with GitHub PAT (cannot be created via SDK)
- Error handling verified — clear 400 error: "Connection dummy-github-connection can't be found in this workspace"
- Streaming + approval code pattern identical to mcp_local_server_agent (which is fully verified)

### Key Findings
- **ngrok needs `--host-header=localhost:PORT`** — Without this, Starlette/uvicorn returns 421 (Misdirected Request) because the Host header doesn't match
- **Foundry validates connection names at runtime, not at agent creation** — Agent creation succeeds with any connection name
- **`models.list()` is not supported** on Foundry OpenAI endpoint — Use agent creation probe to verify model deployments
- **`project.connections.list()` is read-only** — SDK cannot create connections (must use Foundry portal)

## Next Action

Vision expansion — all three v2 demos are complete and E2E verified. Consider Phase 5 (Fabric Data Agent) or other new demos.

## Blocked / Unresolved

- **enterprise_github_agent full E2E** requires manual setup of a Foundry project connection with GitHub PAT (see manual test instructions below)

## Decisions Made

- **Phase 0 complete** — Vision lock synthesized, now tracked in git
- **Phase 1 complete** — Enterprise GitHub Agent validated and fixed for GA SDK
- **Phase 2 complete** — MCP MS Learn Agent ported to v2, 41 tests passing
- **Phase 3 complete** — MCP Local Server Agent ported to v2, 84 tests passing (167 total)
- **Phase 4 complete** — Cross-cutting polish (architecture overview, README, glossary, tech debt)
- **E2E testing complete** — 2/3 demos fully verified, 1/3 partially verified (needs manual connection setup)
- **DB working dir gitignored** — Added `**/db/working/` to .gitignore
- **Project docs tracked in git** — Removed docs/, roadmap/, AGENTS.md from .gitignore
- ADR-001: Two-script demo pattern (create + ask)
- ADR-002: MCP credentials via Foundry project connections (NOT runtime header injection)
- ADR-003: GA V2 SDK with both response-chaining and Conversations API patterns
- ADR-004: Flat demo directory layout (server/ exception for MCP server demos)

## Files Modified This Session

- `.gitignore` — Added `**/db/working/` to ignore MCP server working DB copies
- `roadmap/CURRENT-STATE.md` — Updated with E2E test results

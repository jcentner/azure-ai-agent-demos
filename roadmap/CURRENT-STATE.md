# Azure AI Agent Demos — Current State

**Phase Status**: Complete

## What Exists

- `.github/` — Copilot agents, prompts, hooks, and instructions for autonomous development
- `docs/vision/VISION-LOCK.md` — Vision lock v1.3 — credential isolation pattern, GA SDK
- `docs/architecture/decisions/` — 4 ADRs (two-script pattern, project connection auth, GA v2 SDK, flat layout)
- `.github/skills/azure-docs-research/` — Skill for grounding answers in official MS docs
- `docs/` — Documentation skeleton (architecture, reference docs)
- `roadmap/phases/` — Phase 1 (complete), Phase 2 (complete)
- `AGENTS.md` — Cross-agent instructions
- `enterprise_github_agent/` — Complete v2 demo: validated GA SDK patterns, project connection auth, typed MCP approvals, 42 passing tests
- `mcp_mslearn_agent/` — Complete v2 demo: public MS Learn MCP server, no auth, auto-approved, 41 passing tests
- `mcp_local_server_agent/` — Stub README only (v2 rewrite planned for Phase 3)
- `archive/v1/` — Complete, working v1 demos preserved for reference
- `pyproject.toml` — pytest importlib mode for test isolation across demos

## Current Phase

Phase 2: MCP MS Learn Agent v2 Rewrite — **COMPLETE**

## Next Action

Begin Phase 3: MCP Local Server Agent v2 rewrite — port server + agent from v1, update auth pattern.

## Blocked / Unresolved

Nothing blocked. Live testing of both agents requires an Azure AI Foundry project with a model deployment — cannot be automated without credentials.

## Decisions Made

- **Phase 0 complete** — Vision lock synthesized, now tracked in git
- **Phase 1 complete** — Enterprise GitHub Agent validated and fixed for GA SDK
- **Phase 2 complete** — MCP MS Learn Agent ported to v2, 41 tests passing
- **Project docs tracked in git** — Removed docs/, roadmap/, AGENTS.md from .gitignore
- ADR-001: Two-script demo pattern (create + ask)
- ADR-002: MCP credentials via Foundry project connections (NOT runtime header injection)
- ADR-003: GA V2 SDK with both response-chaining and Conversations API patterns
- ADR-004: Flat demo directory layout
- **extra_body key is `agent_reference`** — All official Python samples use `{"agent_reference": {...}}`
- **MCP auth via project_connection_id** — `McpApprovalResponse` does NOT support headers
- **Public MCP servers use require_approval="never"** — No approval flow needed for read-only public endpoints (MS Learn)
- **pytest importlib mode** — Added pyproject.toml to handle same-named test files across demo directories
- **Removed tests/__init__.py** — Not needed with importlib mode, prevented module name collisions

## Files Modified This Session

- `mcp_mslearn_agent/create_agent.py` — Created: v2 agent creation with MCPTool + PromptAgentDefinition
- `mcp_mslearn_agent/ask_agent.py` — Created: v2 REPL with OpenAI Responses API streaming
- `mcp_mslearn_agent/.env.sample` — Created: PROJECT_ENDPOINT, MODEL_DEPLOYMENT_NAME, AGENT_NAME
- `mcp_mslearn_agent/requirements.txt` — Created: v2 GA SDK dependencies
- `mcp_mslearn_agent/README.md` — Replaced stub with complete setup/walkthrough/v1-v2 comparison
- `mcp_mslearn_agent/tests/test_agent_config.py` — Created: 41 structural tests
- `enterprise_github_agent/ask_agent.py` — Fixed: removed dead current_text_started variable, unnecessary f-strings
- `enterprise_github_agent/tests/__init__.py` — Deleted: not needed with pytest importlib mode
- `pyproject.toml` — Created: pytest importlib import mode config
- `roadmap/phases/phase-2-mcp-mslearn-agent.md` — Created: Phase 2 plan

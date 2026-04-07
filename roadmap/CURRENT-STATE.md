# Azure AI Agent Demos — Current State

**Phase Status**: Complete

## What Exists

- `.github/` — Copilot agents, prompts, hooks, and instructions for autonomous development
- `docs/vision/VISION-LOCK.md` — Vision lock v1.3 — credential isolation pattern, GA SDK
- `docs/architecture/decisions/` — 4 ADRs (two-script pattern, project connection auth, GA v2 SDK, flat layout)
- `.github/skills/azure-docs-research/` — Skill for grounding answers in official MS docs
- `docs/` — Documentation skeleton (architecture, reference docs)
- `roadmap/phases/phase-1-enterprise-github-agent.md` — Phase 1 plan (complete)
- `AGENTS.md` — Cross-agent instructions
- `enterprise_github_agent/` — Complete v2 demo: validated GA SDK patterns, project connection auth, typed MCP approvals, 42 passing tests
- `mcp_local_server_agent/` and `mcp_mslearn_agent/` — Stub READMEs only (v2 rewrites planned for Phases 2–3)
- `archive/v1/` — Complete, working v1 demos preserved for reference

## Current Phase

Phase 1: Enterprise GitHub Agent Demo — **COMPLETE**

## Next Action

Begin Phase 2: MCP MS Learn Agent v2 rewrite — port from v1, verify against GA SDK.

## Blocked / Unresolved

Nothing blocked. Live testing of the enterprise agent requires an Azure AI Foundry project with a model deployment and GitHub MCP project connection — cannot be automated without credentials.

## Decisions Made

- **Phase 0 complete** — Vision lock synthesized, now tracked in git
- **Phase 1 complete** — Enterprise GitHub Agent validated and fixed for GA SDK
- **Project docs tracked in git** — Removed docs/, roadmap/, AGENTS.md from .gitignore
- ADR-001: Two-script demo pattern (create + ask)
- ADR-002: MCP credentials via Foundry project connections (NOT runtime header injection)
- ADR-003: GA V2 SDK with both response-chaining and Conversations API patterns
- ADR-004: Flat demo directory layout
- **extra_body key is `agent_reference`** — All official Python samples use `{"agent_reference": {...}}`
- **MCP auth via project_connection_id** — `McpApprovalResponse` does NOT support headers

## Files Modified This Session

- `enterprise_github_agent/create_agent.py` — Fixed: added project_connection_id, GA SDK comments
- `enterprise_github_agent/ask_agent.py` — Fixed: extra_body key, typed McpApprovalResponse, removed header injection
- `enterprise_github_agent/requirements.txt` — Fixed: >=2.0.0 (GA, not beta)
- `enterprise_github_agent/.env.sample` — Fixed: MCP_CONNECTION_NAME replaces GITHUB_PAT
- `enterprise_github_agent/README.md` — Fixed: project connection auth, security model, related docs
- `enterprise_github_agent/tests/test_agent_config.py` — Created: 42 structural tests
- `docs/architecture/decisions/002-runtime-only-auth-injection.md` — Updated: project connections
- `docs/architecture/decisions/003-v2-sdk-and-openai-responses-api.md` — Updated: both conversation patterns
- `docs/vision/VISION-LOCK.md` — Updated: v1.3, credential isolation, "What Exists" table
- `.gitignore` — Fixed: track docs/, roadmap/, AGENTS.md

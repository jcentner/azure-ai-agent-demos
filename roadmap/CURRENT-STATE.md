# Azure AI Agent Demos — Current State

**Phase Status**: Complete

## What Exists

- `.github/` — Copilot agents, prompts, hooks, and instructions for autonomous development
- `docs/vision/VISION-LOCK.md` — Synthesized vision lock (v1.1) — broadened scope beyond MCP, GA SDK
- `docs/architecture/decisions/` — 4 initial ADRs (two-script pattern, runtime auth, GA v2 SDK, flat layout)
- `.github/skills/azure-docs-research/` — Skill for grounding answers in official MS docs
- `docs/` — Documentation skeleton (architecture, reference docs)
- `roadmap/phases/phase-1-enterprise-github-agent.md` — Phase 1 plan with 5 slices
- `AGENTS.md` — Cross-agent instructions
- `enterprise_github_agent/` — Prototype v2 code (`create_agent.py`, `ask_agent.py`) — needs validation
- `mcp_local_server_agent/` and `mcp_mslearn_agent/` — Stub READMEs only (v2 rewrites planned for Phases 2–3)
- `archive/v1/` — Complete, working v1 demos preserved for reference

## Current Phase

Phase 1: Enterprise GitHub Agent Demo

## Next Action

Begin Phase 1, Slice 1.1: Validate the existing enterprise_github_agent prototype against GA v2 SDK docs (use azure-docs-research skill). Determine if the code is functional or needs rewrite.

## Blocked / Unresolved

Nothing yet.

## Decisions Made

- **Phase 0 complete** — Vision lock synthesized from repo evidence
- ADR-001: Two-script demo pattern (create + ask)
- ADR-002: Runtime-only auth injection for MCP credentials
- ADR-003: GA V2 SDK with Conversations and Responses API
- ADR-004: Flat demo directory layout
- Phase ordering: Enterprise GitHub Agent first (most complex, has prototype), then MS Learn (simplest port), then Local Server (most complex port)
- **V2 SDK is GA** — `azure-ai-projects>=2.0.0`, not beta. Updated all references.
- **Scope broadened** — Repo is for Azure AI Agent demos generally, not just MCP demos. Vision lock updated to v1.1.

## Files Modified This Session

- `docs/vision/VISION-LOCK.md` — Synthesized from template to v1.0, then updated to v1.1 (broadened scope, GA SDK)
- `docs/architecture/decisions/001-two-script-demo-pattern.md` — Created
- `docs/architecture/decisions/002-runtime-only-auth-injection.md` — Created
- `docs/architecture/decisions/003-v2-sdk-and-openai-responses-api.md` — Created, then updated for GA SDK with full API surface
- `docs/architecture/decisions/004-flat-demo-directory-layout.md` — Created
- `docs/architecture/decisions/README.md` — Updated ADR index
- `roadmap/phases/phase-1-enterprise-github-agent.md` — Created, updated for GA SDK
- `roadmap/CURRENT-STATE.md` — Updated
- `.github/skills/azure-docs-research/SKILL.md` — Created (docs grounding skill)

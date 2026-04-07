# Azure AI Agent Demos — Vision Lock

**Version**: v1.3
**Last updated**: 2026-04-07

## Problem Statement

Azure AI Foundry provides powerful agent capabilities — tool use, code execution, MCP integrations, grounding, and more — but developers lack clear, runnable examples showing how to build, configure, and wire up these agents for real scenarios. The original v1 demos targeted the now-superseded Agents v1 SDK; the GA v2 SDK (`azure-ai-projects`) introduces breaking changes to agent creation, conversation management, and tool integration patterns that require new demo code.

## Target User

Azure developers learning to build AI agents with Azure AI Foundry — specifically those who:
- Want hands-on examples of agent capabilities (MCP integrations, Code Interpreter, file search, grounding, and more)
- Need practical patterns for streaming output, tool call visibility, and runtime auth
- Are following an accompanying walkthrough video/content series

## Core Concept

A collection of **self-contained Python demos**, each showcasing a distinct Azure AI Foundry Agent capability or integration pattern. Demos span MCP server connections, Code Interpreter, file search, grounding, and other tool types. Every demo follows a consistent two-script pattern (`create_agent.py` + `ask_agent.py`) with streaming console output and clear documentation. The v1 archive is preserved for reference; active development targets the GA v2 SDK and new Foundry portal.

## Explicit Non-Goals

- **Production-ready code** — No mTLS, IP allowlists, key rotation, multi-tenant isolation, or production hardening
- **Web UI** — All demos are terminal-based interactive REPLs
- **Language variety** — Python only; no TypeScript/C#/.NET variants
- **Agent orchestration** — No multi-agent workflows or agent-to-agent communication
- **OAuth flows** — Demos use PATs or bearer tokens for simplicity where auth is needed

## Product Constraints

- Every demo must be runnable independently with its own README, requirements, and `.env.sample`
- Auth credentials (where applicable) must never be persisted on agent definitions — runtime injection only
- V1 code in `archive/v1/` must remain untouched (referenced by existing walkthrough content)
- Demos require an Azure AI Foundry project with public network access enabled

## Technical Constraints

- **Language**: Python 3.11+
- **Primary SDK**: `azure-ai-projects` (GA v2 API surface)
- **Auth**: `azure-identity` (DefaultAzureCredential) for Azure; PATs/bearer tokens where MCP or external services require them
- **Config**: `python-dotenv` for environment variable management
- **MCP transport**: Streamable HTTP (not stdio) — required for remote agent↔server connections (applies to MCP demos only)
- **Models**: Azure-hosted OpenAI models (configurable per demo via `MODEL_DEPLOYMENT_NAME`)

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│  Demo Directory (e.g., enterprise_github_agent/) │
│                                                  │
│  create_agent.py ─── AIProjectClient             │
│    └─ PromptAgentDefinition + tool(s)            │
│    └─ Persists agent name to .agent_name file    │
│                                                  │
│  ask_agent.py ─── Interactive REPL               │
│    └─ Loads agent name from .agent_name file     │
│    └─ OpenAI Responses API (streaming)           │
│    └─ Runtime auth injection (where needed)      │
│    └─ Prints streamed text + tool call events    │
│                                                  │
│  .env.sample ─── Required environment variables  │
│  requirements.txt ─── Python dependencies        │
│  README.md ─── Setup + walkthrough instructions  │
└─────────────────────────────────────────────────┘
         │                          │
         ▼                          ▼
  Azure AI Foundry              External Services
  (agent hosting,           (MCP servers, APIs,
   model deployment)         sandboxed tools)
```

### V2 SDK Patterns

See [ADR-003](../architecture/decisions/003-v2-sdk-and-openai-responses-api.md) for detailed API surface. Key patterns:
- Agent creation via `PromptAgentDefinition` with versioned agents
- OpenAI Responses API for streaming conversations
- Tool classes from `azure.ai.projects.models` (`MCPTool`, `CodeInterpreterTool`, `FileSearchTool`, etc.)

## What Exists Today

| Component | State | Verified |
|-----------|-------|----------|
| V1 MS Learn agent (`archive/v1/mcp_mslearn_agent/`) | Complete, working code | Yes |
| V1 Local server agent (`archive/v1/mcp_local_server_agent/`) | Complete, working code — full MCP server + agent | Yes |
| V2 Enterprise GitHub agent (`enterprise_github_agent/`) | Validated against GA SDK, fixed auth and API patterns | Compiles, not live-tested |
| V2 MS Learn agent (`mcp_mslearn_agent/`) | Complete v2 demo: public MCP server, auto-approved, 41 tests | Compiles, not live-tested |
| V2 Local server agent (`mcp_local_server_agent/`) | Complete v2 demo: custom MCP server, approval flow, 84 tests | Compiles, not live-tested |
| Documentation skeleton | Empty templates in `docs/` | Yes |
| Enterprise agent plan (`.github/prompts/plan-enterpriseGitHubAgent.prompt.md`) | Detailed plan, partially diverges from actual code | Yes |

## Success Criteria

| Criterion | Status |
|-----------|--------|
| Enterprise GitHub Agent demo runs end-to-end (create → chat → issue → code → PR) | Not started |
| MCP MS Learn Agent rewritten for v2 SDK and runs end-to-end | Not started |
| MCP Local Server Agent rewritten for v2 SDK and runs end-to-end | Not started |
| Fabric Data Agent demo queries lakehouse data via natural language | Not started |
| Multi-Tool Knowledge Worker demo combines File Search + Code Interpreter + Web Search | Not started |
| Browser Automation demo controls a real browser through natural language | Not started |
| Each demo has complete README with prerequisites, setup, and walkthrough | Not started |
| Each demo has `.env.sample` with all required variables | Not started |
| Architecture docs reflect actual implementation | Not started |

## Architecture Invariants

1. **Two-script pattern** — Every demo has `create_agent.py` (provision once) + `ask_agent.py` (interactive REPL). No exceptions.
2. **Credential isolation** — Where external services require credentials, they are stored in Foundry project connections and referenced by name, never embedded in agent definitions.
3. **Streaming with tool visibility** — All demos show streaming token output with visible tool call indicators.
4. **Self-contained demos** — Each demo directory contains everything needed to run it independently.
5. **Flat file layout** — Demo directories use flat structure (no nested `agent/` or `server/` subdirectories), except where a separate MCP server is required.

## Where We're Going

Priority-ordered phases:

1. **Phase 1**: Enterprise GitHub Agent — validate and complete the v2 prototype (MCP + Code Interpreter), write tests, full README
2. **Phase 2**: MCP MS Learn Agent v2 rewrite — port from v1, verify against GA SDK
3. **Phase 3**: MCP Local Server Agent v2 rewrite — port server + agent from v1, update auth pattern
4. **Phase 4**: Cross-cutting polish — `.env.sample` files, architecture docs, shared utilities (if warranted)
5. **Phase 5**: Fabric Data Agent — natural language queries against Fabric lakehouse via `MicrosoftFabricPreviewTool`
6. **Phase 6**: Multi-Tool Knowledge Worker — File Search + Code Interpreter + Web Search composing three built-in tools
7. **Phase 7**: Browser Automation Agent — `BrowserAutomationPreviewTool` controlling a real browser via natural language

## Out of Scope

- Production deployment patterns (mTLS, key rotation, IP allowlists)
- Copilot Studio / Teams bot integration
- Multi-agent orchestration
- Non-Python SDK implementations
- Automated CI/CD pipelines for the demos themselves

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| V2 SDK GA introduces breaking changes in future releases | Low | Medium | Pin versions, document API surface assumptions, keep v1 archive as fallback |
| Enterprise agent prototype needs full rewrite despite existing code | Medium | Medium | Validate prototype first before rewriting from scratch |
| GitHub MCP server endpoint changes | Low | Medium | Document endpoint version, test in CI |
| Foundry portal UI changes invalidate screenshots/instructions | Medium | Low | Use text-based instructions, defer screenshots to final polish |
| Fabric/Browser Automation preview tools change before GA | Medium | Medium | Pin SDK version, document preview status prominently in READMEs |

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-04-07 | Synthesized from repo evidence during Phase 0 |
| v1.1 | 2026-04-07 | Broadened scope beyond MCP-only; updated SDK from beta to GA per human feedback |
| v1.2 | 2026-04-07 | Added Phases 5-7: Fabric Data Agent, Multi-Tool Knowledge Worker, Browser Automation |
| v1.3 | 2026-04-07 | Architecture Invariant #2 updated: "credential isolation" via project connections (not runtime header injection). Enterprise agent prototype validated. |

# Azure AI Agent Demos — Architecture Overview

## Overview

A collection of self-contained Python demos and explicitly scoped training suites for Azure AI
Foundry Agents. Standalone demos follow a consistent two-script pattern. Training suites may use
staged scripts and shared setup when the labs form one learning sequence. The v1 archive is
preserved for reference; active development targets the GA v2 SDK.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Demo Directory (e.g., enterprise_github_agent/)         │
│                                                          │
│  create_agent.py                                         │
│    └─ AIProjectClient → agents.create_version()          │
│    └─ PromptAgentDefinition + tool(s)                    │
│    └─ Saves agent name to .agent_name                    │
│                                                          │
│  ask_agent.py                                            │
│    └─ project.get_openai_client()                        │
│    └─ openai.responses.create() with agent_reference     │
│    └─ Streaming + tool call visibility                   │
│    └─ previous_response_id for conversation continuity   │
│                                                          │
│  .env.sample / requirements.txt / README.md              │
│  tests/test_agent_config.py                              │
└─────────────────────────────────────────────────────────┘
         │                          │
         ▼                          ▼
  Azure AI Foundry              External Services
  (agent hosting,           (MCP servers, APIs,
   model deployment)         sandboxed tools)
```

## Key Components

| Component | Description | Status |
|-----------|-------------|--------|
| `enterprise_github_agent/` | GitHub MCP + Code Interpreter, approval flow, project connection auth | Complete (42 tests) |
| `mcp_mslearn_agent/` | Public MS Learn MCP server, auto-approved, no auth | Complete (41 tests) |
| `mcp_local_server_agent/` | Custom Chinook SQLite MCP server + agent, approval flow, optional auth | Complete (84 tests) |
| `training/l200-tools/` | Connected Toolbox, Azure AI Search, and Foundry IQ labs | Complete |
| `archive/v1/` | Original v1 demos (deprecated SDK), preserved for reference | Archived |

## Technology Choices

| Choice | Decision | Reference |
|--------|----------|-----------|
| Language | Python 3.11+ | Vision lock |
| Primary SDK | `azure-ai-projects>=2.0.0` (GA v2 API) | [ADR-003](decisions/003-v2-sdk-and-openai-responses-api.md) |
| Auth | `azure-identity` (DefaultAzureCredential) | Vision lock |
| MCP credentials | Foundry project connections (`project_connection_id`) | [ADR-002](decisions/002-runtime-only-auth-injection.md) |
| Agent creation | `PromptAgentDefinition` + `create_version()` | [ADR-003](decisions/003-v2-sdk-and-openai-responses-api.md) |
| Conversations | OpenAI Responses API via `project.get_openai_client()` | [ADR-003](decisions/003-v2-sdk-and-openai-responses-api.md) |
| Demo structure | Two-script pattern (`create_agent.py` + `ask_agent.py`) | [ADR-001](decisions/001-two-script-demo-pattern.md) |
| Directory layout | Flat per demo, `server/` exception for MCP servers | [ADR-004](decisions/004-flat-demo-directory-layout.md) |
| Training layout | Shared setup with staged, connected lab directories | [ADR-005](decisions/005-connected-training-suites.md) |
| Config | `python-dotenv` (`.env` files) | Vision lock |
| MCP transport | Streamable HTTP (not stdio) | Vision lock |

## Architectural Invariants

1. **Two-script pattern** — Every standalone demo has `create_agent.py` + `ask_agent.py`
2. **Credential isolation** — External credentials stored in Foundry project connections, never on agent definitions
3. **Streaming with tool visibility** — All demos show streaming tokens with visible tool call indicators
4. **Self-contained demos** — Each directory has everything needed to run independently
5. **Flat file layout** — No nested subdirectories, except `server/` where a custom MCP server is required

Training suites under `training/` are a documented exception. They may share one environment and
use staged scripts or cross-lab dependencies. They must provide a top-level setup guide, pinned
dependencies, sample configuration, a preflight check, and per-lab READMEs.

## Data Flow

1. **Agent creation**: `create_agent.py` → `AIProjectClient.agents.create_version()` → Agent stored in Foundry → `.agent_name` file written
2. **Conversation**: `ask_agent.py` → `project.get_openai_client()` → `openai.responses.create(stream=True)` → Streamed events → Console output
3. **MCP tool calls**: Agent → Foundry service → MCP server (via `server_url`) → Tool execution → Response streamed back
4. **MCP approval**: Agent requests → Approval event → `ask_agent.py` auto-approves → Agent continues

## Related Docs

- [ADRs](decisions/)
- [Vision Lock](../vision/VISION-LOCK.md)
- [Open Questions](../reference/open-questions.md)

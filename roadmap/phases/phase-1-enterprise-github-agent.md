# Phase 1: Enterprise GitHub Agent Demo

## Goal

Deliver a complete, runnable Enterprise GitHub Agent demo that connects an Azure AI Foundry Agent to the official GitHub MCP Server + Code Interpreter. The demo should show a complete workflow: create a GitHub issue, write code to solve it, and open a PR — all through natural language in a streaming console REPL.

## Prerequisites

- Azure AI Foundry project with public network access
- Model deployment (configurable via `MODEL_DEPLOYMENT_NAME`)
- GitHub Personal Access Token with `repo` scope
- Python 3.11+
- `azure-ai-projects>=2.0.0` (GA)

## Existing State

A substantial prototype exists in `enterprise_github_agent/` with both `create_agent.py` and `ask_agent.py`. CURRENT-STATE marks it as "needs full rewrite from scratch" but the code may be functional. First task is to **validate** the existing prototype before deciding to rewrite.

## Slices

### 1.1 — Validate existing prototype
- Read and understand current `create_agent.py` and `ask_agent.py`
- Compare against GA v2 SDK docs (consult MS docs via azure-docs-research skill) to verify API calls are correct
- Identify what works, what's wrong, and what's missing
- Decision: rewrite from scratch or fix what exists

### 1.2 — Implement/fix create_agent.py
- Agent creation with `PromptAgentDefinition`, `MCPTool` (GitHub), `CodeInterpreterTool` using GA SDK (`azure-ai-projects>=2.0.0`)
- Agent name persistence to `.agent_name` file
- Clear console output confirming creation
- `.env.sample` with all required variables

### 1.3 — Implement/fix ask_agent.py
- Interactive REPL loading agent name from `.agent_name` file
- Conversations API (`conversations.create()` / `conversations.items.create()`) + Responses API streaming
- MCP approval handling with runtime PAT injection
- Streaming output: text deltas, MCP call indicators, Code Interpreter indicators
- Clean error handling for common failures (missing env vars, auth errors)

### 1.4 — README and documentation
- Complete README with prerequisites, PAT setup, Foundry setup, walkthrough
- `.env.sample` with documented variables
- Architecture notes in `docs/architecture/overview.md`

### 1.5 — Testing
- Structural/unit tests for agent configuration (no live Azure calls required)
- Verify imports resolve correctly
- Lint/type check passes

## Done When

- `create_agent.py` runs successfully against a configured Azure AI Foundry project
- `ask_agent.py` streams responses with visible tool calls
- GitHub MCP tools (issues, PRs, code) work through the agent
- Code Interpreter executes Python in sandboxed environment
- README provides complete walkthrough from zero to working demo
- Tests pass

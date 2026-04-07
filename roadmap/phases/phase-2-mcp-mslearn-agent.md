# Phase 2: MCP MS Learn Agent v2 Rewrite

## Goal

Port the v1 MCP Microsoft Learn agent to the GA v2 SDK (`azure-ai-projects>=2.0.0`), following the same patterns established in Phase 1 (Enterprise GitHub Agent).

## Key Differences from Enterprise Agent

- **No auth required** — MS Learn MCP server is public (`https://learn.microsoft.com/api/mcp`)
- **No Code Interpreter** — Simple search/retrieve agent (MCP tool only)
- **No approval flow** — `require_approval="never"` since all operations are read-only
- **No project connection** — No `project_connection_id` or `MCP_CONNECTION_NAME` needed

## Deliverables

1. `mcp_mslearn_agent/create_agent.py` — V2 agent creation with `PromptAgentDefinition` + `MCPTool`
2. `mcp_mslearn_agent/ask_agent.py` — V2 interactive REPL using OpenAI Responses API (streaming)
3. `mcp_mslearn_agent/.env.sample` — Required environment variables
4. `mcp_mslearn_agent/requirements.txt` — GA v2 SDK dependencies
5. `mcp_mslearn_agent/README.md` — Complete setup and walkthrough
6. `mcp_mslearn_agent/tests/test_agent_config.py` — Structural tests (AST + SDK validation)

## V2 Patterns to Follow

- `AIProjectClient` with `DefaultAzureCredential`
- `PromptAgentDefinition` + `MCPTool` for agent creation via `create_version()`
- Agent name saved to `.agent_name` (not `.agent_id`)
- `project.get_openai_client()` → `openai.responses.create()` with `agent_reference` in `extra_body`
- Response chaining via `previous_response_id`
- Streaming with visible MCP tool call events

## Success Criteria

- All structural tests pass
- Code compiles and follows GA SDK patterns
- README has complete setup instructions
- Self-contained demo directory (ADR-004)

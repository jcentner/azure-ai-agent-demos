# Azure AI Agent Demos — Glossary

Project-specific terms and their definitions.

**ADR** — Architecture Decision Record. Stored in `docs/architecture/decisions/`.

**Agent reference** — The `extra_body` parameter in `openai.responses.create()` that tells the Foundry service which agent to use: `{"agent_reference": {"name": agent_name, "type": "agent_reference"}}`.

**Chinook** — A sample SQLite database of a music store (artists, albums, customers, invoices). Used by the `mcp_local_server_agent` demo.

**Credential isolation** — Architecture invariant requiring that external credentials (PATs, bearer tokens) are stored in Foundry project connections, never embedded in agent definitions or source code. See ADR-002.

**FastMCP** — A Python library from the MCP SDK for building MCP servers with minimal boilerplate. Uses Starlette under the hood.

**Foundry project connection** — An Azure AI Foundry feature that stores credentials (API keys, tokens) and makes them available to agents via `project_connection_id` without exposing them in code.

**GA V2 SDK** — The `azure-ai-projects>=2.0.0` package, the general availability release of the Azure AI Projects SDK. Replaces the deprecated `azure-ai-agents` package.

**MCP** — Model Context Protocol. An open standard for connecting AI models to external tools and data sources via a JSON-RPC-based protocol.

**MCP approval flow** — The pattern where an agent requests approval before calling an MCP tool (`mcp_approval_request` event), and the client responds with `mcp_approval_response`. Used when `require_approval="always"`.

**PromptAgentDefinition** — The v2 SDK class for defining an agent's model, instructions, and tools. Used with `agents.create_version()`.

**Response chaining** — Conversation continuity pattern using `previous_response_id` on each `openai.responses.create()` call. Each response chains to the previous one.

**Streamable HTTP** — The MCP transport protocol used for remote agent↔server connections. Runs over standard HTTP (not stdio).

**Two-script pattern** — Architecture invariant: every demo has `create_agent.py` (provision once) + `ask_agent.py` (interactive REPL). See ADR-001.

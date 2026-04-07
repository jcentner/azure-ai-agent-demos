# ADR-002: MCP Credentials Via Project Connections

## Status

Accepted (updated 2026-04-07 — corrected from header injection to project connections)

## Context

MCP servers (GitHub, local services) require authentication. Azure AI Foundry supports multiple MCP auth methods: project connections (key-based), Microsoft Entra, and OAuth identity passthrough. For demos handling personal access tokens, we need a secure, documented approach that keeps credentials off agent definitions.

The original approach proposed injecting headers via MCP approval responses, but this is **not supported by the API** — the `McpApprovalResponse` type only has `approve`, `approval_request_id`, `type`, `id`, and `reason` fields. No `headers` parameter exists.

## Decision

MCP credentials are stored in **Foundry project connections** and referenced by name on the MCPTool:

- **V2 pattern**: Create a project connection in the Foundry portal with the credential (e.g., `Authorization: Bearer <PAT>`). Reference it via `project_connection_id` on the `MCPTool`. Set `require_approval="always"` for visibility and control.
- **V1 pattern** (archived): Used `mcp.update_headers()` + `tool_resources` at run creation time.

Credentials are NOT stored on agent definitions — only a connection reference (by name) is stored.

## Consequences

- **Positive**: Credentials managed centrally in Foundry project connections, not scattered across agent definitions
- **Positive**: Approval flow still works — users approve/deny each MCP tool call
- **Positive**: Follows the officially documented and supported pattern
- **Trade-off**: Requires portal setup to create the project connection (documented in each demo's README)
- **Trade-off**: Credential is shared across all users of the project (use OAuth identity passthrough for per-user auth)

# Azure AI Agent Demos — Tech Debt Tracker

Known compromises, shortcuts, and deferred improvements. Each item should have a reason it was accepted and a rough priority for resolution.

## Format

```
### TD-NNN: Title

**Priority**: High / Medium / Low
**Introduced**: Phase/session where this was introduced
**Description**: What the shortcut is.
**Why accepted**: Why this was OK for now.
**Resolution path**: What it would take to fix properly.
```

## Tech Debt Items

### TD-001: Server errors.py is dead code

**Priority**: Low
**Introduced**: Phase 3
**Description**: `mcp_local_server_agent/server/errors.py` defines custom exception classes that are never imported. In v1, `auth.py` imported `UnauthorizedError` from it, but v2 uses Starlette's `JSONResponse` directly.
**Why accepted**: Harmless dead code; may be useful if custom error handling is added later.
**Resolution path**: Delete the file or add imports where needed.

### TD-002: Server `_single_statement` has false positives for semicolons in string literals

**Priority**: Low
**Introduced**: Phase 3 (inherited from v1)
**Description**: The SQL statement validator in `server/db/client.py` rejects queries with semicolons inside string literals (e.g., `SELECT * FROM t WHERE name = 'test;test'`).
**Why accepted**: The agent-generated SQL won't typically include semicolons in string literals. This is a demo, not production code.
**Resolution path**: Use a proper SQL parser or at least handle quoted strings.

### TD-003: MCP_PATH config is loaded but not used

**Priority**: Low
**Introduced**: Phase 3 (inherited from v1)
**Description**: `server/config.py` loads and validates `MCP_PATH`, but `app.py` hardcodes `/mcp` for both the auth middleware and FastMCP. Changing `MCP_PATH` in `.env` has no effect.
**Why accepted**: The default `/mcp` path is the convention. Making it configurable adds complexity without demo value.
**Resolution path**: Either wire `cfg.MCP_PATH` through to FastMCP and the middleware, or remove it from config.

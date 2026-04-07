# ADR-004: Flat Demo Directory Layout

## Status

Accepted

## Context

V1 used nested subdirectories (e.g., `mcp_local_server_agent/agent/` and `mcp_local_server_agent/server/`). This added navigational complexity for beginners without providing meaningful architectural benefit for small demo scripts.

## Decision

Each v2 demo uses a flat file layout at the top level:
```
demo_name/
  create_agent.py
  ask_agent.py
  README.md
  requirements.txt
  .env.sample
```

Exception: If a demo includes a separate MCP server (e.g., the local server agent), server code lives in a `server/` subdirectory within the demo folder, since it's a separate runnable component.

## Consequences

- **Positive**: Simpler navigation for demo users
- **Positive**: Each demo is visually scannable in a file listing
- **Negative**: If shared utilities emerge across demos, they'll need a separate location
- **Accepted**: YAGNI — we'll add shared utilities only if warranted by actual duplication

# server/surface/prompts.py
from __future__ import annotations

import re
from mcp.server.fastmcp import FastMCP


def _render_explanation(sql: str) -> str:
    s = (sql or "").strip()
    if not s:
        return "Empty SQL."
    head = re.split(r"\s+", s, maxsplit=6)
    head = " ".join(head[:6])
    if s.lower().startswith("select"):
        return f"This appears to be a SELECT query (starts with: {head!r}). It reads data without modifying the database."
    if s.lower().startswith(("insert", "update", "delete", "replace")):
        return f"This appears to be a WRITE query (starts with: {head!r}). It modifies data in the database."
    return f"This looks like a SQL statement (starts with: {head!r})."


def register(mcp: FastMCP) -> None:
    @mcp.prompt()
    def explain_query_purpose(sql: str) -> str:
        """
        Return a simple, deterministic NL explanation of what a SQL statement *appears* to do.
        """
        return _render_explanation(sql)

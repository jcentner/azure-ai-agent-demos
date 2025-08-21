# server/surface/schema.py
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ..db.client import Database


def register(mcp: FastMCP, db: Database) -> None:
    @mcp.resource("schema://current")
    def schema_snapshot() -> dict:
        with db.transaction() as con:
            tables = [
                r[0]
                for r in con.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;"
                ).fetchall()
            ]
            out = {"tables": []}
            for t in tables:
                cols = [
                    {
                        "name": r["name"],
                        "type": r["type"],
                        "pk": bool(r["pk"]),
                        "not_null": bool(r["notnull"]),
                        "default": r["dflt_value"],
                    }
                    for r in con.execute(f"PRAGMA table_info('{t}');").fetchall()
                ]
                fks = [
                    {"from": r["from"], "to_table": r["table"], "to_column": r["to"]}
                    for r in con.execute(f"PRAGMA foreign_key_list('{t}');").fetchall()
                ]
                out["tables"].append({"name": t, "columns": cols, "foreign_keys": fks})
            return out

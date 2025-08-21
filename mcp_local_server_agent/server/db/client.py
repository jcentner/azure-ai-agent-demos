# server/db/client.py
from __future__ import annotations

import re
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Database:
    path: Path

    def connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        return con

    @contextmanager
    def transaction(self):
        con = self.connect()
        try:
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()


_semicolon_re = re.compile(r";")
_select_re = re.compile(r"^\s*select\b", re.IGNORECASE)
_write_re = re.compile(r"^\s*(insert|update|delete|replace)\b", re.IGNORECASE)


def _single_statement(sql: str) -> bool:
    # Allow trailing semicolon only
    s = sql.strip()
    if ";" in s[:-1]:
        return False
    return True


def is_select(sql: str) -> bool:
    return _select_re.match(sql or "") is not None and _single_statement(sql)


def is_write(sql: str) -> bool:
    return _write_re.match(sql or "") is not None and _single_statement(sql)


def execute_read(con: sqlite3.Connection, sql: str, params: dict | None = None) -> tuple[list[str], list[list[Any]]]:
    cur = con.execute(sql, params or {})
    cols = [c[0] for c in cur.description] if cur.description else []
    rows = [list(map(_jsonify_cell, row)) for row in cur.fetchall()]
    cur.close()
    return cols, rows


def execute_write(con: sqlite3.Connection, sql: str, params: dict | None = None, max_rows: int = 10_000) -> int:
    before = con.total_changes
    cur = con.execute(sql, params or {})
    cur.close()
    affected = con.total_changes - before
    if affected > max_rows:
        raise ValueError(f"Write would affect {affected} rows (> {max_rows}).")
    return affected


def _jsonify_cell(v: Any) -> Any:
    # SQLite returns bytes for blobs; convert to repr for JSON-ability.
    if isinstance(v, (bytes, bytearray)):
        return f"<{len(v)} bytes>"
    return v

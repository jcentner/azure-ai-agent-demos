# server/db/init.py
from __future__ import annotations

from pathlib import Path
import shutil
from .client import Database


def ensure_working_copy(*, base_path: Path, working_dir: Path, persist: bool) -> tuple[Path, Path]:
    working_dir.mkdir(parents=True, exist_ok=True)
    working_path = working_dir / "chinook.work.sqlite"

    if not persist or not working_path.exists():
        shutil.copy2(base_path, working_path)

    return base_path, working_path


def integrity_check(db: Database) -> None:
    with db.transaction() as con:
        row = con.execute("PRAGMA integrity_check;").fetchone()
        if not row or row[0] != "ok":
            raise RuntimeError(f"SQLite integrity check failed: {row[0] if row else 'unknown'}")

        # simple smoke query (count tables)
        con.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        ).fetchone()

# server/config.py
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _as_bool(v: str | None, default: bool) -> bool:
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Config:
    PORT: int
    MCP_PATH: str
    DB_BASE_PATH: Path
    DB_WORKING_DIR: Path
    PERSIST_WORKING_COPY: bool
    LOCAL_MCP_TOKEN: str | None
    LOG_LEVEL: str

    def validate(self) -> None:
        if not self.MCP_PATH.startswith("/"):
            raise ValueError("MCP_PATH must start with '/'.")
        if not self.DB_BASE_PATH.exists():
            raise FileNotFoundError(
                f"DB base file not found at {self.DB_BASE_PATH}. "
                "Place Chinook SQLite (e.g., chinook.db) at this path."
            )
        self.DB_WORKING_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> Config:
    port = int(os.getenv("PORT", "8787"))
    path = os.getenv("MCP_PATH", "/mcp")
    base = Path(os.getenv("DB_BASE_PATH", "server/db/chinook.db"))
    working_dir = Path(os.getenv("DB_WORKING_DIR", "server/db/working"))
    persist = _as_bool(os.getenv("PERSIST_WORKING_COPY"), False)
    token = os.getenv("LOCAL_MCP_TOKEN")
    log_level = os.getenv("LOG_LEVEL", "info")

    cfg = Config(
        PORT=port,
        MCP_PATH=path,
        DB_BASE_PATH=base,
        DB_WORKING_DIR=working_dir,
        PERSIST_WORKING_COPY=persist,
        LOCAL_MCP_TOKEN=token,
        LOG_LEVEL=log_level,
    )
    cfg.validate()
    return cfg

# server/app.py
from __future__ import annotations

import logging

from starlette.applications import Starlette
import uvicorn

from mcp.server.fastmcp import FastMCP

from .config import load_config
from .logging import setup_logging, new_request_id
from .db.init import ensure_working_copy, integrity_check
from .db.client import Database
from .auth import BearerAuthMiddleware
from .surface import tools as surface_tools
from .surface import schema as surface_schema
from .surface import prompt as surface_prompt


def build_mcp(db: Database) -> FastMCP:
    mcp = FastMCP(name="Chinook SQLite MCP Server")

    # Register everything in one place
    surface_tools.register(mcp, db)
    surface_schema.register(mcp, db)
    surface_prompt.register(mcp)

    return mcp


def main():
    cfg = load_config()
    setup_logging(cfg.LOG_LEVEL)

    base_path, working_path = ensure_working_copy(
        base_path=cfg.DB_BASE_PATH,
        working_dir=cfg.DB_WORKING_DIR,
        persist=cfg.PERSIST_WORKING_COPY,
    )
    logging.getLogger(__name__).info("DB base=%s working=%s", base_path, working_path)

    db = Database(working_path)
    integrity_check(db)

    mcp = build_mcp(db)

    # Build the inner Starlette app from MCP and use it directly so its lifespan runs.
    app: Starlette = mcp.streamable_http_app()

    # Apply auth middleware on the MCP paths (e.g., /mcp ...).
    app.add_middleware(
        BearerAuthMiddleware,
        token=cfg.LOCAL_MCP_TOKEN,
        mount_path="/mcp",
    )

    logging.getLogger(__name__).info(
        "Starting MCP server on http://0.0.0.0:%d/mcp", cfg.PORT
    )
    new_request_id()
    # Ensure lifespan runs on this app by giving it directly to Uvicorn.
    uvicorn.run(app, host="0.0.0.0", port=cfg.PORT, lifespan="auto")


if __name__ == "__main__":
    main()

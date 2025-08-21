#!/usr/bin/env python3
# agent/create_agent.py
"""
create_agent.py — Create an Azure AI Foundry Agent with your Chinook MCP tool.

- Connects to your Azure AI Foundry project using DefaultAzureCredential
- Creates an agent with the Chinook MCP tool attached (no secrets persisted)
- Saves the new agent's id to ./.agent_id for ask_agent.py to use

Env (read from .env via python-dotenv):
- PROJECT_ENDPOINT           (required)
- MODEL_DEPLOYMENT_NAME      (required)
- AGENT_NAME                 (optional; default 'mcp_local_server_agent')
- MCP_SERVER_URL             (required for agent running in Azure; e.g., https://<sub>.ngrok.app/mcp)
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv, find_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import McpTool


def resolve_server_url_or_warn(raw: str | None) -> tuple[str, bool]:
    """
    Return (url, ok). If MCP_SERVER_URL is missing, return an intentionally invalid URL
    and ok=False so callers can warn/pause but still proceed for demo purposes.
    Ensures the returned URL ends with '/mcp'.
    """
    if not raw or not raw.strip():
        return "https://example.invalid/mcp", False
    raw = raw.strip()
    if not raw.rstrip("/").endswith("/mcp"):
        raw = raw.rstrip("/") + "/mcp"
    return raw, True


def main():
    # Load repo-root .env regardless of CWD
    load_dotenv(find_dotenv())

    endpoint = os.environ["PROJECT_ENDPOINT"]
    model = os.environ["MODEL_DEPLOYMENT_NAME"]
    agent_name = os.environ.get("AGENT_NAME", "mcp_local_server_agent")

    # MCP server URL (must be reachable from Azure; localhost will not work)
    server_url, has_server_url = resolve_server_url_or_warn(os.getenv("MCP_SERVER_URL"))
    if not has_server_url:
        print("[config] ERROR: MCP_SERVER_URL is not set.")
        print("         When running in Azure, a localhost URL will NOT be reachable.")
        print("         Set MCP_SERVER_URL to your public MCP endpoint (e.g., your ngrok https URL + '/mcp').")
        try:
            input("Press Enter to CONTINUE with an intentionally invalid URL (this will fail), or Ctrl+C to abort...")
        except (EOFError, KeyboardInterrupt):
            # Non-interactive or user aborted; continue anyway (creates agent with invalid URL).
            pass

    # Connect to the Azure AI Foundry project
    project = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())

    # Define the Chinook MCP tool "shape"
    chinook_mcp = McpTool(
        server_label="chinook",
        server_url=server_url,
    )

    # Minimal instructions to guide tool use
    instructions = (
        "You can use the Chinook SQLite MCP tool to inspect the database schema and perform database operations. "
        "Prefer calling MCP tools when the user asks about Chinook data: list tables, run SQL "
        "(use run_sql for SELECTs and run_sql_write for INSERT/UPDATE/DELETE), and helper tools like "
        "insert_customer, update_customer_email, create_invoice, and top_customers."
    )

    # Create the agent (no secrets persisted; headers added at runtime in ask_agent.py)
    with project:
        agent = project.agents.create_agent(
            model=model,
            name=agent_name,
            instructions=instructions,
            tools=chinook_mcp.definitions,
        )

    # Save the agent id so the interactive script can find it
    Path(".agent_id").write_text(agent.id + "\n", encoding="utf-8")
    print(f"Created agent: {agent.id} (name='{agent_name}'). Wrote .agent_id")
    print(f"MCP server URL attached to the agent definition: {server_url}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
create_agent.py — Create an Azure AI Foundry Agent with your local Chinook MCP server.

Uses the GA Foundry SDK (azure-ai-projects>=2.0.0) with:
- Custom MCP server (Chinook SQLite) exposed via ngrok
- Optional Foundry project connection for MCP auth (bearer token)
- Configurable model deployment

The MCP server URL must be publicly reachable from Azure (use ngrok).
Saves the agent name to ./.agent_name for ask_agent.py to use.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    MCPTool,
)


def main():
    load_dotenv()

    # Required config
    endpoint = os.environ["PROJECT_ENDPOINT"]
    model = os.environ["MODEL_DEPLOYMENT_NAME"]
    agent_name = os.environ.get("AGENT_NAME", "mcp-local-chinook-demo")

    # MCP server URL — must be reachable from Azure (ngrok HTTPS URL + /mcp)
    server_url = os.environ.get("MCP_SERVER_URL", "").strip()
    if not server_url:
        print("ERROR: MCP_SERVER_URL is not set.")
        print("  The Azure agent service needs a public URL to reach your local MCP server.")
        print("  Start your server, run ngrok, then set MCP_SERVER_URL=https://<sub>.ngrok.app/mcp")
        sys.exit(1)

    # Optional: Foundry project connection for MCP auth (stores bearer token)
    mcp_connection = os.environ.get("MCP_CONNECTION_NAME", "").strip() or None

    # Connect to the Azure AI Foundry project
    project = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    # Agent instructions — guide tool use for the Chinook database
    instructions = (
        "You can use the Chinook SQLite MCP tool to inspect the database schema and "
        "perform database operations. Prefer calling MCP tools when the user asks about "
        "Chinook data: list tables, run SQL (use run_sql for SELECTs and run_sql_write "
        "for INSERT/UPDATE/DELETE), and helper tools like insert_customer, "
        "update_customer_email, create_invoice, and top_customers."
    )

    # Define MCP tool — require approval since server does writes
    mcp_kwargs = {
        "server_label": "chinook",
        "server_url": server_url,
        "require_approval": "always",
    }
    if mcp_connection:
        mcp_kwargs["project_connection_id"] = mcp_connection

    tools = [MCPTool(**mcp_kwargs)]

    # Create agent using GA Foundry SDK pattern
    with project:
        agent = project.agents.create_version(
            agent_name=agent_name,
            definition=PromptAgentDefinition(
                model=model,
                instructions=instructions,
                tools=tools,
            ),
        )

    # Save agent name (new API uses name + version, not just ID)
    Path(".agent_name").write_text(agent.name + "\n", encoding="utf-8")
    print(f"Created agent: name='{agent.name}' version={agent.version} id={agent.id}")
    print(f"MCP server URL: {server_url}")
    if mcp_connection:
        print(f"MCP auth: via project connection '{mcp_connection}'")
    else:
        print("MCP auth: none (MCP_CONNECTION_NAME not set)")
    print("Wrote .agent_name")
    print("\nNext: Run 'python ask_agent.py' to chat with the agent.")


if __name__ == "__main__":
    main()

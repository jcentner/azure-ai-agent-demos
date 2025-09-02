#!/usr/bin/env python3
"""
create_agent.py — Minimal: create an Azure AI Foundry Agent with the Microsoft Learn MCP server.

- Connects to your Azure AI Foundry project using DefaultAzureCredential
- Creates an agent with the Learn MCP tool attached
- Saves the new agent's id to ./.agent_id for ask_agent.py to use
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import McpTool

LEARN_MCP_URL = "https://learn.microsoft.com/api/mcp"  # public, no auth required

def main():
    load_dotenv()

    # Required config
    endpoint = os.environ["PROJECT_ENDPOINT"]
    model = os.environ["MODEL_DEPLOYMENT_NAME"]
    agent_name = os.environ.get("AGENT_NAME", "mcp-learn-readonly-demo")

    # Connect to the Azure AI Foundry project
    project = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())

    # Define the Microsoft Learn MCP server
    learn_mcp = McpTool(
        server_label="learn",
        server_url=LEARN_MCP_URL,
    )

    # Minimal instructions to nudge tool use
    instructions = (
        "You can use the Microsoft Learn MCP tool to search and retrieve Learn documentation. "
        "When the user asks about Azure/Microsoft docs, call the MCP tools and include links."
    )

    with project:
        agent = project.agents.create_agent(
            model=model,
            name=agent_name,
            instructions=instructions,
            tools=learn_mcp.definitions,
        )

    Path(".agent_id").write_text(agent.id + "\n", encoding="utf-8")
    print(f"Created agent: {agent.id} (name='{agent_name}'). Wrote .agent_id")

if __name__ == "__main__":
    main()
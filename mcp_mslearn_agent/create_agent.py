#!/usr/bin/env python3
"""
create_agent.py — Create an Azure AI Foundry Agent with the Microsoft Learn MCP server.

Uses the GA Foundry SDK (azure-ai-projects>=2.0.0) with:
- Microsoft Learn MCP server (public, no auth required)
- Configurable model deployment

Saves the agent name to ./.agent_name for ask_agent.py to use.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    MCPTool,
)

# Microsoft Learn MCP server — public, no auth required
LEARN_MCP_URL = "https://learn.microsoft.com/api/mcp"


def main():
    load_dotenv()

    # Required config
    endpoint = os.environ["PROJECT_ENDPOINT"]
    model = os.environ["MODEL_DEPLOYMENT_NAME"]
    agent_name = os.environ.get("AGENT_NAME", "mcp-mslearn-demo-agent")

    # Connect to the Azure AI Foundry project
    project = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    # Agent instructions — encourage using MCP tools for documentation queries
    instructions = (
        "You are a documentation assistant with access to Microsoft Learn via MCP tools. "
        "When the user asks about Azure, Microsoft, or any technical topic covered by "
        "Microsoft Learn, use the MCP tools to search and retrieve documentation. "
        "Always include links to the source articles in your responses."
    )

    # Define MCP tool — no auth needed, auto-approve all calls (read-only operations)
    tools = [
        MCPTool(
            server_label="learn",
            server_url=LEARN_MCP_URL,
            require_approval="never",
        ),
    ]

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
    print("Wrote .agent_name")
    print("\nNext: Run 'python ask_agent.py' to chat with the agent.")


if __name__ == "__main__":
    main()

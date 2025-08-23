#!/usr/bin/env python3
"""
create_agent.py — Minimal: create an Azure AI Foundry Agent with an MCP tool.

- Connects to your Azure AI Foundry project using DefaultAzureCredential
- Creates an agent with the GitHub MCP tool attached
- Saves the new agent's id to ./.agent_id for ask_agent.py to use

Note:
- Auth headers (PAT/OAuth) are NOT persisted on the agent; they are attached
  only at run-time in ask_agent.py via tool_resources.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import McpTool

def main():
    load_dotenv()

    # Required config
    endpoint = os.environ["PROJECT_ENDPOINT"]
    model = os.environ["MODEL_DEPLOYMENT_NAME"]
    agent_name = os.environ.get("AGENT_NAME", "mcp-github-readonly-demo")

    # Connect to the Azure AI Foundry project (credential can also be a subscription key)
    project = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())

    # Define the GitHub MCP tool "shape" 
    github_mcp = McpTool(
        server_label="github",
        server_url="https://api.githubcopilot.com/mcp/",
    )

    # Instructions inform the agent of the tool
    instructions = (
        "You can use the GitHub MCP tool to read repositories and issues. "
        "When the user asks for GitHub data, call the MCP tools."
    )

    # Create the agent 
    with project:
        agent = project.agents.create_agent(
            model=model,
            name=agent_name,
            instructions=instructions,
            tools=github_mcp.definitions,  # <-- no secrets persisted
        )

    # Save the agent id so the interactive script can find it
    Path(".agent_id").write_text(agent.id + "\n", encoding="utf-8")
    print(f"Created agent: {agent.id} (name='{agent_name}'). Wrote .agent_id")

if __name__ == "__main__":
    main()

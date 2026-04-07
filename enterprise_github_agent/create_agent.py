#!/usr/bin/env python3
"""
create_agent.py — Create an Azure AI Foundry Agent with GitHub MCP + Code Interpreter.

Uses the GA Foundry SDK (azure-ai-projects>=2.0.0) with:
- Official GitHub MCP server (https://api.githubcopilot.com/mcp/)
- Code Interpreter for writing and testing code
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
    CodeInterpreterTool,
)

# GitHub MCP server (official remote server - default toolset)
GITHUB_MCP_URL = "https://api.githubcopilot.com/mcp/"


def main():
    load_dotenv()

    # Required config
    endpoint = os.environ["PROJECT_ENDPOINT"]
    model = os.environ["MODEL_DEPLOYMENT_NAME"]
    mcp_connection = os.environ["MCP_CONNECTION_NAME"]
    agent_name = os.environ.get("AGENT_NAME", "enterprise-github-agent")

    # Connect to the Azure AI Foundry project
    project = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    # Agent instructions - light guidance, let the agent discover workflows naturally
    instructions = """You are a developer assistant with GitHub integration and code execution capabilities.

You have access to:
1. **GitHub tools** via MCP - you can create issues, read repositories, create branches, push files, and open pull requests.
2. **Code Interpreter** - you can write, test, and debug code in a sandboxed Python environment.

When helping with development tasks:
- Use Code Interpreter to write and validate code before pushing to GitHub
- Create meaningful commit messages and PR descriptions
- Reference issue numbers in commits/PRs when applicable (e.g., "Fixes #123")

You work with the user's GitHub repositories using their personal access token for authentication."""

    # Define tools for the agent
    # GitHub PAT is stored in a Foundry project connection (not on the agent definition)
    tools = [
        MCPTool(
            server_label="github",
            server_url=GITHUB_MCP_URL,
            require_approval="always",
            project_connection_id=mcp_connection,
        ),
        CodeInterpreterTool(),
    ]

    # Create agent using new Foundry SDK pattern
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

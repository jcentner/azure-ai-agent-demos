#!/usr/bin/env python3
"""
agent_mcp_github.py - Minimal read-only GitHub MCP demo script.

This script connects to an Azure AI Foundry project, creates an agent with the MCP tool,
asks the agent to list the five most recent open issues in a given repository,
and prints the assistant's reply.
"""

import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import McpTool

def main():
    # Required environment variables
    project_endpoint = os.environ["PROJECT_ENDPOINT"]
    model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]
    github_pat = os.environ.get("GITHUB_PAT")

    # Create the project client using DefaultAzureCredential (requires az login)
    project = AIProjectClient(endpoint=project_endpoint, credential=DefaultAzureCredential())

    # Define the GitHub MCP tool (no secrets here; server URL is constant)
    github_mcp_url = "https://api.githubcopilot.com/mcp/"
    mcp_tool = McpTool(server_label="github", server_url=github_mcp_url)

    # Build a simple agent with MCP tool attached
    with project:
        agent = project.agents.create_agent(
            model=model_deployment_name,
            name="mcp-github-readonly-demo",
            instructions=(
                "You can use the GitHub MCP tool to read repositories and issues. "
                "When the user asks for GitHub data, call the MCP tools."
            ),
            tools=mcp_tool.definitions,
        )

        # Create a new thread and a user prompt
        thread = project.agents.threads.create()
        # Change this repository to one you can read with your PAT
        repo = "microsoft/vscode"
        user_prompt = f"List the 5 most recent open issues in {repo} with their titles and numbers."
        project.agents.messages.create(thread_id=thread.id, role="user", content=user_prompt)

        # Attach the PAT header only at run time (not persisted on the agent)
        if github_pat:
            mcp_tool.update_headers("Authorization", f"Bearer {github_pat}")
        # Skip approval prompts for a smoother demo
        mcp_tool.set_approval_mode("never")

        # Run the agent and wait for completion
        run = project.agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent.id,
            tool_resources=mcp_tool.resources,
        )

        # Print the assistant's response
        messages = project.agents.messages.list(thread_id=thread.id)
        for msg in reversed(list(messages)):
            if msg.role == "assistant":
                # Print any text parts from the assistant message
                for part in msg.content or []:
                    if getattr(part, "type", None) in ("output_text", "text"):
                        print(getattr(part, "text", getattr(part, "value", "")))
                break

if __name__ == "__main__":
    main()

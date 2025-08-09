#!/usr/bin/env python3
"""
agent_mcp_github_bing.py - GitHub MCP + Bing Search demo.

This script demonstrates how to create an Azure AI Foundry agent that uses both
the GitHub MCP tool (read-only) and Grounding with Bing Search. It biases the
model to use Microsoft Learn and Microsoft-owned GitHub repositories when answering
questions about Azure AI Foundry.
"""

import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import McpTool, BingGroundingTool

def main():
    # Read environment variables for endpoints and credentials
    project_endpoint = os.environ["PROJECT_ENDPOINT"]
    model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]
    bing_connection_id = os.environ["AZURE_BING_CONNECTION_ID"]
    github_pat = os.environ.get("GITHUB_PAT")

    project = AIProjectClient(endpoint=project_endpoint, credential=DefaultAzureCredential())

    # Define tools: GitHub MCP and Bing Grounding
    mcp_tool = McpTool(server_label="github", server_url="https://api.githubcopilot.com/mcp/")
    bing_tool = BingGroundingTool(connection_id=bing_connection_id)

    # Instructions to bias Bing to official Microsoft docs/repos
    instructions = (
        "You are an Azure AI Foundry helper.\n"
        "\n"
        "When the user asks about Azure AI Foundry or Azure AI Agents:\n"
        "- Use Grounding with Bing Search to fetch up-to-date info.\n"
        "- Bias your queries toward official sources, such as:\n"
        "  site:learn.microsoft.com/azure/ai-foundry OR site:learn.microsoft.com/azure/ai-services/agents\n"
        "  and Microsoft GitHub orgs (github.com/microsoft and github.com/Azure-Samples).\n"
        "- Prefer Microsoft Learn and Microsoft-owned GitHub repositories.\n"
        "- When the user asks for repo issues/PRs or file contents, use the GitHub MCP tool.\n"
        "\n"
        "If you cite links, include the titles and URLs. Use concise, actionable answers."
    )

    with project:
        # Create the agent with both tools attached
        agent = project.agents.create_agent(
            model=model_deployment_name,
            name="mcp-github-bing-foundry-demo",
            instructions=instructions,
            tools=bing_tool.definitions + mcp_tool.definitions,
        )

        # Create a thread and user message
        thread = project.agents.threads.create()
        user_prompt = (
            "What's the current guidance for using Azure AI Foundry Agent Service with MCP? "
            "Answer briefly with links to Microsoft Learn pages. "
            "Also list the 3 most recent open issues (number + title) in microsoft/azure-ai-projects."
        )
        project.agents.messages.create(thread_id=thread.id, role="user", content=user_prompt)

        # Attach GitHub PAT header at run time (not persisted on agent)
        if github_pat:
            mcp_tool.update_headers("Authorization", f"Bearer {github_pat}")
        mcp_tool.set_approval_mode("never")

        # Run and wait for completion
        run = project.agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=agent.id,
            tool_resources=mcp_tool.resources,
        )

        # Print assistant response and citations if available
        messages = project.agents.messages.list(thread_id=thread.id)
        for msg in reversed(list(messages)):
            if msg.role == "assistant":
                for part in msg.content or []:
                    if getattr(part, "type", None) in ("output_text", "text"):
                        print(getattr(part, "text", getattr(part, "value", "")))
                # Print URL citations from Bing if provided
                anns = getattr(msg, "url_citation_annotations", None) or []
                if anns:
                    print("\nCitations:")
                    for a in anns:
                        try:
                            print(f"- {a.url_citation.title}: {a.url_citation.url}")
                        except Exception:
                            pass
                break

if __name__ == "__main__":
    main()

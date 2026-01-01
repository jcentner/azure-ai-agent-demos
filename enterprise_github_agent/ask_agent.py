#!/usr/bin/env python3
"""
ask_agent.py — Interactive chat with the Enterprise GitHub Agent.

Uses the new Foundry SDK (azure-ai-projects --pre) with:
- OpenAI Responses API for conversation
- GitHub MCP tool with PAT authentication (injected at runtime)
- Code Interpreter for code execution
- Streaming output with visible tool calls

Auth behavior:
- GitHub PAT is passed at runtime via MCP headers - NOT persisted on the agent
- Requires GITHUB_PAT environment variable
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# GitHub MCP server (official remote server)
GITHUB_MCP_URL = "https://api.githubcopilot.com/mcp/"


def print_response_details(response):
    """Print details about tool usage from the response."""
    # Check for tool calls in the response output
    if hasattr(response, "output") and response.output:
        for item in response.output:
            item_type = getattr(item, "type", None)

            # Handle MCP tool calls
            if item_type == "mcp_call":
                server = getattr(item, "server_label", "?")
                name = getattr(item, "name", "?")
                print(f"  [mcp_call] server={server} tool={name}")

            # Handle Code Interpreter calls
            elif item_type == "code_interpreter_call":
                code = getattr(item, "input", "")
                if code:
                    preview = code[:100] + ("..." if len(code) > 100 else "")
                    print(f"  [code_interpreter] {preview}")


def main():
    load_dotenv()

    # Required config
    endpoint = os.environ["PROJECT_ENDPOINT"]
    github_pat = os.environ.get("GITHUB_PAT")

    if not github_pat:
        print("ERROR: GITHUB_PAT environment variable is required.")
        print("Create a GitHub Personal Access Token with 'repo' scope at:")
        print("  https://github.com/settings/tokens")
        sys.exit(1)

    # Get agent name from file or environment
    agent_name = os.getenv("AGENT_NAME")
    if not agent_name:
        agent_name_file = Path(".agent_name")
        if agent_name_file.exists():
            agent_name = agent_name_file.read_text(encoding="utf-8").strip()
        else:
            print("ERROR: No agent name found. Run 'python create_agent.py' first.")
            sys.exit(1)

    # Optional: target repo for context
    target_repo = os.environ.get("GITHUB_REPO", "")

    # Connect to the project
    project = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    # Print startup info
    print("=" * 60)
    print("Enterprise GitHub Agent (New Foundry Experience)")
    print("=" * 60)
    print(f"Agent: {agent_name}")
    print(f"GitHub MCP: {GITHUB_MCP_URL}")
    if target_repo:
        print(f"Target repo: {target_repo}")
    print("\nTools available:")
    print("  - GitHub MCP (repos, issues, pull_requests, users, context)")
    print("  - Code Interpreter (Python execution)")
    print("\nCommands: /exit to quit")
    print("=" * 60)

    # Suggest demo prompts
    print("\nTry these prompts:")
    if target_repo:
        print(f'  "Create an issue in {target_repo} for adding a hello world function"')
        print(f'  "Write a Python hello world function, then push it to {target_repo}"')
    else:
        print('  "List my GitHub repositories"')
        print('  "Create an issue in <owner>/<repo> for adding a greeting function"')
    print()

    # Get OpenAI client from project
    with project:
        openai_client = project.get_openai_client()

        # Create a conversation for multi-turn chat
        conversation = openai_client.conversations.create()
        print(f"[conversation] id={conversation.id}\n")

        while True:
            try:
                user_input = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting.")
                break

            if not user_input:
                continue
            if user_input.lower() in {"/exit", "exit", "quit"}:
                print("Goodbye.")
                break

            # Create response using the agent with conversation context
            # GitHub PAT is injected via extra headers for MCP authentication
            try:
                print("[thinking...]")

                # Use streaming for real-time output
                stream = openai_client.responses.create(
                    input=user_input,
                    conversation=conversation.id,
                    extra_body={
                        "agent": {
                            "name": agent_name,
                            "type": "agent_reference",
                        },
                        # Inject GitHub PAT for MCP tool authentication
                        "tool_config": {
                            "mcp": {
                                "github": {
                                    "headers": {
                                        "Authorization": f"Bearer {github_pat}",
                                    },
                                },
                            },
                        },
                    },
                    stream=True,
                )

                # Stream the response
                print("\n[assistant]")
                full_response = None
                for event in stream:
                    # Handle different event types
                    event_type = getattr(event, "type", None)

                    if event_type == "response.output_text.delta":
                        # Stream text deltas
                        delta = getattr(event, "delta", "")
                        print(delta, end="", flush=True)

                    elif event_type == "response.mcp_call.started":
                        server = getattr(event, "server_label", "?")
                        name = getattr(event, "name", "?")
                        print(f"\n  [mcp_call] server={server} tool={name}")

                    elif event_type == "response.code_interpreter_call.started":
                        print("\n  [code_interpreter] executing...")

                    elif event_type == "response.code_interpreter_call.code.delta":
                        code_delta = getattr(event, "delta", "")
                        print(code_delta, end="", flush=True)

                    elif event_type == "response.completed":
                        full_response = getattr(event, "response", None)

                print("\n")  # Newline after response

                # Print any additional tool details from completed response
                if full_response:
                    print_response_details(full_response)

            except Exception as e:
                print(f"\n[error] {type(e).__name__}: {e}")
                print("Check that the agent exists and your credentials are valid.")


if __name__ == "__main__":
    main()

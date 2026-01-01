#!/usr/bin/env python3
"""
ask_agent.py — Interactive chat with the Enterprise GitHub Agent.

Uses the new Foundry SDK (azure-ai-projects --pre) with:
- OpenAI Responses API for conversation
- GitHub MCP tool with PAT authentication (injected via approval headers)
- Code Interpreter for code execution
- Streaming output with visible tool calls

Auth behavior:
- GitHub PAT is injected at runtime via MCP approval response headers
- PAT is NOT persisted on the agent definition
- Requires GITHUB_PAT environment variable
"""

import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient


def get_mcp_approval_requests(response, github_pat: str) -> list[dict[str, Any]]:
    """Extract MCP approval requests from response output and build approval responses with auth headers."""
    approvals: list[dict[str, Any]] = []
    if hasattr(response, "output") and response.output:
        for item in response.output:
            if getattr(item, "type", None) == "mcp_approval_request":
                server_label = getattr(item, "server_label", "?")
                tool_name = getattr(item, "name", "?")
                item_id = getattr(item, "id", None)
                if item_id:
                    print(f"\n  ⏳ [mcp_approval] server={server_label} tool={tool_name}")
                    # Build approval with GitHub PAT in headers for authentication
                    # This injects the PAT at runtime - never stored on the agent
                    approval: dict = {
                        "type": "mcp_approval_response",
                        "approve": True,
                        "approval_request_id": item_id,
                    }
                    # Add auth headers for GitHub MCP server
                    if server_label == "github":
                        approval["headers"] = {"Authorization": f"Bearer {github_pat}"}
                    approvals.append(approval)
    return approvals


def stream_response(openai_client, request_kwargs: dict) -> Any:
    """Stream a response and print events in real-time. Returns the completed response."""
    stream = openai_client.responses.create(**request_kwargs, stream=True)
    
    full_response = None
    current_text_started = False
    
    for event in stream:
        event_type = getattr(event, "type", None)
        
        # Text streaming
        if event_type == "response.output_text.delta":
            if not current_text_started:
                current_text_started = True
            delta = getattr(event, "delta", "")
            print(delta, end="", flush=True)
        
        # MCP tool call started
        elif event_type == "response.mcp_call.started":
            server = getattr(event, "server_label", "?")
            name = getattr(event, "name", "?")
            print(f"\n  🔧 [mcp_call] server={server} tool={name}", flush=True)
        
        # MCP tool call completed
        elif event_type == "response.mcp_call.completed":
            print(f"  ✓ [mcp_call] completed", flush=True)
        
        # Code Interpreter started
        elif event_type == "response.code_interpreter_call.started":
            print(f"\n  🐍 [code_interpreter] executing...", flush=True)
        
        # Code Interpreter code delta (show code being written)
        elif event_type == "response.code_interpreter_call.code.delta":
            code_delta = getattr(event, "delta", "")
            print(code_delta, end="", flush=True)
        
        # Code Interpreter completed
        elif event_type == "response.code_interpreter_call.completed":
            print(f"\n  ✓ [code_interpreter] completed", flush=True)
        
        # Response completed - capture the full response
        elif event_type == "response.completed":
            full_response = getattr(event, "response", None)
    
    return full_response


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
    if target_repo:
        print(f"Target repo: {target_repo}")
    print("\nTools available:")
    print("  - GitHub MCP (repos, issues, pull_requests, users, context)")
    print("  - Code Interpreter (Python execution)")
    print("\nMCP tool calls require approval (auto-approved for demo)")
    print("Commands: /exit to quit")
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

        # Track conversation context via previous_response_id
        previous_response_id = None

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

            try:
                print("[thinking...]")

                # Build the request - use previous_response_id for conversation continuity
                request_kwargs = {
                    "input": user_input,
                    "extra_body": {
                        "agent": {
                            "name": agent_name,
                            "type": "agent_reference",
                        },
                    },
                }
                if previous_response_id:
                    request_kwargs["previous_response_id"] = previous_response_id

                # Stream initial response (may require MCP approval)
                print("\n[assistant]")
                response = stream_response(openai_client, request_kwargs)

                # Handle MCP approval requests in a loop
                while response:
                    approvals = get_mcp_approval_requests(response, github_pat)
                    if not approvals:
                        break

                    print(f"  ✅ [approving {len(approvals)} MCP tool call(s)...]")
                    # Send approval and stream continuation
                    approval_kwargs = {
                        "input": approvals,
                        "previous_response_id": response.id,
                        "extra_body": {
                            "agent": {
                                "name": agent_name,
                                "type": "agent_reference",
                            },
                        },
                    }
                    response = stream_response(openai_client, approval_kwargs)

                # Save for conversation continuity
                if response:
                    previous_response_id = response.id
                
                print("\n")  # Clean newline after response

            except Exception as e:
                print(f"\n[error] {type(e).__name__}: {e}")
                print("Check that the agent exists and your credentials are valid.")
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    main()

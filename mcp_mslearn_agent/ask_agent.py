#!/usr/bin/env python3
"""
ask_agent.py — Interactive chat with the Microsoft Learn MCP Agent.

Uses the GA Foundry SDK (azure-ai-projects>=2.0.0) with:
- OpenAI Responses API for conversation
- Microsoft Learn MCP tool (public, no auth, auto-approved)
- Streaming output with visible tool calls

Auth behavior:
- No auth is required for the Microsoft Learn MCP server
- MCP tool calls are auto-approved (require_approval="never" set at creation)
"""

import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient


def stream_response(openai_client, request_kwargs: dict) -> Any:
    """Stream a response and print events in real-time. Returns the completed response."""
    stream = openai_client.responses.create(**request_kwargs, stream=True)

    full_response = None

    for event in stream:
        event_type = getattr(event, "type", None)

        # Text streaming
        if event_type == "response.output_text.delta":
            delta = getattr(event, "delta", "")
            print(delta, end="", flush=True)

        # MCP tool call started
        elif event_type == "response.mcp_call.started":
            server = getattr(event, "server_label", "?")
            name = getattr(event, "name", "?")
            print(f"\n  🔧 [mcp_call] server={server} tool={name}", flush=True)

        # MCP tool call completed
        elif event_type == "response.mcp_call.completed":
            print("  ✓ [mcp_call] completed", flush=True)

        # Response completed - capture the full response
        elif event_type == "response.completed":
            full_response = getattr(event, "response", None)

    return full_response


def main():
    load_dotenv()

    # Required config
    endpoint = os.environ["PROJECT_ENDPOINT"]

    # Get agent name from file or environment
    agent_name = os.getenv("AGENT_NAME")
    if not agent_name:
        agent_name_file = Path(".agent_name")
        if agent_name_file.exists():
            agent_name = agent_name_file.read_text(encoding="utf-8").strip()
        else:
            print("ERROR: No agent name found. Run 'python create_agent.py' first.")
            sys.exit(1)

    # Connect to the project
    project = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    # Print startup info
    print("=" * 60)
    print("Microsoft Learn MCP Agent (New Foundry Experience)")
    print("=" * 60)
    print(f"Agent: {agent_name}")
    print("\nTools available:")
    print("  - Microsoft Learn MCP (search and retrieve documentation)")
    print("\nMCP tool calls are auto-approved (read-only operations)")
    print("Commands: /exit to quit")
    print("=" * 60)

    # Suggest demo prompts
    print("\nTry these prompts:")
    print('  "Find docs on Azure Functions triggers and bindings"')
    print('  "What is Azure Cosmos DB indexing? Include links."')
    print('  "Search Microsoft Learn for Azure App Service deployment options"')
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
                        "agent_reference": {
                            "name": agent_name,
                            "type": "agent_reference",
                        },
                    },
                }
                if previous_response_id:
                    request_kwargs["previous_response_id"] = previous_response_id

                # Stream the response
                print("\n[assistant]")
                response = stream_response(openai_client, request_kwargs)

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

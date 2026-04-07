#!/usr/bin/env python3
"""
ask_agent.py — Interactive chat with the Chinook MCP Agent.

Uses the GA Foundry SDK (azure-ai-projects>=2.0.0) with:
- OpenAI Responses API for conversation
- Chinook MCP tool with approval flow (auto-approved for demo)
- Streaming output with visible tool calls

Auth behavior:
- If MCP_CONNECTION_NAME was set at agent creation, the Foundry project connection
  provides the bearer token to the MCP server automatically.
- MCP tool calls require approval (auto-approved for demo convenience).
"""

import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from openai.types.responses.response_input_param import McpApprovalResponse


def get_mcp_approval_requests(response) -> list[McpApprovalResponse]:
    """Extract MCP approval requests from response output and build approval responses."""
    approvals: list[McpApprovalResponse] = []
    if hasattr(response, "output") and response.output:
        for item in response.output:
            if getattr(item, "type", None) == "mcp_approval_request":
                server_label = getattr(item, "server_label", "?")
                tool_name = getattr(item, "name", "?")
                item_id = getattr(item, "id", None)
                if item_id:
                    print(f"\n  ⏳ [mcp_approval] server={server_label} tool={tool_name}")
                    approvals.append(
                        McpApprovalResponse(
                            type="mcp_approval_response",
                            approve=True,
                            approval_request_id=item_id,
                        )
                    )
    return approvals


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
    print("Chinook MCP Agent (New Foundry Experience)")
    print("=" * 60)
    print(f"Agent: {agent_name}")
    print("\nTools available:")
    print("  - Chinook SQLite MCP (list_tables, get_table_info, run_sql,")
    print("    run_sql_write, insert_customer, update_customer_email,")
    print("    top_customers, create_invoice)")
    print("\nMCP tool calls require approval (auto-approved for demo)")
    print("Commands: /exit to quit")
    print("=" * 60)

    # Suggest demo prompts
    print("\nTry these prompts:")
    print('  "List all tables in the database"')
    print('  "Show the top 5 customers by spending"')
    print('  "Create a new customer named Test User with email test@example.com"')
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

                # Stream initial response (may require MCP approval)
                print("\n[assistant]")
                response = stream_response(openai_client, request_kwargs)

                # Handle MCP approval requests in a loop
                while response:
                    approvals = get_mcp_approval_requests(response)
                    if not approvals:
                        break

                    print(f"  ✅ [approving {len(approvals)} MCP tool call(s)...]")
                    # Send approval and stream continuation
                    approval_kwargs = {
                        "input": approvals,
                        "previous_response_id": response.id,
                        "extra_body": {
                            "agent_reference": {
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
                print("Check that the agent exists, your MCP server is running, and credentials are valid.")
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    main()

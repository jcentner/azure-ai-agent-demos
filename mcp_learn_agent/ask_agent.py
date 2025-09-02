#!/usr/bin/env python3
"""
ask_agent.py — Minimal interactive chat loop using the Microsoft Learn MCP server.

What it shows:
- How to stream a run and see message tokens + tool call steps
- A tiny REPL: type a prompt, see streaming output, '/exit' to quit

Auth behavior:
- No auth is required for the Microsoft Learn MCP server.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import (
    McpTool,
    AgentEventHandler,
    ThreadMessage,
    MessageDeltaChunk,
    RunStep,
)

LEARN_MCP_URL = "https://learn.microsoft.com/api/mcp"  # public, no auth required

# --- Minimal event handler to show what the agent is doing -----------------
class ConsoleEvents(AgentEventHandler):
    """Print run status, token deltas, and basic MCP tool call details."""

    def on_thread_run(self, run):
        print(f"\n[run] id={run.id} status={getattr(run, 'status', None)}")

    def on_thread_message(self, message: ThreadMessage):
        print(f"[message] role={getattr(message, 'role', '?')} id={message.id} status={getattr(message, 'status', None)}")

    def on_message_delta(self, delta: MessageDeltaChunk):
        # Stream assistant tokens live
        if getattr(delta, "text", None):
            print(delta.text, end="", flush=True)

    def on_run_step(self, step: RunStep):
        # Print when steps complete; include basic MCP tool call info if present
        print(f"\n[step] id={step.id} type={getattr(step, 'type', None)} status={getattr(step, 'status', None)}")
        details = getattr(step, "step_details", None)
        if details and getattr(details, "type", None) == "tool_calls":
            for i, tc in enumerate(getattr(details, "tool_calls", []) or [], 1):
                tc_type = getattr(tc, "type", None)
                print(f"  [tool_call {i}] type={tc_type}")
                mcp = getattr(tc, "mcp_tool", None)
                if mcp:
                    print(f"    mcp.server_label={getattr(mcp, 'server_label', None)} name={getattr(mcp, 'name', None)}")

def main():
    load_dotenv()

    endpoint = os.environ["PROJECT_ENDPOINT"]
    agent_id = os.getenv("AGENT_ID") or Path(".agent_id").read_text(encoding="utf-8").strip()

    # Connect to the project
    project = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())

    # Rebuild the MCP tool (no headers needed)
    mcp = McpTool(server_label="learn", server_url=LEARN_MCP_URL)
    # If you later need headers or toggles, you would set them here:
    # mcp.update_headers("X-Some-Header", "value")

    # Create a single thread for the chat session
    with project:
        thread = project.agents.threads.create()
        print("Chat ready. Ask about Microsoft Learn docs (e.g., 'Find docs on Azure Functions triggers'), or '/exit' to quit.\n")

        while True:
            try:
                user = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting.")
                break

            if not user:
                continue
            if user.lower() in {"/exit", "exit", "quit"}:
                print("Goodbye.")
                break

            # Add the user message to the thread
            project.agents.messages.create(thread_id=thread.id, role="user", content=user)

            # Stream the run so you can see tokens + tool calls live
            handler = ConsoleEvents()
            with project.agents.runs.stream(
                thread_id=thread.id,
                agent_id=agent_id,
                event_handler=handler,
                #tool_resources=mcp.resources,   # if you needed auth, you would add it here
            ) as stream:
                handler.until_done()  # block until completion

            print()  # add a newline after the streamed reply

if __name__ == "__main__":
    main()

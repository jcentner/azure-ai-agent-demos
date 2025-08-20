#!/usr/bin/env python3
"""
ask_agent.py — Minimal interactive chat loop that prints what the agent is doing.

What it shows:
- How to attach GitHub MCP auth (OAuth or PAT) at run-time 
- How to stream a run and see message tokens + tool call steps
- A tiny REPL: type a prompt, see streaming output, '/exit' to quit

Auth behavior:
- If GITHUB_OAUTH_TOKEN is set, it's used.
- Else if GITHUB_PAT is set, it's used.
- Else, the run will proceed but MCP calls will fail due to missing auth.
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


def pick_token() -> tuple[str | None, str | None]:
    """
    Prefer OAuth token if present, otherwise PAT. Returns (token, source_env_name).
    If neither is set, returns (None, None).
    """
    oauth = os.getenv("GITHUB_OAUTH_TOKEN")
    if oauth:
        return oauth, "GITHUB_OAUTH_TOKEN"
    pat = os.getenv("GITHUB_PAT")
    if pat:
        return pat, "GITHUB_PAT"
    return None, None


def main():
    load_dotenv()

    endpoint = os.environ["PROJECT_ENDPOINT"]
    # Agent id comes from .agent_id (created by create_agent.py), or env override
    agent_id = os.getenv("AGENT_ID") or Path(".agent_id").read_text(encoding="utf-8").strip()

    # Connect to the project
    project = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())

    # Build the MCP tool and attach auth headers AT RUN TIME (not persisted)
    mcp = McpTool(server_label="github", server_url="https://api.githubcopilot.com/mcp/")
    token, src = pick_token()
    if token:
        mcp.update_headers("Authorization", f"Bearer {token}")
        print(f"[auth] Using {src}")
    else:
        print("[auth] No GITHUB_OAUTH_TOKEN or GITHUB_PAT set — GitHub MCP calls will fail.")
    mcp.set_approval_mode("never")  # skip approval prompts for a smooth demo

    # Create a single thread for the chat session
    with project:
        thread = project.agents.threads.create()
        print("Chat ready. Type your question (e.g., 'List 5 open issues in microsoft/vscode'), or '/exit' to quit.\n")

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
                tool_resources=mcp.resources,  # <-- runtime-only auth & headers
            ) as stream:
                handler.until_done()  # block until completion

            print()  # add a newline after the streamed reply

if __name__ == "__main__":
    main()

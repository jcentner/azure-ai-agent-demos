#!/usr/bin/env python3
# agent/ask_agent.py
"""
ask_agent.py — Minimal interactive chat loop that prints what the agent is doing.

What it shows:
- How to attach MCP auth (Bearer token) at run-time
- How to stream a run and see message tokens + tool call steps
- A tiny REPL: type a prompt, see streaming output, '/exit' to quit

Auth behavior:
- If LOCAL_MCP_TOKEN is set, it is used as "Authorization: Bearer <token>" for MCP calls.
- Else, the run proceeds but MCP calls will fail if your server requires auth.

Env (read from .env via python-dotenv):
- PROJECT_ENDPOINT           (required)
- AGENT_ID                   (optional; else read from ./.agent_id)
- MCP_SERVER_URL             (required in Azure; e.g., https://<sub>.ngrok.app/mcp)
- LOCAL_MCP_TOKEN            (optional; recommended if server enforces auth)
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv, find_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import (
    McpTool,
    AgentEventHandler,
    ThreadMessage,
    MessageDeltaChunk,
    RunStep,
)


def resolve_server_url_or_warn(raw: str | None) -> tuple[str, bool]:
    """
    Return (url, ok). If MCP_SERVER_URL is missing, return an intentionally invalid URL
    and ok=False so callers can warn/pause but still proceed for demo purposes.
    Ensures the returned URL ends with '/mcp'.
    """
    if not raw or not raw.strip():
        return "https://example.invalid/mcp", False
    raw = raw.strip()
    if not raw.rstrip("/").endswith("/mcp"):
        raw = raw.rstrip("/") + "/mcp"
    return raw, True


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
    # Load repo-root .env
    load_dotenv(find_dotenv())

    endpoint = os.environ["PROJECT_ENDPOINT"]

    # Agent id comes from .agent_id (created by create_agent.py), or env override
    agent_id = os.getenv("AGENT_ID") or Path(".agent_id").read_text(encoding="utf-8").strip()

    # MCP server URL (must be reachable from Azure; localhost won't work there)
    server_url, has_server_url = resolve_server_url_or_warn(os.getenv("MCP_SERVER_URL"))
    if not has_server_url:
        print("[config] ERROR: MCP_SERVER_URL is not set in ../.env")
        print("         When running in Azure, a localhost URL will NOT be reachable.")
        print("         Set MCP_SERVER_URL to your public MCP endpoint (e.g., your ngrok https URL + '/mcp').")
        try:
            input("Press Enter to CONTINUE with an intentionally invalid URL (this will fail), or Ctrl+C to abort...")
        except (EOFError, KeyboardInterrupt):
            pass
    print(f"[config] Using MCP server URL: {server_url}")

    # Rebuild the MCP tool, but for inference, attach auth headers AT RUN TIME (not persisted)
    mcp = McpTool(server_label="chinook", server_url=server_url)

    token = os.getenv("LOCAL_MCP_TOKEN")
    if token:
        mcp.update_headers("Authorization", f"Bearer {token}")
        print("[auth] Using LOCAL_MCP_TOKEN for MCP Authorization header")
    else:
        print("[auth] No LOCAL_MCP_TOKEN set — MCP calls will fail if your server requires auth.")

    # Skip approval prompts for a smooth demo
    mcp.set_approval_mode("never")

    # Connect to the project and run a simple REPL
    project = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    with project:
        thread = project.agents.threads.create()
        print("\nChat ready. Try prompts like:")
        print("  - tell me what database tools you can use")
        print("  - list top customers")
        print("  - create a new customer, then show them")
        print("Type '/exit' to quit.\n")

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

            # Add the user message
            project.agents.messages.create(thread_id=thread.id, role="user", content=user)

            # Stream the run so you can see tokens + tool calls live
            handler = ConsoleEvents()
            with project.agents.runs.stream(
                thread_id=thread.id,
                agent_id=agent_id,
                event_handler=handler,
                tool_resources=mcp.resources,  # runtime-only auth & headers
            ) as stream:
                handler.until_done()  # block until completion

            print()  # newline after streamed reply


if __name__ == "__main__":
    main()

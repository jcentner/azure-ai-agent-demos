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

Additions in this version:
- Simple verbose mode via CLI flag (-v/--verbose) or VERBOSE_AGENTS=1
- --no-stream flag to disable token streaming
"""

import os
import argparse
import time
from datetime import datetime, timezone
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

# ----------------------- Verbose helpers (tiny) ----------------------------
def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _truncate(s: str, limit: int = 400) -> str:
    if not isinstance(s, str):
        return ""
    return s if len(s) <= limit else s[:limit] + f"... [{len(s)-limit} more chars]"

def _redact_map(d):
    if not isinstance(d, dict):
        return d
    out = {}
    for k, v in d.items():
        if isinstance(k, str) and k.lower() in {"authorization", "proxy-authorization"}:
            out[k] = "REDACTED"
        else:
            out[k] = v
    return out

# --- Minimal event handler to show what the agent is doing -----------------
class ConsoleEvents(AgentEventHandler):
    """Print run status, token deltas, and MCP tool-call details; supports a simple verbose mode."""
    def __init__(self, verbose: bool = False, stream_tokens: bool = True):
        super().__init__()
        self.verbose = bool(verbose)
        self.stream_tokens = bool(stream_tokens)
        self._run_started_at = None
        self._tool_call_count = 0

    def on_thread_run(self, run):
        status = getattr(run, "status", None)
        if status in {None, "queued", "in_progress"} and self._run_started_at is None:
            self._run_started_at = time.time()
        print(f"\n[run] id={run.id} status={status}")
        if status in {"completed", "failed", "cancelled"} and self.verbose:
            dur = None if self._run_started_at is None else round(time.time() - self._run_started_at, 3)
            print(f"[run] done status={status} duration_s={dur} tool_calls={self._tool_call_count}")

    def on_thread_message(self, message: ThreadMessage):
        role = getattr(message, "role", "?")
        status = getattr(message, "status", None)
        print(f"[message] role={role} id={message.id} status={status}")
        if self.verbose:
            try:
                content = getattr(message, "content", None)
                if isinstance(content, str):
                    preview = _truncate(content, 400)
                    if preview:
                        print(f"  └─ content: {preview}")
            except Exception:
                pass

    def on_message_delta(self, delta: MessageDeltaChunk):
        # Stream assistant tokens live
        if not self.stream_tokens:
            return
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
                
                # Debug: print all attributes of the tool call
                if self.verbose:
                    print(f"    [debug] tool_call attributes: {dir(tc)}")
                    print(f"    [debug] tool_call dict: {tc.__dict__ if hasattr(tc, '__dict__') else 'no __dict__'}")
                
                # Try different ways to access MCP details
                mcp = getattr(tc, "mcp_tool", None)
                if not mcp and tc_type == "mcp":
                    # Try accessing it directly if type is mcp
                    mcp = tc
                
                if mcp:
                    self._tool_call_count += 1
                    server_label = getattr(mcp, 'server_label', None)
                    name = getattr(mcp, 'name', None)
                    print(f"    mcp.server_label={server_label} name={name}")
                    if self.verbose:
                        # Debug: print all MCP attributes
                        print(f"      [debug] mcp attributes: {dir(mcp)}")
                        
                        # Show (truncated) args/result if available
                        try:
                            args = getattr(mcp, "arguments", None)
                            if isinstance(args, dict):
                                args = _redact_map(args)
                            print(f"      args={_truncate(str(args), 800)}")
                        except Exception as e:
                            print(f"      [debug] args error: {e}")
                        
                        try:
                            res = getattr(mcp, "result", None)
                            print(f"      result={_truncate(str(res), 800)}")
                        except Exception as e:
                            print(f"      [debug] result error: {e}")
                        
                        # Try output attribute
                        try:
                            output = getattr(mcp, "output", None)
                            if output:
                                print(f"      output={_truncate(str(output), 800)}")
                        except Exception:
                            pass

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

    # -------------------- CLI --------------------
    parser = argparse.ArgumentParser(description="Chat with an Azure AI Agent (GitHub MCP).")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose console output.")
    parser.add_argument("--no-stream", action="store_true", help="Disable token streaming.")
    args = parser.parse_args()

    # Env fallback for verbosity (only if flag not set)
    if not args.verbose and os.getenv("VERBOSE_AGENTS") in {"1", "true", "True"}:
        args.verbose = True

    endpoint = os.environ["PROJECT_ENDPOINT"]
    # Agent id comes from .agent_id (created by create_agent.py), or env override
    agent_id = os.getenv("AGENT_ID") or Path(".agent_id").read_text(encoding="utf-8").strip()

    # Connect to the project
    project = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())

    # Rebuild the MCP tool, but for inference, attach auth headers AT RUN TIME (not persisted)
    mcp = McpTool(server_label="github", server_url="https://api.githubcopilot.com/mcp/")
    mcp.set_approval_mode("never")  # skip approval prompts for a smooth demo
    token, src = pick_token()
    if token:
        mcp.update_headers("Authorization", f"Bearer {token}")
        print(f"[auth] Using {src}")
        
        # Debug: Let's see what headers are actually set
        if args.verbose:
            print(f"[debug] MCP headers after update: {mcp.headers if hasattr(mcp, 'headers') else 'no headers attr'}")
            print(f"[debug] MCP resources: {mcp.resources if hasattr(mcp, 'resources') else 'no resources attr'}")
    else:
        print("[auth] No GITHUB_OAUTH_TOKEN or GITHUB_PAT set — GitHub MCP calls will fail.")

    # Create a single thread for the chat session
    with project:
        thread = project.agents.threads.create()
        # Verbose session banner
        if args.verbose:
            print(f"[session] { _now_iso() } endpoint={endpoint} agent_id={agent_id}")
            print("[mcp] server_label=github server_url=https://api.githubcopilot.com/mcp/ headers=REDACTED")
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
            handler = ConsoleEvents(verbose=args.verbose, stream_tokens=not args.no_stream)
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

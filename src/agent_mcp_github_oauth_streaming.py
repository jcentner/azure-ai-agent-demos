#!/usr/bin/env python3
"""
agent_mcp_github_oauth_streaming.py

- Uses OAuth token for GitHub MCP (no PAT)
- Streams ALL agent events (message deltas, run steps, tool calls)
- Idempotent agent creation: reuses existing agent by name if found
"""

import os
import json
from typing import Optional

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import (
    McpTool,
    AgentEventHandler,
    ThreadMessage,
    MessageDeltaChunk,
    RunStep,
    RunStepDeltaChunk,
)

AGENT_DEFAULT_NAME = "mcp-github-readonly-demo"


# ---------- Utilities ----------

def get_or_create_agent(
    project: AIProjectClient,
    *,
    name: str,
    model: str,
    instructions: str,
    tools,
    tool_resources=None,
):
    """
    Idempotent agent creation. Tries to find by name; creates if missing.
    """
    # Try list APIs available on this SDK surface
    list_fn = getattr(project.agents, "list_agents", None) or getattr(project.agents, "list", None)
    if list_fn:
        try:
            for a in list_fn():
                if getattr(a, "name", None) == name:
                    print(f"[agent] Reusing existing agent: {a.id} ({a.name})")
                    return a
        except Exception as e:
            print(f"[agent] Warning: listing agents failed, will create new. Details: {e}")

    # Create if not found
    agent = project.agents.create_agent(
        model=model,
        name=name,
        instructions=instructions,
        tools=tools,
        tool_resources=tool_resources,
    )
    print(f"[agent] Created new agent: {agent.id} ({agent.name})")
    return agent


class ConsoleEventPrinter(AgentEventHandler):
    """
    Prints EVERYTHING to console while the run streams:
      - thread run state changes
      - message deltas (token stream)
      - run steps and tool call deltas
      - unhandled events (for completeness)
    """

    def __init__(self):
        super().__init__()
        self.last_run_id: Optional[str] = None

    # ThreadRun lifecycle (created/in_progress/completed/…)
    def on_thread_run(self, run):
        self.last_run_id = getattr(run, "id", self.last_run_id)
        status = getattr(run, "status", None)
        print(f"\n[run] id={run.id} status={status}")

    # Full messages (created/completed)
    def on_thread_message(self, message: ThreadMessage):
        # Prints when a message object (assistant/user) is created or completed
        role = getattr(message, "role", "?")
        print(f"[message] role={role} id={message.id} status={getattr(message, 'status', None)}")

    # Token deltas from the assistant
    def on_message_delta(self, delta: MessageDeltaChunk):
        if getattr(delta, "text", None):
            print(delta.text, end="", flush=True)

    # Completed steps (e.g., message creation, tool calls)
    def on_run_step(self, step: RunStep):
        print(f"\n[step] id={step.id} type={getattr(step, 'type', None)} status={getattr(step, 'status', None)}")
        details = getattr(step, "step_details", None)
        if details and getattr(details, "type", None) == "tool_calls":
            # Generic dump of tool calls (covers function/file search/MCP/etc.)
            tool_calls = getattr(details, "tool_calls", []) or []
            for idx, tc in enumerate(tool_calls, 1):
                tc_type = getattr(tc, "type", None)
                print(f"  [tool_call {idx}] type={tc_type}")
                # Print function/MCP specifics if present
                func = getattr(tc, "function", None)
                if func:
                    print(f"    function.name={getattr(func, 'name', None)}")
                    params = getattr(func, "parameters", None)
                    if params:
                        try:
                            print("    function.params=", json.dumps(json.loads(params), indent=2))
                        except Exception:
                            print("    function.params=", params)

                mcp = getattr(tc, "mcp_tool", None)
                if mcp:
                    print(f"    mcp.server_label={getattr(mcp, 'server_label', None)}")
                    print(f"    mcp.name={getattr(mcp, 'name', None)}")
                    args = getattr(mcp, "arguments", None)
                    if args:
                        try:
                            print("    mcp.arguments=", json.dumps(json.loads(args), indent=2))
                        except Exception:
                            print("    mcp.arguments=", args)

                file_search = getattr(tc, "file_search", None)
                if file_search:
                    # May be populated if you included the 'include' param when listing run steps
                    results = getattr(file_search, "results", None)
                    print(f"    file_search.results_count={len(results or [])}")

    # Step delta updates (detail-by-detail)
    def on_run_step_delta(self, delta: RunStepDeltaChunk):
        # Handy during tool resolve cycles
        print(f"[step-delta] {getattr(delta, 'type', None)} -> details={getattr(delta, 'delta', None)}")

    def on_unhandled_event(self, event_type: str, event_data):
        print(f"[unhandled] {event_type}: {event_data}")


def main():
    # Required env vars
    project_endpoint = os.environ["PROJECT_ENDPOINT"]
    model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]
    github_oauth_token = os.environ.get("GITHUB_OAUTH_TOKEN")  # Must be a valid GH OAuth access token
    agent_name = os.environ.get("AGENT_NAME", AGENT_DEFAULT_NAME)

    if not github_oauth_token:
        raise RuntimeError("Set GITHUB_OAUTH_TOKEN to a valid GitHub OAuth access token.")

    # Connect to Foundry project
    project = AIProjectClient(endpoint=project_endpoint, credential=DefaultAzureCredential())

    # GitHub MCP tool (OAuth via header)
    github_mcp_url = "https://api.githubcopilot.com/mcp/"
    mcp_tool = McpTool(server_label="github", server_url=github_mcp_url)
    mcp_tool.update_headers("Authorization", f"Bearer {github_oauth_token}")
    mcp_tool.set_approval_mode("never")

    instructions = (
        "You can use the GitHub MCP tool to read repositories and issues. "
        "When the user asks for GitHub data, call the MCP tools."
    )

    with project:
        # Idempotent: reuse agent if already present
        agent = get_or_create_agent(
            project,
            name=agent_name,
            model=model_deployment_name,
            instructions=instructions,
            tools=mcp_tool.definitions,
            tool_resources=mcp_tool.resources,
        )

        # New thread and user message
        thread = project.agents.threads.create()
        repo = os.environ.get("REPO", "microsoft/vscode")
        user_prompt = f"List the 5 most recent open issues in {repo} with their titles and numbers."
        project.agents.messages.create(thread_id=thread.id, role="user", content=user_prompt)

        # Stream the run with a verbose event handler
        handler = ConsoleEventPrinter()
        print("\n--- STREAM START ---")
        with project.agents.runs.stream(
            thread_id=thread.id,
            agent_id=agent.id,
            event_handler=handler,          # prints deltas, steps & tool calls
            tool_resources=mcp_tool.resources,
        ) as stream:
            handler.until_done()
        print("\n--- STREAM END ---\n")

        # Grab assistant’s final text (most recent assistant message)
        last = project.agents.messages.get_last_message_text_by_role(thread_id=thread.id, role="assistant")
        if last:
            print("\n--- ASSISTANT (final) ---")
            print(last)

        # Optional: list run steps with tool call details (post-mortem)
        # Include file search content if any tools used it (safe to include regardless).
        print("\n--- RUN STEPS ---")
        # Prefer the run ID captured by the handler; otherwise fall back to latest run
        run_id = handler.last_run_id
        if not run_id:
            # Get most recent run on the thread (desc)
            runs = project.agents.runs.list(thread_id=thread.id, order="desc", limit=1)
            for r in runs:
                run_id = r.id
                break

        if run_id:
            steps = project.agents.run_steps.list(
                thread_id=thread.id,
                run_id=run_id,
                include=["step_details.tool_calls[*].file_search.results[*].content"],
            )
            for s in steps:
                print(
                    f"step_id={s.id} type={getattr(s, 'type', None)} "
                    f"status={getattr(s, 'status', None)} created_at={getattr(s, 'created_at', None)}"
                )
                sd = getattr(s, "step_details", None)
                if sd and getattr(sd, "type", None) == "tool_calls":
                    for i, tc in enumerate(getattr(sd, "tool_calls", []) or [], 1):
                        print(f"  tool_call[{i}] type={getattr(tc, 'type', None)} details={tc}")
        else:
            print("No run id captured; skipping run step dump.")


if __name__ == "__main__":
    main()

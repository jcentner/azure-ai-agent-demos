#!/usr/bin/env python3
import os
import json
import time
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

# --- OpenTelemetry / Azure Monitor ---
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from opentelemetry.trace import SpanKind

# Enable detailed content capture in traces (optional; may contain PII)
if os.getenv("AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"):
    # Any truthy value enables recording (False by default).
    pass  # value read by Azure SDK; no code changes needed.  # docs: learn.microsoft.com link

AGENT_DEFAULT_NAME = "mcp-github-readonly-demo"


def enable_tracing(project: AIProjectClient):
    """
    Wire OpenTelemetry → Azure Monitor (Application Insights) and enable
    Azure AI Agents SDK instrumentation.
    """
    # Use the project's connected App Insights (no manual copy/paste needed)
    # Foundry portal: Observability → Tracing connects App Insights.
    conn = project.telemetry.get_application_insights_connection_string()
    configure_azure_monitor(connection_string=conn)  # sets up provider + exporter
    # Optional: set OTEL_SERVICE_NAME via env to make your service name clear in App Insights
    # os.environ.setdefault("OTEL_SERVICE_NAME", "mcp-github-oauth-demo")


class OTelVerbosePrinter(AgentEventHandler):
    """
    Streams EVERYTHING to console and emits custom OTel spans for tool calls.

    - Prints run and message events (like your prior version).
    - Creates custom spans per tool call to expose "tool latency" even if you just
      see client-side timing. Attributes are attached for easy Kusto queries.
    """
    def __init__(self, tracer):
        super().__init__()
        self.tracer = tracer
        self.last_run_id: Optional[str] = None
        self._step_start_ns = {}  # step_id -> perf_counter_ns
        self._step_spans = {}     # step_id -> span

    def on_thread_run(self, run):
        self.last_run_id = getattr(run, "id", self.last_run_id)
        print(f"\n[run] id={run.id} status={getattr(run, 'status', None)}")

    def on_thread_message(self, message: ThreadMessage):
        print(f"[message] role={getattr(message, 'role', '?')} id={message.id} status={getattr(message, 'status', None)}")

    def on_message_delta(self, delta: MessageDeltaChunk):
        if getattr(delta, "text", None):
            print(delta.text, end="", flush=True)

    def on_run_step(self, step: RunStep):
        # Print summary
        print(f"\n[step] id={step.id} type={getattr(step, 'type', None)} status={getattr(step, 'status', None)}")

        # We create a span the first time we see a tool step move into progress;
        # and finish it when we see completed/failed/cancelled.
        status = str(getattr(step, "status", "")).lower()
        details = getattr(step, "step_details", None)
        is_tool = bool(details and getattr(details, "type", None) == "tool_calls")

        if is_tool:
            tool_calls = list(getattr(details, "tool_calls", []) or [])
            # Show in console
            for i, tc in enumerate(tool_calls, 1):
                tc_type = getattr(tc, "type", None)
                print(f"  [tool_call {i}] type={tc_type}")

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

            # OTel: create/start span on first observation of this step
            if status in ("in_progress", "queued") and step.id not in self._step_spans:
                # Derive a readable name for the span
                span_name = "tool"
                if tool_calls:
                    # Prefer MCP tool name or function name if available
                    mcp = getattr(tool_calls[0], "mcp_tool", None)
                    func = getattr(tool_calls[0], "function", None)
                    if mcp and getattr(mcp, "name", None):
                        span_name = f"tool.mcp:{mcp.name}"
                    elif func and getattr(func, "name", None):
                        span_name = f"tool.func:{func.name}"

                span = self.tracer.start_span(span_name, kind=SpanKind.INTERNAL)
                # Attach attributes useful for queries/dashboards
                span.set_attribute("ai.agents.step.id", step.id)
                span.set_attribute("ai.agents.step.type", getattr(step, "type", None))
                span.set_attribute("ai.agents.step.status", status)
                span.set_attribute("ai.agents.tool.count", len(tool_calls))
                # Add specific tool names if we can
                names = []
                for tc in tool_calls:
                    mcp = getattr(tc, "mcp_tool", None)
                    func = getattr(tc, "function", None)
                    if mcp and getattr(mcp, "name", None):
                        names.append(f"mcp:{mcp.name}")
                    elif func and getattr(func, "name", None):
                        names.append(f"func:{func.name}")
                if names:
                    span.set_attribute("ai.agents.tools", ", ".join(names))

                self._step_spans[step.id] = span
                self._step_start_ns[step.id] = time.perf_counter_ns()

            # OTel: finish span on terminal status
            if status in ("completed", "failed", "cancelled"):
                span = self._step_spans.pop(step.id, None)
                start_ns = self._step_start_ns.pop(step.id, None)
                if span:
                    if start_ns is not None:
                        elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000
                        span.set_attribute("ai.agents.tool.latency_ms", round(elapsed_ms, 2))
                    span.set_attribute("ai.agents.step.status", status)
                    span.end()

    def on_run_step_delta(self, delta: RunStepDeltaChunk):
        # Helpful for visualizing progression of a step
        print(f"[step-delta] {getattr(delta, 'type', None)} -> details={getattr(delta, 'delta', None)}")


def main():
    # --- Required env ---
    project_endpoint = os.environ["PROJECT_ENDPOINT"]
    model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]
    github_oauth_token = os.environ.get("GITHUB_OAUTH_TOKEN")
    agent_name = os.environ.get("AGENT_NAME", AGENT_DEFAULT_NAME)
    if not github_oauth_token:
        raise RuntimeError("Set GITHUB_OAUTH_TOKEN to a valid GitHub OAuth access token.")

    # Connect to Foundry project
    project = AIProjectClient(endpoint=project_endpoint, credential=DefaultAzureCredential())

    # Enable tracing/export to your project's Application Insights
    enable_tracing(project)  # uses project's connected App Insights

    # Optional: also see spans locally in your console
    # from opentelemetry.sdk.trace import TracerProvider
    # from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
    # tracer_provider = TracerProvider()
    # tracer_provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    # trace.set_tracer_provider(tracer_provider)

    tracer = trace.get_tracer(__name__)

    # GitHub MCP tool (OAuth via header)
    github_mcp_url = "https://api.githubcopilot.com/mcp/"
    mcp_tool = McpTool(server_label="github", server_url=github_mcp_url)
    mcp_tool.update_headers("Authorization", f"Bearer {github_oauth_token}")
    mcp_tool.set_approval_mode("never")

    instructions = (
        "You can use the GitHub MCP tool to read repositories and issues. "
        "When the user asks for GitHub data, call the MCP tools."
    )

    # Idempotent agent creation (reuse by name if exists)
    with project:
        # Try to find by name; create otherwise
        list_fn = getattr(project.agents, "list_agents", None) or getattr(project.agents, "list", None)
        agent = None
        if list_fn:
            try:
                for a in list_fn():
                    if getattr(a, "name", None) == agent_name:
                        print(f"[agent] Reusing existing agent: {a.id} ({a.name})")
                        agent = a
                        break
            except Exception as e:
                print(f"[agent] Warning: listing agents failed, will create new. Details: {e}")

        if agent is None:
            agent = project.agents.create_agent(
                model=model_deployment_name,
                name=agent_name,
                instructions=instructions,
                tools=mcp_tool.definitions,
                tool_resources=mcp_tool.resources,
            )
            print(f"[agent] Created new agent: {agent.id} ({agent.name})")

        # New thread and user message
        thread = project.agents.threads.create()
        repo = os.environ.get("REPO", "microsoft/vscode")
        user_prompt = f"List the 5 most recent open issues in {repo} with their titles and numbers."
        project.agents.messages.create(thread_id=thread.id, role="user", content=user_prompt)

        # Stream the run with verbose console + custom OTel spans
        handler = OTelVerbosePrinter(tracer)
        print("\n--- STREAM START ---")
        with project.agents.runs.stream(
            thread_id=thread.id,
            agent_id=agent.id,
            event_handler=handler,
            tool_resources=mcp_tool.resources,
        ) as stream:
            handler.until_done()
        print("\n--- STREAM END ---\n")

        # Final assistant text (handy in CI logs)
        last = project.agents.messages.get_last_message_text_by_role(thread_id=thread.id, role="assistant")
        if last:
            print("\n--- ASSISTANT (final) ---")
            print(last)

        # Optional: enumerate steps after the fact (also shows in traces)
        print("\n--- RUN STEPS ---")
        run_id = handler.last_run_id
        if not run_id:
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
        else:
            print("No run id captured; skipping run step dump.")


if __name__ == "__main__":
    main()

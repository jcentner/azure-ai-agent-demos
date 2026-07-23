"""Shared helpers for Lab 1 (Foundry Toolbox versioning).

Every script imports from here so the setup lives in one place.

Auth model for this lab:
- We mint a fresh Entra token at call time (scope https://ai.azure.com/.default)
  and hand it to the toolbox MCP endpoint. The raw azure-ai-projects SDK does NOT
  auto-inject managed identity for a first-party toolbox, so the token is explicit.
- Minting per call means the token never goes stale mid-lab.
"""

import json
import os
import urllib.request
from pathlib import Path

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

TOOLBOX_NAME = "lab1tools"
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

MODEL = os.environ.get("MODEL_DEPLOYMENT_NAME")
PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")


def _required(value: str | None, variable: str) -> str:
    if not value:
        raise RuntimeError(f"Set {variable} in training/l200-tools/.env.")
    return value

_credential = DefaultAzureCredential()
project = AIProjectClient(
    endpoint=_required(PROJECT_ENDPOINT, "PROJECT_ENDPOINT"),
    credential=_credential,
)


def token() -> str:
    """Fresh Entra token for the toolbox MCP endpoint."""
    return _credential.get_token("https://ai.azure.com/.default").token


def consumer_endpoint() -> str:
    """Always serves the toolbox's default_version. This is what agents use."""
    return f"{PROJECT_ENDPOINT}/toolboxes/{TOOLBOX_NAME}/mcp?api-version=v1"


def developer_endpoint(version: str) -> str:
    """Serves one specific version. Use to test a version before promoting it."""
    return f"{PROJECT_ENDPOINT}/toolboxes/{TOOLBOX_NAME}/versions/{version}/mcp?api-version=v1"


def tools_list(url: str) -> list:
    """Raw MCP tools/list against a toolbox endpoint. Shows exactly what the
    endpoint serves right now - the deterministic ground truth for diagnosis."""
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}).encode()
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {token()}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
    )
    with urllib.request.urlopen(request) as response:
        payload = json.loads(response.read().decode())
    return [t["name"] for t in payload["result"]["tools"]]


def toolbox_tool(server_label: str, url: str) -> dict:
    """The toolbox as one MCP tool on an agent call."""
    return {
        "type": "mcp",
        "server_label": server_label,
        "server_url": url,
        "require_approval": "never",
        "authorization": token(),
    }


def run_agent(instructions_input: str, server_label: str, url: str):
    """One agent turn against the toolbox. Returns (tools_seen, answer)."""
    if not MODEL:
        raise RuntimeError(
            "Set MODEL_DEPLOYMENT_NAME to a model deployment that supports MCP, "
            "Web Search, and Code Interpreter."
        )
    client = project.get_openai_client()
    response = client.responses.create(
        model=MODEL,
        input=instructions_input,
        tools=[toolbox_tool(server_label, url)],
    )
    tools_seen, tool_calls = [], []
    for item in response.output:
        kind = getattr(item, "type", None)
        if kind == "mcp_list_tools":
            tools_seen = [t.name for t in item.tools]
        elif kind == "mcp_call":
            tool_calls.append(getattr(item, "name", ""))
    return tools_seen, tool_calls, (response.output_text or "")

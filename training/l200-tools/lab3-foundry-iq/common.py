"""Shared helpers for Lab 3 (Foundry IQ knowledge base).

Every script imports from here so the setup lives in one place.

What this lab builds:
- A reusable Foundry IQ *knowledge base* (KB) in Azure AI Search: a knowledge source over the Lab 2
  `contoso-benefits` index, plus an LLM for query planning and answer synthesis.
- The KB exposes an MCP endpoint. A Foundry project *connection* (RemoteTool + project managed
  identity) targets that endpoint, and each agent adds it as an MCP tool. One KB -> many agents.

API versions (deliberate mix):
- The search *index* and the *knowledge source* are generally available (2026-04-01) and created with
  the stable `azure-search-documents` SDK.
- A KB *with a model* (answer synthesis, configurable reasoning effort) is a 2026-05-01-preview
  feature the stable SDK will not send, so the KB is created via a raw REST PUT at that api-version.
- The agent<->KB connection uses the MCP endpoint at 2026-05-01-preview.
"""

import os
from pathlib import Path
from typing import Optional

import requests
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import MCPTool, PromptAgentDefinition
from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndexFieldReference,
    SearchIndexKnowledgeSource,
    SearchIndexKnowledgeSourceParameters,
)
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

MODEL_DEPLOYMENT_NAME = os.environ.get("MODEL_DEPLOYMENT_NAME")
MODEL_NAME = os.environ.get("MODEL_NAME") or MODEL_DEPLOYMENT_NAME
INDEX_NAME = "contoso-benefits"  # reused from Lab 2
SEMANTIC_CONFIG = "default"
KS_NAME = "contoso-benefits-ks"
KB_NAME = "contoso-benefits-kb"
KB_CONNECTION_NAME = "contoso-kb-mcp"
AGENT_NAMES = ["hr-assistant", "onboarding-assistant"]

SEARCH_CONNECTION_NAME = os.environ.get("SEARCH_CONNECTION_NAME")
KB_API_VERSION = "2026-05-01-preview"

PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")
PROJECT_RESOURCE_ID = os.environ.get("PROJECT_RESOURCE_ID")
# The Azure OpenAI endpoint on the Foundry resource that hosts the KB's query-planning model.
AOAI_ENDPOINT = os.environ.get("AOAI_ENDPOINT")


def _required(value: Optional[str], variable: str) -> str:
    if not value:
        raise RuntimeError(f"Set {variable} in training/l200-tools/.env.")
    return value


_credential = DefaultAzureCredential()
project = AIProjectClient(
    endpoint=_required(PROJECT_ENDPOINT, "PROJECT_ENDPOINT"),
    credential=_credential,
)

_conn = project.connections.get(_required(SEARCH_CONNECTION_NAME, "SEARCH_CONNECTION_NAME"))
SEARCH_ENDPOINT = _conn.target.rstrip("/")


def index_client() -> SearchIndexClient:
    return SearchIndexClient(endpoint=SEARCH_ENDPOINT, credential=_credential)


def mcp_endpoint() -> str:
    """The KB's MCP endpoint, which the agent calls to run agentic retrieval."""
    return f"{SEARCH_ENDPOINT}/knowledgebases/{KB_NAME}/mcp?api-version={KB_API_VERSION}"


def _search_token() -> str:
    return _credential.get_token("https://search.azure.com/.default").token


def _arm_token() -> str:
    return _credential.get_token("https://management.azure.com/.default").token


def create_knowledge_source() -> None:
    """Create a search-index knowledge source over the Lab 2 index (GA SDK)."""
    ks = SearchIndexKnowledgeSource(
        name=KS_NAME,
        description="Contoso employee benefits, sourced from the Lab 2 search index.",
        search_index_parameters=SearchIndexKnowledgeSourceParameters(
            search_index_name=INDEX_NAME,
            semantic_configuration_name=SEMANTIC_CONFIG,
            source_data_fields=[
                SearchIndexFieldReference(name=f) for f in ("id", "title", "content", "category")
            ],
            search_fields=[SearchIndexFieldReference(name=f) for f in ("title", "content")],
        ),
    )
    index_client().create_or_update_knowledge_source(ks)


def create_knowledge_base() -> None:
    """Create the KB with an LLM (answer synthesis + reasoning effort) via preview REST."""
    model_deployment = _required(MODEL_DEPLOYMENT_NAME, "MODEL_DEPLOYMENT_NAME")
    model_name = _required(MODEL_NAME, "MODEL_NAME")
    model_endpoint = _required(AOAI_ENDPOINT, "AOAI_ENDPOINT")
    body = {
        "name": KB_NAME,
        "description": "Reusable benefits knowledge base shared across agents.",
        "knowledgeSources": [{"name": KS_NAME}],
        "models": [
            {
                "kind": "azureOpenAI",
                "azureOpenAIParameters": {
                    "resourceUri": model_endpoint,
                    "deploymentId": model_deployment,
                    "modelName": model_name,
                },
            }
        ],
        "outputMode": "answerSynthesis",
        "retrievalReasoningEffort": {"kind": "medium"},
    }
    resp = requests.put(
        f"{SEARCH_ENDPOINT}/knowledgebases/{KB_NAME}?api-version={KB_API_VERSION}",
        headers={"Authorization": f"Bearer {_search_token()}", "Content-Type": "application/json"},
        json=body,
    )
    resp.raise_for_status()


def create_kb_connection() -> None:
    """Create the RemoteTool project connection that targets the KB's MCP endpoint.

    authType=ProjectManagedIdentity: the agent reaches the KB as the project MI, which needs
    Search Index Data Reader on the search service (granted in Lab 2).
    """
    body = {
        "name": KB_CONNECTION_NAME,
        "type": "Microsoft.MachineLearningServices/workspaces/connections",
        "properties": {
            "authType": "ProjectManagedIdentity",
            "category": "RemoteTool",
            "target": mcp_endpoint(),
            "isSharedToAll": True,
            "audience": "https://search.azure.com/",
            "metadata": {"ApiType": "Azure"},
        },
    }
    resp = requests.put(
        f"https://management.azure.com{_required(PROJECT_RESOURCE_ID, 'PROJECT_RESOURCE_ID')}"
        f"/connections/{KB_CONNECTION_NAME}"
        "?api-version=2025-10-01-preview",
        headers={"Authorization": f"Bearer {_arm_token()}", "Content-Type": "application/json"},
        json=body,
    )
    resp.raise_for_status()


_INSTRUCTIONS = (
    "You are a helpful assistant that must use the knowledge base tool to answer every question. "
    "Never answer from your own knowledge. Include citations to the retrieved sources. "
    'If the knowledge base does not contain the answer, respond with "I don\'t know".'
)


def build_agent(agent_name: str):
    """Create an agent version that consumes the KB as an MCP tool."""
    model_deployment = _required(MODEL_DEPLOYMENT_NAME, "MODEL_DEPLOYMENT_NAME")
    tool = MCPTool(
        server_label="knowledge-base",
        server_url=mcp_endpoint(),
        require_approval="never",
        allowed_tools=["knowledge_base_retrieve"],
        project_connection_id=KB_CONNECTION_NAME,
    )
    return project.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=model_deployment,
            instructions=_INSTRUCTIONS,
            tools=[tool],
        ),
    )


def run_agent(agent, question: str):
    """One turn against a KB-backed agent. Returns (answer, tool_used, annotation_count)."""
    oc = project.get_openai_client()
    response = oc.responses.create(
        input=question,
        extra_body={
            "agent_reference": {"type": "agent_reference", "name": agent.name, "version": agent.version}
        },
    )
    tool_used = False
    annotations = 0
    for item in response.output:
        item_type = getattr(item, "type", None)
        if item_type == "mcp_call" and getattr(item, "name", "") == "knowledge_base_retrieve":
            tool_used = True
        if item_type == "message":
            for block in getattr(item, "content", []) or []:
                annotations += len(getattr(block, "annotations", []) or [])
    return (response.output_text or ""), tool_used, annotations

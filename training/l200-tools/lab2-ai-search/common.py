"""Shared helpers for Lab 2 (Azure AI Search grounding).

Every script imports from here so setup lives in one place.

Grounding model for this lab:
- We create a plain Azure AI Search index over a small document set and attach it to ONE agent as
  the built-in AzureAISearch tool. The agent answers only from the index and cites its sources.
- Auth to the search service uses the project's AI Search *connection* (Entra/AAD). The Foundry
  service reaches Search under the project identity, so that identity needs the Search data-plane
  roles (see README Phase 2).
"""

import glob
import os
import re
from pathlib import Path

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AISearchIndexResource,
    AzureAISearchQueryType,
    AzureAISearchTool,
    AzureAISearchToolResource,
    PromptAgentDefinition,
)
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    SimpleField,
)
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

MODEL = os.environ.get("MODEL_DEPLOYMENT_NAME")
INDEX_NAME = "contoso-benefits"
SEARCH_CONNECTION_NAME = os.environ.get("SEARCH_CONNECTION_NAME")
SEMANTIC_CONFIG = "default"
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

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

_conn = project.connections.get(_required(SEARCH_CONNECTION_NAME, "SEARCH_CONNECTION_NAME"))
SEARCH_ENDPOINT = _conn.target.rstrip("/")
SEARCH_CONNECTION_ID = _conn.id


def _index_client() -> SearchIndexClient:
    return SearchIndexClient(endpoint=SEARCH_ENDPOINT, credential=_credential)


def _search_client() -> SearchClient:
    return SearchClient(endpoint=SEARCH_ENDPOINT, index_name=INDEX_NAME, credential=_credential)


def create_index() -> None:
    """Create the contoso-benefits index (keyword + semantic; no vectors for the first pass)."""
    index = SearchIndex(
        name=INDEX_NAME,
        fields=[
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="title", type=SearchFieldDataType.String),
            SearchableField(name="content", type=SearchFieldDataType.String),
            SimpleField(name="category", type=SearchFieldDataType.String, filterable=True),
        ],
        semantic_search=SemanticSearch(
            configurations=[
                SemanticConfiguration(
                    name=SEMANTIC_CONFIG,
                    prioritized_fields=SemanticPrioritizedFields(
                        title_field=SemanticField(field_name="title"),
                        content_fields=[SemanticField(field_name="content")],
                    ),
                )
            ]
        ),
    )
    _index_client().create_or_update_index(index)


def upload_docs() -> int:
    """Load every markdown file in data/ as one document. Returns the count uploaded."""
    docs = []
    for path in sorted(glob.glob(os.path.join(DATA_DIR, "*.md"))):
        text = open(path, encoding="utf-8").read()
        first_line = text.splitlines()[0]
        title = re.sub(r"^#\s*", "", first_line).strip()
        doc_id = os.path.splitext(os.path.basename(path))[0]
        docs.append({"id": doc_id, "title": title, "content": text, "category": "benefits"})
    _search_client().upload_documents(documents=docs)
    return len(docs)


def build_agent(agent_name: str, query_type: AzureAISearchQueryType) -> object:
    """Create an agent version with the AzureAISearch tool bound to the index."""
    if not MODEL:
        raise RuntimeError(
            "Set MODEL_DEPLOYMENT_NAME to a model deployment that supports Azure AI Search."
        )
    tool = AzureAISearchTool(
        azure_ai_search=AzureAISearchToolResource(
            indexes=[
                AISearchIndexResource(
                    project_connection_id=SEARCH_CONNECTION_ID,
                    index_name=INDEX_NAME,
                    query_type=query_type,
                    top_k=5,
                )
            ]
        )
    )
    instructions = (
        "You are the Contoso HR assistant. Answer employee questions using ONLY the Azure AI Search "
        "tool results. Cite the source document. If the answer is not in the results, say you don't "
        "know."
    )
    return project.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(model=MODEL, instructions=instructions, tools=[tool]),
    )


def run_agent(agent, question: str):
    """One turn against the grounded agent. Returns (answer, tool_used, annotation_count)."""
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
        if getattr(item, "type", None) in ("azure_ai_search_call", "file_search_call", "tool_call"):
            tool_used = True
        if getattr(item, "type", None) == "message":
            for block in getattr(item, "content", []) or []:
                annotations += len(getattr(block, "annotations", []) or [])
    return (response.output_text or ""), tool_used, annotations

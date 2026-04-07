# ADR-003: GA V2 SDK with Conversations and Responses API

## Status

Accepted (updated 2026-04-07 — SDK is now GA)

## Context

The Azure AI Foundry Agents SDK has two major versions:
- **V1 (classic, deprecated)**: `azure-ai-projects<1.0` + `azure-ai-agents` (separate packages), Thread-based conversation model with `AgentEventHandler`. Deprecated as of 2026; retirement March 2027.
- **V2 (GA)**: `azure-ai-projects>=2.0.0` (unified package), Conversations + OpenAI Responses API via `project.get_openai_client()`

V2 is GA, aligns with the new Foundry portal, and is the only actively developed path. The classic SDK will not receive new features.

Source: [Azure AI Projects client library for Python v2.0.1](https://learn.microsoft.com/python/api/overview/azure/ai-projects-readme?view=azure-python)

## Decision

All new (non-archived) demos target the GA V2 SDK:

**Package**: `azure-ai-projects>=2.0.0` (GA, not beta)

**Agent creation**:
```python
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool, CodeInterpreterTool

project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=DefaultAzureCredential())
agent = project.agents.create_version(
    agent_name="my-agent",
    definition=PromptAgentDefinition(model=model, instructions=instructions, tools=[...]),
)
```

**Conversations** (two patterns — both supported):

*Pattern A: Response chaining (simpler, used by enterprise_github_agent)*
```python
openai = project.get_openai_client()
# First message
response = openai.responses.create(
    input=user_input,
    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
    stream=True,
)
# Follow-up messages use previous_response_id
response = openai.responses.create(
    input=follow_up,
    previous_response_id=response.id,
    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
    stream=True,
)
```

*Pattern B: Explicit Conversations API (more control over conversation lifecycle)*
```python
openai = project.get_openai_client()
conversation = openai.conversations.create(
    items=[{"type": "message", "role": "user", "content": user_input}],
)
response = openai.responses.create(
    conversation=conversation.id,
    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
    stream=True,
)
# Follow-up messages:
openai.conversations.items.create(
    conversation_id=conversation.id,
    items=[{"type": "message", "role": "user", "content": follow_up}],
)
```

**Available tool classes** (from `azure.ai.projects.models`):
- Built-in: `CodeInterpreterTool`, `FileSearchTool`, `ImageGenTool`, `WebSearchTool`, `MCPTool`, `OpenApiTool`, `FunctionTool`, `AzureFunctionTool`, `ComputerUsePreviewTool`
- Connection-based: Azure AI Search, Bing Grounding, SharePoint, Fabric, Memory Search, Browser Automation, Agent-to-Agent (various preview)

V1 code is preserved in `archive/v1/` for reference but is not maintained.

## Consequences

- **Positive**: Demos showcase the GA, officially recommended API surface
- **Positive**: Single `azure-ai-projects` package simplifies dependencies
- **Positive**: GA status means stable API — no more beta churn
- **Risk**: Some tool types are still in preview (Computer Use, Browser Automation, etc.)
- **Mitigation**: Document which tools are GA vs preview in each demo's README

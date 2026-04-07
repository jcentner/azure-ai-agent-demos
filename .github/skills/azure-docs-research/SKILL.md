---
name: azure-docs-research
description: "Ground answers in official Microsoft documentation. USE WHEN: writing or modifying Azure AI Foundry agent code; answering questions about azure-ai-projects SDK, Foundry Agent Service, MCP tools, or any Azure AI service; validating SDK API surfaces, class names, or method signatures; resolving version discrepancies between v1 and v2 SDK. DO NOT USE FOR: general Python questions unrelated to Azure; non-Azure library usage."
user-invocable: true
disable-model-invocation: false
---

# Azure Documentation Research

Always consult official Microsoft documentation before writing or modifying Azure AI code. Never rely solely on training data for SDK APIs, class names, method signatures, or service behavior — these change frequently.

## When to Use

- Writing or modifying any `azure-ai-projects` SDK code
- Answering questions about Azure AI Foundry Agent Service
- Validating tool class names, method signatures, or import paths
- Checking what tools/capabilities are available for agents
- Resolving conflicts between what you "know" and what the docs say

## Procedure

### 1. Search docs first

Use the `microsoft_docs_search` MCP tool to find relevant documentation:

```
microsoft_docs_search("azure-ai-projects <topic>")
```

Good search queries:
- `azure-ai-projects Python SDK agents create_version PromptAgentDefinition`
- `Azure Foundry Agent Service MCPTool CodeInterpreterTool tools`
- `azure-ai-projects conversations responses create stream`
- `Azure Foundry agents MCP approval require_approval`

### 2. Search for code samples

Use the `microsoft_code_sample_search` MCP tool with `language: "python"`:

```
microsoft_code_sample_search("AIProjectClient agents create_version", language="python")
```

### 3. Fetch full page when needed

If search results are incomplete or you need detailed setup/prerequisites, fetch the full doc page:

```
microsoft_docs_fetch("<url from search results>")
```

### 4. Cross-reference key facts

Before writing code, verify these against docs:
- **Package name and version**: Currently `azure-ai-projects>=2.0.0` (GA)
- **Import paths**: `from azure.ai.projects import AIProjectClient`, `from azure.ai.projects.models import ...`
- **Agent creation**: `project.agents.create_version(agent_name=, definition=PromptAgentDefinition(...))`
- **Conversation API**: `openai.conversations.create()`, `openai.conversations.items.create()`, `openai.responses.create()`
- **Tool classes**: `MCPTool`, `CodeInterpreterTool`, `FileSearchTool`, `WebSearchTool`, `FunctionTool`, `ImageGenTool`, `OpenApiTool`, `AzureFunctionTool`, `ComputerUsePreviewTool`, etc.
- **Agent reference in responses**: `extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}}`

### 5. Flag uncertainty

If docs conflict with existing code or your knowledge, explicitly state the discrepancy and cite the doc URL. Never silently use stale information.

## Key Documentation URLs

- [SDK README (GA)](https://learn.microsoft.com/python/api/overview/azure/ai-projects-readme?view=azure-python) — Canonical reference for current API surface
- [Prompt Agent Quickstart](https://learn.microsoft.com/azure/foundry/agents/quickstarts/prompt-agent) — Agent creation walkthrough
- [MCP Tool Guide](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/model-context-protocol) — MCP integration patterns
- [SDK Samples on GitHub](https://aka.ms/azsdk/azure-ai-projects-v2/python/samples/) — Official code samples
- [Structured Inputs](https://learn.microsoft.com/azure/foundry/agents/how-to/structured-inputs) — Runtime template variables for agents

## Available Agent Tools (as of SDK v2.0.1)

Built-in (no connection required):
- Code Interpreter, File Search, Image Generation, Web Search, Computer Use (Preview), MCP, OpenAPI, Function Tool, Azure Functions

Connection-based (require Foundry project connection):
- Azure AI Search, Bing Grounding, Bing Custom Search (Preview), Microsoft Fabric (Preview), Microsoft SharePoint (Preview), Memory Search (Preview), Browser Automation (Preview), Agent-to-Agent (Preview)

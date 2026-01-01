# Plan: Enterprise GitHub Agent Demo

A Foundry-first demo connecting an Azure AI Agent (GPT-5.2) to the **official GitHub MCP Server** + **Code Interpreter**, demonstrating a complete workflow: create an issue, write code to solve it, and open a PR—all with user-delegated PAT authentication.

## SDK Reference

- **Package**: `azure-ai-projects` v2.0.0b2+ (preview)
- **API Version**: `2025-11-15-preview`
- **Docs**: https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme?view=azure-python-preview

## Steps

1. **Create folder structure** in `enterprise_github_agent/` with flat layout:
   - `create_agent.py` — Agent creation script
   - `ask_agent.py` — Interactive chat REPL
   - `README.md` — Documentation
   - `requirements.txt` — Dependencies
   - `.env.sample` — Environment template

2. **Implement create_agent.py** using new Foundry SDK:
   ```python
   from azure.ai.projects import AIProjectClient
   from azure.ai.projects.models import PromptAgentDefinition, MCPTool, CodeInterpreterTool
   
   tools = [
       MCPTool(
           server_label="github",
           server_url="https://api.githubcopilot.com/mcp/",
           require_approval="never",
       ),
       CodeInterpreterTool(),
   ]
   
   agent = project.agents.create_version(
       agent_name=agent_name,
       definition=PromptAgentDefinition(
           model=model,
           instructions=instructions,
           tools=tools,
       ),
   )
   ```

3. **Implement ask_agent.py** using OpenAI Responses API:
   ```python
   from azure.ai.projects.models import McpToolResource
   
   openai_client = project.get_openai_client()
   conversation = openai_client.conversations.create()
   
   # Add user message to conversation
   openai_client.conversations.items.create(
       conversation_id=conversation.id,
       items=[{"type": "message", "role": "user", "content": user_input}],
   )
   
   # Inject GitHub PAT at runtime via tool_resources (NOT persisted on agent)
   tool_resources = McpToolResource(
       server_label="github",
       headers={"Authorization": f"Bearer {github_pat}"},
   )
   
   # Stream response with agent reference
   stream = openai_client.responses.create(
       input="",  # Empty since message is in conversation
       conversation=conversation.id,
       extra_body={"agent": {"name": agent_name, "type": "agent_reference"}},
       tool_resources=[tool_resources],
       stream=True,
   )
   ```

4. **Write README.md** covering:
   - GitHub PAT creation (`repo` scope for full access)
   - Azure AI Foundry project setup
   - Architecture diagram
   - End-to-end demo walkthrough: *"Create an issue for adding a greeting function, write the code, then open a PR to close the issue."*

## Design Decisions

1. **Agent instructions**: Light guidance in system instructions (explain available capabilities) + freeform user prompts for natural demo flow. Agent discovers the issue→code→PR workflow organically.

2. **Target repo**: User provides a pre-existing test repo in `.env` (`GITHUB_REPO`). Simpler setup, avoids cleanup, documented in prerequisites.

3. **Streaming output**: Visible tool calls and streaming tokens. Handle event types:
   - `response.output_text.delta` — Text streaming
   - `response.mcp_call.started` — MCP tool invocation
   - `response.code_interpreter_call.started` — Code execution
   - `response.completed` — Final response

4. **PAT Security**: GitHub PAT injected at runtime via `McpToolResource(server_label, headers)` in `tool_resources` parameter—never stored on agent definition, never visible in Azure portal.

## Key Files

| File | Key Imports | Purpose |
|------|-------------|---------|
| `create_agent.py` | `AIProjectClient`, `PromptAgentDefinition`, `MCPTool`, `CodeInterpreterTool` | Create agent with tools attached |
| `ask_agent.py` | `AIProjectClient`, `McpToolResource` | Chat REPL with runtime PAT injection |

## Dependencies

```
azure-ai-projects --pre
azure-identity
python-dotenv
openai
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `PROJECT_ENDPOINT` | Yes | `https://<resource>.services.ai.azure.com/api/projects/<project>` |
| `MODEL_DEPLOYMENT_NAME` | Yes | e.g., `gpt-5.2` |
| `GITHUB_PAT` | Yes | GitHub Personal Access Token with `repo` scope |
| `AGENT_NAME` | No | Default: `enterprise-github-agent` |
| `GITHUB_REPO` | No | Default repo for demo prompts, e.g., `owner/repo` |

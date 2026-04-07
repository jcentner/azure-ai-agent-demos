# MCP (Model Context Protocol) — Basics for these Demos

This doc explains how MCP fits into the Azure AI Foundry **Agent** flow used in this repo,
and defines a few terms you’ll see in the scripts.

---

## What is MCP?

The Model Context Protocol is an open standard that enables developers to build secure, two-way connections between their data sources and AI-powered tools. The architecture is straightforward: developers can either expose their data through MCP servers or build AI applications (MCP clients) that connect to these servers.

Read more from Anthropic's release: [Model Context Protoco](https://www.anthropic.com/news/model-context-protocol)

- **MCP server**: a process that exposes a set of **tools** (capabilities) an AI agent can call.
- **MCP client**: the runtime (your Azure AI Foundry Agent) that connects to an MCP server and calls its tools.

The agent’s model decides *when* to call a tool; the MCP server implements *what the tool does*.

---

## Key terms

- **Tool definition**: The shape of a tool and its endpoint (e.g., MCP server URL).  
  We attach tool *definitions* to the **agent** when we create it.

- **Tool resources (run-time)**: Per-run configuration we pass when starting a **run**.  
  This is where we include **headers** like `Authorization: Bearer <token>`.  
  That keeps secrets **out of the agent definition**.

- **MCP approval behavior**:
  - `never` — The agent can call MCP tools without asking for approval (good for read-only).
  - `always` — Each tool call requires explicit approval (useful when tools can write/modify).
  - (Some SDKs allow per-tool maps; in these demos we use the global modes above.)
  - These options can only be set **at run-time** by passing the MCP tool_resources when creating a run. 
  
---

## Security tips

- Keep tokens out of your repo (use `.env`, environment variables, and `.gitignore`).
- Rotate tokens regularly; the demos read environment variables at run time, so rotation is straightforward.
- For write-capable tools, consider `approval_mode="always"` and narrow token scopes.

---

## Useful Documentation

- [Azure AI Agents SDK: Create an agent with MCP](https://github.com/Azure/azure-sdk-for-python/tree/azure-ai-agents_1.2.0b3/sdk/ai/azure-ai-agents#create-agent-with-mcp)
- [Azure AI Agents SDK reference](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-agents-readme?view=azure-python)
- [Azure AI Foundry - Connect to Model Context Protocol servers (preview)](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/model-context-protocol)
- [Azure AI Foundry - Code Samples: Hot to use the MCP tool (preview)](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/model-context-protocol-samples?pivots=python)
- [MCP Security Best Practices](https://modelcontextprotocol.io/specification/draft/basic/security_best_practices)
- [Understanding and mitigating security risks in MCP implementations - Microsoft Blog](https://techcommunity.microsoft.com/blog/microsoft-security-blog/understanding-and-mitigating-security-risks-in-mcp-implementations/4404667)

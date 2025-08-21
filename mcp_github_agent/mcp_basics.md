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
  
  In the scripts you can set this via the `.env` key `MCP_APPROVAL=never|always`.

- **Read-only vs write**:  
  The GitHub MCP server can be used read-only if your GitHub token (PAT) has read scopes only.  
  Our examples assume read-only usage.
  
---

## Troubleshooting (quick fixes)

- **“Unauthorized” / 401**  
  Ensure `GITHUB_OAUTH_TOKEN` *or* `GITHUB_PAT` is exported in your shell or present in `.env`.

- **Tool appears unused**  
  The model may decide not to call a tool for vague prompts. Ask explicitly (e.g., “List the 5 most recent open issues in `<owner>/<repo>`”).

- **Rate limiting / 403 or 429**  
  Try a different repo or wait; consider using an OAuth token with appropriate quotas.

- **Agent not found**  
  Run `create_agent.py` again to make a fresh agent and refresh `./.agent_id`.

---

## Security tips

- Keep tokens out of your repo (use `.env`, environment variables, and `.gitignore`).
- Rotate tokens regularly; the demos read environment variables at run time, so rotation is straightforward.
- For write-capable tools, consider `approval_mode="always"` and narrow token scopes.

---

## Useful Documentation

- [Azure AI Foundry - Model Context Protocol](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/model-context-protocol)
- [Azure AI Foundry - MCP Code Samples](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/model-context-protocol-samples?pivots=python)
- [MCP Security Best Practices](https://modelcontextprotocol.io/specification/draft/basic/security_best_practices)
- [Understanding and mitigating security risks in MCP implementations - Microsoft Blog](https://techcommunity.microsoft.com/blog/microsoft-security-blog/understanding-and-mitigating-security-risks-in-mcp-implementations/4404667)

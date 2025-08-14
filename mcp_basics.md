# MCP (Model Context Protocol) — Basics for this Demo

This doc explains how MCP fits into the Azure AI Foundry **Agent** flow used in this repo,
and defines a few terms you’ll see in the scripts.

---

## What is MCP?

- **MCP server**: a process that exposes a set of **tools** (capabilities) an AI agent can call.
  In this repo we use:
  - The **hosted GitHub MCP** (`https://api.githubcopilot.com/mcp/`) as the default, and
  - Optionally a **local MCP** (you can run one yourself), typically exposed via **ngrok** so it’s reachable from Azure.
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
  - `never` — The agent can call MCP tools without asking for approval (good for read-only demos).
  - `always` — Each tool call requires explicit approval (useful when tools can write/modify).
  - (Some SDKs allow per-tool maps; in this demo we use the global modes above.)
  
  In the scripts you can set this via the `.env` key `MCP_APPROVAL=never|always`.

- **Read-only vs write**:  
  The GitHub MCP server can be used read-only if your GitHub token (PAT) has read scopes only.  
  Our examples assume read-only usage.


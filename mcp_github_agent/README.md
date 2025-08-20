# Minimal GitHub MCP Demo (Azure AI Foundry Agents)

Two small scripts that show how to use the **GitHub MCP** tool from an Azure AI Foundry Agent:
- `create_agent.py` — creates an agent (no secrets persisted).
- `ask_agent.py` — simple chat loop that streams the agent's reply and prints basic tool activity.

## Setup

```bash
pip install -r requirements.txt
cp .env.sample .env
# Fill in PROJECT_ENDPOINT and MODEL_DEPLOYMENT_NAME
# Set GITHUB_OAUTH_TOKEN or GITHUB_PAT (OAuth is preferred if both are set)
```

## 1) Create the agent

```bash
python create_agent.py
```

This writes the new agent id to `./.agent_id`.

## 2) Chat with the agent

```bash
python ask_agent.py
```

- Type questions like:
  - `List the 5 most recent open issues in microsoft/vscode`
  - `Show open PR titles in azure/azure-sdk-for-python`
- The console shows:
  - streaming assistant tokens (so you see the reply as it's generated),
  - basic run/step events,
  - basic MCP tool call details (server label + tool name).

### Auth

- If `GITHUB_OAUTH_TOKEN` is set, it is used.
- Else if `GITHUB_PAT` is set, it is used.
- If neither is set, the run still executes, but GitHub MCP requests will fail.

### Why both PAT and OAuth?

- **PAT** mirrors personal workflows and quick demos.
- **OAuth** mirrors enterprise SSO/app flows and is closer to production auth practices.

### Notes

- Auth headers are added **at run time** via `tool_resources`; they are **not persisted** on the agent.
- `create_agent.py` always creates a fresh agent (intentionally no idempotency to keep the demo simple).


## Troubleshooting (quick fixes)

- **“Unauthorized” / 401**  
  Ensure `GITHUB_OAUTH_TOKEN` *or* `GITHUB_PAT` is exported in your shell or present in `.env`.

- **Tool appears unused**  
  The model may decide not to call a tool for vague prompts. Ask explicitly (e.g., “List the 5 most recent open issues in `<owner>/<repo>`”).

- **Rate limiting / 403 or 429**  
  Try a different repo or wait; consider using an OAuth token with appropriate quotas.

- **Agent not found**  
  Run `create_agent.py` again to make a fresh agent and refresh `./.agent_id`.



# Enterprise GitHub Agent (Azure AI Foundry + MCP)

An Azure AI Foundry Agent with **GitHub MCP integration** and **Code Interpreter**, demonstrating a complete developer workflow: create issues, write code, and open pull requests—all through natural language.

```
┌─────────────────┐      ┌──────────────────────┐      ┌─────────────────┐
│   User (CLI)    │◄────►│  Azure AI Foundry    │◄────►│  GitHub MCP     │
│                 │      │  Agent (GPT-5.2)     │      │  (Official)     │
└─────────────────┘      │                      │      └────────┬────────┘
                         │  + Code Interpreter  │               │
                         └──────────────────────┘               ▼
                                                         ┌─────────────────┐
                                                         │   GitHub API    │
                                                         │   (your repos)  │
                                                         └─────────────────┘
```

## Features

- **GitHub MCP Server** (official): Create issues, push files, open PRs, list repos
- **Code Interpreter**: Write and test Python code before pushing
- **Streaming output**: See tokens and tool calls in real-time
- **PAT authentication**: User-scoped access via Personal Access Token (not persisted on agent)

## Repository Map

```
enterprise_github_agent/
├── README.md           # This file
├── requirements.txt    # Python dependencies
├── .env.sample         # Environment template
├── create_agent.py     # Creates the agent (run once)
└── ask_agent.py        # Interactive chat REPL
```

## Prerequisites

1. **Python 3.11+**
2. **Azure CLI** - logged in (`az login`)
3. **Azure AI Foundry project** with:
   - GPT-5.2 (or compatible model) deployed
   - Public network access enabled (required for MCP)
4. **GitHub Personal Access Token** with `repo` scope

## Quickstart

### 1. Setup environment

```bash
cd enterprise_github_agent

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.sample .env
# Edit .env with your values
```

### 2. Create GitHub PAT

1. Go to [GitHub Settings → Tokens](https://github.com/settings/tokens)
2. Click **Generate new token (classic)**
3. Select scopes:
   - `repo` - Full control of private repositories
4. Copy the token to your `.env` file as `GITHUB_PAT`

> **Security**: The PAT is passed at runtime via MCP headers and is **never persisted** on the agent.

### 3. Create the agent

```bash
python create_agent.py
```

This creates the agent in your Azure AI Foundry project and saves the agent name to `.agent_name`.

### 4. Chat with the agent

```bash
python ask_agent.py
```

## Demo Walkthrough

### Example: Issue → Code → PR workflow

```
> Create an issue in myuser/test-repo titled "Add greeting function" with description "Add a Python function that returns a greeting message"

[step] type=tool_calls status=completed
  [tool_call 1] type=mcp_tool
    mcp.server_label=github name=create_issue

Created issue #42 in myuser/test-repo: "Add greeting function"

> Now write a Python greeting function, test it with Code Interpreter, then push it to the repo

[step] type=tool_calls status=completed
  [tool_call 1] type=code_interpreter
    code_interpreter.input: def greet(name: str) -> str:
        return f"Hello, {name}!"...

Code executed successfully. Testing:
  greet("World") → "Hello, World!" ✓

[step] type=tool_calls status=completed
  [tool_call 2] type=mcp_tool
    mcp.server_label=github name=create_or_update_file

Pushed greet.py to myuser/test-repo on branch 'feature/greeting'

> Open a PR to merge this into main, referencing issue #42

[step] type=tool_calls status=completed
  [tool_call 1] type=mcp_tool
    mcp.server_label=github name=create_pull_request

Created PR #43: "Add greeting function (Fixes #42)"
```

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `PROJECT_ENDPOINT` | Yes | Azure AI Foundry project endpoint |
| `MODEL_DEPLOYMENT_NAME` | Yes | Model deployment (e.g., `gpt-5.2`) |
| `GITHUB_PAT` | Yes | GitHub Personal Access Token |
| `AGENT_NAME` | No | Agent name (default: `enterprise-github-agent`) |
| `GITHUB_REPO` | No | Default repo for demo prompts (e.g., `owner/repo`) |

## Available GitHub Tools (default toolset)

The official GitHub MCP server exposes these tool categories:

| Toolset | Description |
|---------|-------------|
| `context` | Current user and GitHub context |
| `repos` | Repository operations (list, get, create files, branches) |
| `issues` | Issue management (create, update, close, comment) |
| `pull_requests` | PR operations (create, merge, review) |
| `users` | User information |

See [GitHub MCP Server docs](https://github.com/github/github-mcp-server) for full tool reference.

## Security Model

```
┌─────────────────────────────────────────────────────────────┐
│                    Runtime Only                              │
│  ┌─────────────┐                                            │
│  │ GITHUB_PAT  │──► MCP Headers ──► GitHub API              │
│  └─────────────┘    (per-request)                           │
│        │                                                     │
│        └── NOT stored on agent definition                   │
│            NOT visible in Azure AI Foundry portal           │
└─────────────────────────────────────────────────────────────┘
```

- **PAT is injected at runtime** via `McpTool.update_headers()` and `tool_resources`
- **Agent only has permissions** that the PAT grants
- **Revoke access** by regenerating or deleting the PAT

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Agent not found" | Run `create_agent.py` again |
| "401 Unauthorized" from GitHub | Check GITHUB_PAT is valid and has `repo` scope |
| "Tool call not executing" | Verify MCP server URL is reachable (requires public network) |
| "Rate limit exceeded" | Wait or use a different PAT; check Azure model quotas |
| No streaming output | Ensure `azure-ai-agents>=1.2.0b2` is installed |

## Extending the Demo

### Add more GitHub toolsets

By default, this demo uses the `default` toolset. To enable additional tools (e.g., `actions`, `discussions`):

```python
# In ask_agent.py, modify the MCP URL to include toolsets:
GITHUB_MCP_URL = "https://api.githubcopilot.com/mcp/?toolsets=default,actions"
```

## Related Docs

- [Azure AI Foundry Quickstart](https://learn.microsoft.com/en-us/azure/ai-foundry/quickstarts/get-started-code)
- [Azure AI Agents MCP Integration](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/model-context-protocol)
- [GitHub MCP Server](https://github.com/github/github-mcp-server)
- [Code Interpreter Tool](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/code-interpreter)

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
- **Streaming output**: Real-time text streaming with visible tool calls (🔧 MCP, 🐍 Code Interpreter)
- **MCP approval flow**: Tool calls require approval with runtime PAT injection
- **PAT authentication**: User-scoped access via Personal Access Token (never persisted on agent)

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

[assistant]
  🔧 [mcp_call] server=github tool=create_issue
  ⏳ [mcp_approval] server=github tool=create_issue
  ✅ [approving 1 MCP tool call(s)...]
  ✓ [mcp_call] completed

I've created issue #42 in myuser/test-repo titled "Add greeting function" with your description.

> Now write a Python greeting function, test it with Code Interpreter, then push it to the repo

[assistant]
I'll write a greeting function, test it, and then push it to the repository.

  🐍 [code_interpreter] executing...
def greet(name: str) -> str:
    return f"Hello, {name}!"

# Test the function
print(greet("World"))
  ✓ [code_interpreter] completed

The function works correctly - it outputs "Hello, World!" ✓

Now I'll push this to the repository:
  🔧 [mcp_call] server=github tool=create_or_update_file
  ⏳ [mcp_approval] server=github tool=create_or_update_file
  ✅ [approving 1 MCP tool call(s)...]
  ✓ [mcp_call] completed

Done! I've pushed `greet.py` to myuser/test-repo on branch 'feature/greeting'.

> Open a PR to merge this into main, referencing issue #42

[assistant]
  🔧 [mcp_call] server=github tool=create_pull_request
  ⏳ [mcp_approval] server=github tool=create_pull_request
  ✅ [approving 1 MCP tool call(s)...]
  ✓ [mcp_call] completed

Created PR #43: "Add greeting function (Fixes #42)" - ready for review!
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
│                    Runtime Only (Per-Request)               │
│  ┌─────────────┐                                            │
│  │ GITHUB_PAT  │──► MCP Approval Response ──► GitHub API    │
│  └─────────────┘    (headers injected)                      │
│        │                                                     │
│        └── NOT stored on agent definition                   │
│            NOT visible in Azure AI Foundry portal           │
│            Injected only when approving MCP tool calls      │
└─────────────────────────────────────────────────────────────┘
```

- **PAT is injected at runtime** via `headers` in MCP approval responses
- **Tool calls require approval** (`require_approval="always"` on agent)
- **Agent only has permissions** that the PAT grants
- **Revoke access** by regenerating or deleting the PAT

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Agent not found" | Run `create_agent.py` again |
| "401 Unauthorized" from GitHub | Check GITHUB_PAT is valid and has `repo` scope |
| "mcp_approval_request" not handled | Ensure `require_approval="always"` is set on the MCPTool |
| "Rate limit exceeded" | Wait or use a different PAT; check Azure model quotas |
| Import errors | Ensure `azure-ai-projects>=2.0.0b2` is installed |

## Related Docs

- [Azure AI Projects SDK (PyPI)](https://pypi.org/project/azure-ai-projects/)
- [Azure AI Projects SDK Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples)
- [MCP Tool Sample](https://github.com/Azure/azure-sdk-for-python/blob/azure-ai-projects_2.0.0b2/sdk/ai/azure-ai-projects/samples/agents/tools/sample_agent_mcp.py)
- [Azure AI Foundry Quickstart](https://learn.microsoft.com/en-us/azure/ai-foundry/quickstarts/get-started-code)
- [GitHub MCP Server](https://github.com/github/github-mcp-server)
- [Code Interpreter Tool](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/code-interpreter)

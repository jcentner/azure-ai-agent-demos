# Enterprise GitHub Agent (Azure AI Foundry + MCP)

An Azure AI Foundry Agent with **GitHub MCP integration** and **Code Interpreter**, demonstrating a complete developer workflow: create issues, write code, and open pull requests—all through natural language.

```
┌─────────────────┐      ┌──────────────────────┐      ┌─────────────────┐
│   User (CLI)    │◄────►│  Azure AI Foundry    │◄────►│  GitHub MCP     │
│                 │      │  Agent               │      │  (Official)     │
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
- **MCP approval flow**: Tool calls require approval (auto-approved for demo)
- **Project connection auth**: GitHub PAT stored in a Foundry project connection (not on the agent)

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
   - An OpenAI model deployed (configurable via `MODEL_DEPLOYMENT_NAME`)
   - Public network access enabled (required for MCP)
4. **GitHub Personal Access Token** with `repo` scope
5. **Foundry project connection** for the GitHub MCP server (stores the PAT)

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
4. Copy the token — you'll need it for the project connection

### 3. Create the MCP project connection

1. Open the [Microsoft Foundry portal](https://ai.azure.com)
2. Navigate to your project
3. Go to **Connected resources** (or **Settings → Connections**)
4. Click **+ New connection** → **Custom keys**
5. Configure:
   - **Connection name**: e.g., `github-mcp` (use this as `MCP_CONNECTION_NAME` in `.env`)
   - **Credential name**: `Authorization`
   - **Credential value**: `Bearer <your-github-pat>`
6. Save the connection

> **Security**: The PAT is stored in the Foundry project connection, not on the agent definition itself.

### 4. Create the agent

```bash
python create_agent.py
```

This creates the agent in your Azure AI Foundry project and saves the agent name to `.agent_name`.

### 5. Chat with the agent

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
| `MODEL_DEPLOYMENT_NAME` | Yes | Model deployment name |
| `MCP_CONNECTION_NAME` | Yes | Foundry project connection name for GitHub MCP auth |
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
│                  Foundry Project Connection                  │
│  ┌─────────────┐                                            │
│  │ GITHUB_PAT  │──► Project Connection ──► GitHub MCP Server  │
│  └─────────────┘    (stores cred)       (receives header)   │
│        │                                                     │
│        └── NOT stored on agent definition                    │
│            Stored in project-level connection only           │
│            MCP tool calls still require approval             │
└─────────────────────────────────────────────────────────────┘
```

- **PAT stored in Foundry project connection** — not on the agent definition
- **MCP tool calls require approval** (`require_approval="always"` on agent)
- **Agent only has permissions** that the PAT grants
- **Revoke access** by updating or deleting the project connection

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Agent not found" | Run `create_agent.py` again |
| "401 Unauthorized" from GitHub | Check that the project connection has a valid PAT with `repo` scope |
| "mcp_approval_request" not handled | Ensure `require_approval="always"` is set on the MCPTool |
| "Rate limit exceeded" | Wait or use a different PAT; check Azure model quotas |
| Import errors | Ensure `azure-ai-projects>=2.0.0` is installed |

## Related Docs

- [Azure AI Projects SDK (PyPI)](https://pypi.org/project/azure-ai-projects/)
- [Azure AI Projects SDK Samples](https://aka.ms/azsdk/azure-ai-projects-v2/python/samples/)
- [MCP Tool Documentation](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/model-context-protocol?pivots=python)
- [MCP Authentication](https://learn.microsoft.com/azure/foundry/agents/how-to/mcp-authentication)
- [Azure AI Foundry Quickstart](https://learn.microsoft.com/azure/foundry/agents/quickstart)
- [GitHub MCP Server](https://github.com/github/github-mcp-server)
- [Code Interpreter Tool](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/code-interpreter)

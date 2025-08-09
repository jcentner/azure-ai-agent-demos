# Demo Flow

This document outlines the steps to demonstrate the sample Azure AI Foundry agent configured with the GitHub MCP tool and Bing Grounding.

## Prerequisites

1. **Azure AI Foundry Project**: An active project in a supported region (`westus`, `westus2`, `uaenorth`, `southindia`, or `switzerlandnorth`) with the `gpt-4o` model deployed.
2. **GitHub PAT**: A fine-grained personal access token with read-only permissions to the repositories you want to access.
3. **Grounding with Bing Search**: A Bing grounding connection configured within your Foundry project and its connection ID.
4. **Python environment**: Python 3.10+ with packages listed in `requirements.txt`. Use a virtual environment for isolation.

## Running the simple MCP demo

1. Set environment variables:

```
export PROJECT_ENDPOINT="https://<foundry>.services.ai.azure.com/api/projects/<project>"
export MODEL_DEPLOYMENT_NAME="gpt-4o"
export GITHUB_PAT="<your_read_only_pat>"
```

2. Install dependencies:

```
pip install -r requirements.txt
```

3. Run the script:

```
python src/agent_mcp_github.py
```

4. The script will:
   - Create a new agent with the MCP tool.
   - Create a thread and ask for the five most recent open issues in a specified repository.
   - Print the assistant’s reply listing those issues.

## Running the MCP + Bing demo

1. Set additional environment variable for the Bing connection:

```
export AZURE_BING_CONNECTION_ID="/subscriptions/.../connections/<connection_name>"
```

2. Run the script:

```
python src/agent_mcp_github_bing.py
```

3. This script:
   - Creates an agent with both GitHub MCP and Bing Grounding tools.
   - Provides detailed instructions to bias Bing searches toward official Microsoft sources.
   - Asks the assistant to fetch guidance on using Foundry Agent Service with MCP and list open issues in the `microsoft/azure-ai-projects` repository.
   - Outputs the assistant’s reply along with citations for web sources.

## Notes

- The PAT is supplied at runtime via tool headers; it is not stored in the agent configuration.
- The examples rely on default prompt instructions; modify them to suit your scenarios.
- Both scripts use `create_and_process(...)` to execute the entire run synchronously for simplicity.

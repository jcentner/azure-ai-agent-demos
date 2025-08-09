# Azure AI Foundry MCP and Bing Demo

This repository contains sample code and instructions for creating an Azure AI Foundry agent that uses the GitHub Model Context Protocol (MCP) tool and optionally Grounding with Bing Search to answer questions and query GitHub repositories.

## Prerequisites

1. An Azure AI Foundry project in a supported region for the MCP tool (for example, westus, westus2, uaenorth, southindia, or switzerlandnorth).
2. A deployed model (such as **gpt-4o**) in the project.
3. A GitHub personal access token (PAT) with read access to the repository you want to query.
4. *(Optional)* A Grounding with Bing Search resource connected to your project if you want to use the Bing demo.

## Setup

Follow these steps to get started:

1. Ensure you have Python installed. Clone this repository or download its contents.
2. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and fill in your environment variables:
   - **`PROJECT_ENDPOINT`** – The endpoint of your Azure AI Foundry project, e.g.:

     ``
     https://<foundry>.services.ai.azure.com/api/projects/<project>
     ``

   - **`MODEL_DEPLOYMENT_NAME`** – The name of your model deployment (e.g., `gpt-4o`).
   - **`GITHUB_PAT`** – Your GitHub PAT for read-only access to the target repository.
   - **`AZURE_BING_CONNECTION_ID`** – The connection ID for your Bing grounding resource (only needed for the Bing demo).

## Running the demos

### Minimal MCP demo (read‑only)

`src/agent_mcp_github.py` creates an agent with a GitHub MCP tool configured to use the hosted GitHub MCP server and lists the most recent open issues for a repository. Run it with:

```bash
python src/agent_mcp_github.py
```

You can change the repository being queried by editing the `repo = "microsoft/vscode"` line in the script.

### MCP + Bing demo

`src/agent_mcp_github_bing.py` adds a Grounding with Bing Search tool connected via your Bing resource and instructs the agent to search Microsoft Learn and Microsoft‑owned GitHub repositories when answering Azure AI Foundry questions. Run it with:

```bash
python src/agent_mcp_github_bing.py
```

Make sure you have set `AZURE_BING_CONNECTION_ID` in your `.env` file when running this script. The script prints the assistant’s response and, if present, any citations returned by the Bing grounding tool.

## Repository structure

- **`src/agent_mcp_github.py`** – Minimal read‑only GitHub MCP demo script.
- **`src/agent_mcp_github_bing.py`** – GitHub MCP demo with Grounding with Bing Search.
- **`docs/demo_flow.md`** – A detailed walkthrough of the demo flow.
- **`.env.example`** – Sample environment variables to copy to your own `.env`.
- **`requirements.txt`** – Python dependencies.

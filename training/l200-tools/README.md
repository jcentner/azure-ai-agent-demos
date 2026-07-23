# L200 Foundry tools training labs

These labs accompany the L200 training module for Microsoft Foundry Agents support engineers.
Complete the workstation setup once, then work through the labs in order:

1. [Lab 1: Toolbox versioning](lab1-toolbox/)
2. [Lab 2: Azure AI Search grounding](lab2-ai-search/)
3. [Lab 3: Foundry IQ knowledge base](lab3-foundry-iq/)

Lab 3 reuses the Azure AI Search index created in Lab 2.

## What you need

- A Windows, macOS, or Linux workstation.
- Python 3.11 or 3.12.
- Git.
- Azure CLI.
- Access to the Foundry and Azure resources listed in each lab.

Visual Studio Code is optional. If you use it, install the Microsoft Python extension.

## Step 1: Install the workstation tools

### Windows

1. Install [Git for Windows](https://git-scm.com/download/win).
2. Install [Python 3.12](https://www.python.org/downloads/windows/). Select **Add python.exe to
   PATH** during installation.
3. Install the [Azure CLI for Windows](https://learn.microsoft.com/cli/azure/install-azure-cli-windows).
4. Open a new PowerShell window and verify:

   ```powershell
   git --version
   py -3.12 --version
   az version
   ```

### macOS or Linux

Install:

- [Git](https://git-scm.com/downloads);
- [Python 3.11 or 3.12](https://www.python.org/downloads/);
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli).

Verify:

```bash
git --version
python3 --version
az version
```

## Step 2: Download the lab files

Clone the repository:

```bash
git clone --branch l200-tools-v1.0.2 --depth 1 https://github.com/jcentner/azure-ai-agent-demos.git
cd azure-ai-agent-demos/training/l200-tools
```

If Git is unavailable, download the
[l200-tools-v1.0.2 ZIP archive](https://github.com/jcentner/azure-ai-agent-demos/archive/refs/tags/l200-tools-v1.0.2.zip),
extract it, and open `training/l200-tools`.

## Step 3: Create the shared Python environment

Use one virtual environment for all three labs.

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks the activation script, allow it for the current window and retry:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The prompt normally shows `(.venv)` while the environment is active. Activate it again whenever you
open a new terminal.

## Step 4: Sign in to Azure

```bash
az login
az account show
```

If the browser cannot open, use:

```bash
az login --use-device-code
```

Use the non-production subscription assigned to you for support-engineer training. Do not use a
customer or production subscription. Confirm the active subscription and change it when needed:

```bash
az account set --subscription "<subscription-name-or-id>"
```

## Step 5: Configure the labs

Create your local configuration file.

### Windows PowerShell

```powershell
Copy-Item .env.sample .env
notepad .env
```

### macOS or Linux

```bash
cp .env.sample .env
```

Fill in the values:

| Variable | Labs | Where to find it |
|---|---|---|
| `PROJECT_ENDPOINT` | 1, 2, 3 | Foundry project **Overview** page. It ends with `/api/projects/<project>`. |
| `MODEL_DEPLOYMENT_NAME` | 1, 2, 3 | Foundry **Models + endpoints**. Choose a current deployment that supports the lab's tools. |
| `SEARCH_CONNECTION_NAME` | 2, 3 | Foundry project's connected resources. Use the Azure AI Search connection name. |
| `PROJECT_RESOURCE_ID` | 3 | Azure portal JSON view for the Foundry project resource. |
| `AOAI_ENDPOINT` | 3 | Azure portal endpoint for the Foundry resource, ending in `.openai.azure.com`. |
| `MODEL_NAME` | 3 | Optional. Set only when the underlying model name differs from the deployment name. |

The values below are examples only. Your resource, project, connection, deployment, subscription,
and resource-group names will be different:

```dotenv
PROJECT_ENDPOINT=https://support-lab-ai.services.ai.azure.com/api/projects/support-lab
MODEL_DEPLOYMENT_NAME=support-lab-model
SEARCH_CONNECTION_NAME=support-lab-search
PROJECT_RESOURCE_ID=/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-support-lab/providers/Microsoft.CognitiveServices/accounts/support-lab-ai/projects/support-lab
AOAI_ENDPOINT=https://support-lab-ai.openai.azure.com
MODEL_NAME=gpt-5-mini
```

`MODEL_DEPLOYMENT_NAME` is the name assigned to the deployment. `MODEL_NAME` is the underlying
catalog model shown in the deployment details. Select a current model supported by the tools in the
lab instead of copying the example model automatically.

Do not commit `.env`. It is excluded by the repository's `.gitignore`.

## Step 6: Check the setup

Run the check for the lab you are about to start:

```bash
python check_setup.py --lab 1
```

Use `--lab 2`, `--lab 3`, or `--lab all` as needed. Continue only after every check reports
`[PASS]`.

## Running the labs

Keep the virtual environment active, then change to the lab directory:

```bash
cd lab1-toolbox
```

Follow that directory's README. Return to this directory before starting the next lab:

```bash
cd ..
python check_setup.py --lab 2
cd lab2-ai-search
```

Do not run the Lab 2 cleanup if you plan to continue directly to Lab 3.

## Common setup problems

| Symptom | Fix |
|---|---|
| `python` opens the Microsoft Store or is not recognized | On Windows, use `py -3.12` to create the environment, then use `python` after activation. |
| `No virtual environment is active` | Run the activation command from Step 3. |
| `ModuleNotFoundError` | Activate `.venv`, then run `python -m pip install -r requirements.txt`. |
| `az` is not recognized | Install Azure CLI, close the terminal, and open a new one. |
| Azure authentication fails | Run `az login`, confirm `az account show`, and verify the intended subscription. |
| An environment value is missing | Edit `.env`, then rerun `check_setup.py`. |

When you finish all labs:

```bash
deactivate
```

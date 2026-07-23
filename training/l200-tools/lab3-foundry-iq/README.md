# Lab 3: Foundry IQ knowledge base

This lab reuses the Lab 2 index as a Foundry IQ knowledge source. It creates one model-backed
knowledge base and connects two agents through the same MCP project connection.

Follow the L200 module for the teaching steps and screenshots. This README is the operational
companion for running the code.

## Before you begin

1. Complete Lab 2 and keep the `contoso-benefits` index.
2. Complete the [shared workstation setup](../README.md).
3. Activate `training/l200-tools/.venv`.
4. Fill in these values in `training/l200-tools/.env`:
   - `PROJECT_ENDPOINT`
   - `MODEL_DEPLOYMENT_NAME`
   - `SEARCH_CONNECTION_NAME`
   - `PROJECT_RESOURCE_ID`
   - `AOAI_ENDPOINT`
   - `MODEL_NAME` only when it differs from the deployment name
5. Choose a model supported by Foundry IQ for query planning and answer synthesis. The agent model
   must also support MCP.
6. From `training/l200-tools`, run:

   ```bash
   python check_setup.py --lab 3
   cd lab3-foundry-iq
   ```

## Required roles

| Identity | Role and scope |
|---|---|
| Foundry project managed identity | `Search Index Data Reader` on the Search service. The Lab 2 data-contributor grant also provides read access. |
| Search service managed identity | `Cognitive Services User` on the Foundry model resource. |
| Your user account | `Search Service Contributor` on Search, plus `Foundry User` and `Foundry Project Manager` on the Foundry resource. |

If either managed identity is missing its role, the knowledge resources can look correct while
runtime retrieval fails.

## Run order

| Script | Purpose |
|---|---|
| `00_reset.py` | Delete the two agents, project connection, knowledge base, and knowledge source. |
| `01_create_kb.py` | Create the knowledge source, model-backed knowledge base, and RemoteTool connection. |
| `02_query.py` | Connect two agents and verify cited multi-part answers and off-topic declines. |

Run each command separately:

```bash
python 00_reset.py
python 01_create_kb.py
python 02_query.py
```

The lab succeeds when `02_query.py` prints:

```text
PASS: both agents share one KB, answer a multi-part question with citations,
      and decline an off-topic question.
```

## Cleanup

```bash
python 00_reset.py
```

The Lab 2 Search index is intentionally preserved.

## Common execution problems

| Symptom | Check |
|---|---|
| `tool_user_error: Access denied` | Verify both sides of the managed-identity chain and allow time for role propagation. |
| `A Knowledge Base model must be specified...` | Verify `MODEL_DEPLOYMENT_NAME`, `MODEL_NAME`, and `AOAI_ENDPOINT`. |
| Agent cannot connect to the MCP endpoint | Verify the project connection target, audience, and `ProjectManagedIdentity` authentication. |
| Answer has no citations | Confirm `knowledge_base_retrieve` was called and the model supports MCP. |

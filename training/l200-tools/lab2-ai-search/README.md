# Lab 2: Azure AI Search grounding

This lab attaches one Azure AI Search index directly to one agent. The agent must use the Search
tool, cite indexed content, and decline a question that the index cannot answer.

Follow the L200 module for the teaching steps and screenshots. This README is the operational
companion for running the code.

## Before you begin

1. Complete the [shared workstation setup](../README.md).
2. Activate `training/l200-tools/.venv`.
3. Fill in `PROJECT_ENDPOINT`, `MODEL_DEPLOYMENT_NAME`, and `SEARCH_CONNECTION_NAME` in
   `training/l200-tools/.env`.
4. Choose a current model deployment that supports Azure AI Search.
5. Confirm the Search project connection uses Microsoft Entra authentication.
6. From `training/l200-tools`, run:

   ```bash
   python check_setup.py --lab 2
   cd lab2-ai-search
   ```

## Required roles

Assign roles on the Azure AI Search service:

| Identity | Roles |
|---|---|
| Your user account | `Search Service Contributor` and `Search Index Data Contributor` |
| Foundry project managed identity | `Search Index Data Contributor` and `Search Service Contributor` |

The agent reaches Search as the **project** managed identity, not the parent Foundry account
identity. Role assignments can take several minutes to propagate.

## Run order

| Script | Purpose |
|---|---|
| `00_reset.py` | Delete the lab index and agent for a clean rerun. |
| `01_create_index.py` | Create `contoso-benefits` and upload the six documents in `data/`. |
| `02_query.py` | Create the grounded agent and verify cited answers and an off-topic decline. |

Run each command separately:

```bash
python 00_reset.py
python 01_create_index.py
python 02_query.py
```

The lab succeeds when `02_query.py` prints its final `PASS` result.

## Cleanup

If you are continuing to Lab 3, do not run cleanup. Lab 3 reuses the `contoso-benefits` index.

Otherwise:

```bash
python 00_reset.py
```

## Common execution problems

| Symptom | Check |
|---|---|
| `Access denied` or `tool_user_error` | Verify roles are assigned to the Foundry project managed identity and allow time for propagation. |
| `00_reset.py` says the index is referenced by a knowledge source | Lab 3 still references the index. Run `../lab3-foundry-iq/00_reset.py` first, or continue because Lab 2 reuses the existing index. |
| The index contains no documents | Confirm the six Markdown files exist in `data/` and rerun `01_create_index.py`. |
| The agent returns an uncited answer | Confirm the Search tool is attached and the selected model supports Azure AI Search. |
| The wrong Search service is used | Verify `SEARCH_CONNECTION_NAME` in `../.env`. |

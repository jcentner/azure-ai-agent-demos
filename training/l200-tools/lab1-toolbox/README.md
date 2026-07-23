# Lab 1: Toolbox versioning

This lab demonstrates the Toolbox build, break, diagnose, and fix workflow. The consumer endpoint
serves the default Toolbox version. Creating a later version does not change the default until that
version is promoted.

Follow the L200 module for the teaching steps and screenshots. This README is the operational
companion for running the code.

## Before you begin

1. Complete the [shared workstation setup](../README.md).
2. Activate `training/l200-tools/.venv`.
3. Fill in `PROJECT_ENDPOINT` and `MODEL_DEPLOYMENT_NAME` in `training/l200-tools/.env`.
4. Choose a current model deployment that supports MCP, Web Search, and Code Interpreter.
5. From `training/l200-tools`, run:

   ```bash
   python check_setup.py --lab 1
   cd lab1-toolbox
   ```

## Run order

| Script | Purpose |
|---|---|
| `00_reset.py` | Delete the lab Toolbox so the exercise starts clean. |
| `01_build_v1.py` | Create version 1 with Web Search. The first version becomes the default. |
| `02_use_v1.py` | Show two agents discovering tools from the shared consumer endpoint. |
| `03_build_v2.py` | Create version 2 with Web Search and Code Interpreter without promoting it. |
| `04_diagnose.py` | Compare the consumer endpoint, default version, and available versions. |
| `05_fix.py` | Promote version 2 and verify Code Interpreter becomes available. |

Run each command separately so you can inspect the portal and module screenshots between steps:

```bash
python 00_reset.py
python 01_build_v1.py
python 02_use_v1.py
python 03_build_v2.py
python 04_diagnose.py
python 05_fix.py
```

The lab succeeds when `05_fix.py` prints:

```text
PASS: code_interpreter is now available to the agent after promotion.
```

## Cleanup

```bash
python 00_reset.py
```

## Common execution problems

| Symptom | Check |
|---|---|
| A required environment value is missing | Edit `../.env`, then rerun `python ../check_setup.py --lab 1`. |
| Azure authentication fails | Run `az login` and confirm the intended subscription with `az account show`. |
| Code Interpreter is absent after creating version 2 | Continue to `04_diagnose.py`; version 2 is intentionally not the default yet. |
| The endpoint is updated but an existing agent still sees the old list | Use the fresh server label in `05_fix.py`; the runtime can cache MCP tool discovery. |

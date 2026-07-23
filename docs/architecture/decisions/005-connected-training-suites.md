# ADR-005: Connected Training Suites

## Status

Accepted

## Context

The repository's standalone demos are independent examples built around `create_agent.py` and
`ask_agent.py`. The L200 Foundry tools module is different: it teaches a staged build, break,
diagnose, and fix workflow across three labs. Lab 3 intentionally reuses the Azure AI Search index
from Lab 2.

Forcing these labs into the standalone demo shape would either duplicate resources and setup or hide
the sequence that the training is designed to teach.

## Decision

Connected learning content lives under `training/<suite-name>/`.

A training suite:

- may use multiple numbered scripts instead of the two-script demo pattern;
- may share one virtual environment, dependency file, and `.env` file;
- may carry state from one lab to the next when the dependency is explicit;
- must provide a top-level clean-workstation setup guide;
- must pin the validated direct dependencies;
- must provide a preflight setup check;
- must provide a README for every lab;
- must not change the architecture rules for standalone demos.

The L200 tools suite lives at `training/l200-tools/`.

## Consequences

### Positive

- New learners configure Python and Azure authentication once.
- The code preserves the same sequence taught by the module.
- Standalone demos remain simple and independently runnable.
- Future contributors can distinguish training content from capability demos.

### Negative

- Training suites use a different directory convention from root demos.
- Cross-lab dependencies require clearer cleanup guidance.
- Shared dependency pins must be refreshed when the training module is revalidated.

### Neutral

- A training suite can later be split into standalone demos if independent examples are needed.

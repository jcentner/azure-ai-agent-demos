# Azure AI Agent Demos — Roadmap

## Current State

See [CURRENT-STATE.md](CURRENT-STATE.md) for the latest checkpoint.

## Phases

| Phase | Title | Status |
|-------|-------|--------|
| 0 | Vision Baseline | Complete |
| 1 | Enterprise GitHub Agent | Not started |
| 2 | MCP MS Learn Agent v2 | Not started |
| 3 | MCP Local Server Agent v2 | Not started |
| 4 | Cross-cutting polish | Not started |
| 5 | Fabric Data Agent | Not started |
| 6 | Multi-Tool Knowledge Worker | Not started |
| 7 | Browser Automation Agent | Not started |

Phase plans are stored in [phases/](phases/).

## How Phases Work

1. **Plan** — `/phase-plan` creates a planning doc with features, dependencies, and acceptance criteria
2. **Detail** — `/implementation-plan` creates a file-by-file checklist
3. **Implement** — `/implement` executes the plan with tests
4. **Review** — `/code-review` reviews code quality, architecture, and security
5. **Complete** — `/phase-complete` updates docs, records lessons, marks done

The autonomous builder agent performs this cycle automatically with enforced review gates. The prompts are available as manual overrides for human-driven sessions.

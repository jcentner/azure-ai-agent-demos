# Azure AI Agent Demos

Azure AI Foundry Agent demos — v1 archived, v2 rewrites for Agents v2 and new Foundry UI

## Conventions

- **Language**: Python
- **Checkpoint file**: `roadmap/CURRENT-STATE.md` — read this first every session
- **Vision lock**: `docs/vision/VISION-LOCK.md` — highest-authority document in the repo
- **ADRs**: Record significant decisions in `docs/architecture/decisions/`
- **Open questions**: Track uncertainty in `docs/reference/open-questions.md`
- **Tech debt**: Track compromises in `docs/reference/tech-debt.md`

## Development Workflow

This project uses an autonomous build loop. The agent reads the checkpoint, identifies the next slice of work, implements it, reviews it, commits it, and checkpoints.

**Slice protocol** — for every unit of work:
1. Implement the change
2. Run tests — do not proceed if tests fail
3. Review code (invoke reviewer subagent or self-review)
4. Fix Critical/Major findings
5. Commit with `type: description` format (feat, fix, docs, refactor, test)
6. Update `roadmap/CURRENT-STATE.md`

## Rules

- Do not modify `docs/vision/VISION-LOCK.md` without human approval
- Run tests before committing — never commit broken tests
- Update docs when code changes affect documented behavior
- Record new design decisions as ADRs
- Record compromises in the tech debt tracker
- New terms go in `docs/reference/glossary.md`

## Authority Order (highest first)

1. Vision lock (`docs/vision/VISION-LOCK.md`)
2. ADRs (`docs/architecture/decisions/`)
3. Architecture docs
4. Roadmap and planning docs
5. Open questions
6. Instructions and prompts

Lower-priority artifacts must be updated to match higher-priority ones.

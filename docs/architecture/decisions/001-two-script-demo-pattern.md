# ADR-001: Two-Script Demo Pattern

## Status

Accepted

## Context

Each demo needs a consistent, beginner-friendly structure. Users following a walkthrough need to understand when agent provisioning happens vs. interactive use. V1 demos already established a `create_agent.py` + `ask_agent.py` split pattern that proved effective.

## Decision

Every demo follows a two-script pattern:
- `create_agent.py` — Run once to provision the agent (creates definition, persists agent name to file)
- `ask_agent.py` — Interactive REPL for chatting with the agent (loads agent name from file, streams responses)

Agent reference is passed between scripts via a local `.agent_name` file (v2) or `.agent_id` file (v1).

## Consequences

- **Positive**: Clear separation of concerns; users understand the lifecycle; scripts can be run independently
- **Positive**: Consistent experience across all demos
- **Negative**: No single-command "run everything" entrypoint — users must run two scripts
- **Accepted**: This is a demo repo, not a CLI tool; explicit steps are pedagogically preferable

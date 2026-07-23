"""Phase 5 - Fix by promoting v2 to default.

One call moves default_version to v2. The consumer endpoint picks it up
immediately - no agent code change, no redeploy.

Success criterion for this lab: after promotion, code_interpreter is now part of
the agent's toolset (visible in the agent's tool list and in the consumer
tools/list). That proves the version change reached the agent.

Runtime cache gotcha: the endpoint updates instantly, but the agent runtime caches
an MCP server's tool list keyed by (server_label + server_url) with a long TTL. An
agent that already cached the old list under a server_label keeps serving the old
tool set. A fresh server_label (a new agent/session) sees the new tool right away.
Below, "compute-agent-v2" is a fresh label, so it sees Code Interpreter at once.

Preview limitation (troubleshooting sidebar): invoking Code Interpreter THROUGH a
toolbox currently returns a ServerError in preview. Native Code Interpreter
(attached directly to an agent, not via a toolbox) is unaffected. This lab's goal
is the version contract - that the promoted tool becomes available - not code
execution, so we assert the tool is present rather than run it.
"""

from common import TOOLBOX_NAME, consumer_endpoint, project, run_agent, tools_list


def main():
    toolbox = project.toolboxes.update(TOOLBOX_NAME, default_version="2")
    print("promoted. default_version =", toolbox.default_version)

    served = tools_list(consumer_endpoint())
    print("consumer tools/list (endpoint, instant):", served)
    assert "code_interpreter" in served, "consumer endpoint should now serve code_interpreter"

    tools_seen, tool_calls, answer = run_agent(
        "List the tools you can call, then use web search for one current Azure headline with a URL.",
        server_label="compute-agent-v2",  # fresh label -> no stale cache
        url=consumer_endpoint(),
    )
    print("\nfresh agent tools seen:", tools_seen, "| tool calls:", tool_calls)
    print("fresh agent said:", answer[:200])
    assert "code_interpreter" in tools_seen, "agent should now see code_interpreter in its toolset"
    print("\nPASS: code_interpreter is now available to the agent after promotion.")


if __name__ == "__main__":
    main()

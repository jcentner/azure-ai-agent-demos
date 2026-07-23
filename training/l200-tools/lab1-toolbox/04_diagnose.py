"""Phase 4 - Diagnose the break.

Symptom: an agent that could search the web suddenly cannot do compute, even
though you "added" Code Interpreter. Work from ground truth, not the model's words.

Three checks, in order:
  1. Consumer endpoint tools/list  -> what agents actually get right now.
  2. toolboxes.get().default_version -> which version the consumer serves.
  3. list_versions()               -> confirm the tool you expected lives in a
                                       version that is NOT the default.

Portal trap: the Foundry Toolkit UI shows the LATEST version, so it looks like
Code Interpreter is there. The consumer endpoint serves the DEFAULT version, which
is a different thing. Version list and promotion are SDK/REST/azd only.
"""

from common import TOOLBOX_NAME, consumer_endpoint, project, run_agent, tools_list


def main():
    print("1) consumer tools/list:", tools_list(consumer_endpoint()))

    toolbox = project.toolboxes.get(TOOLBOX_NAME)
    print("2) default_version   :", toolbox.default_version)

    print("3) all versions      :")
    for version in project.toolboxes.list_versions(TOOLBOX_NAME):
        print(f"     v{version.version}: {[t.type for t in version.tools]}")

    tools_seen, tool_calls, answer = run_agent(
        "Use the code interpreter tool to compute the 15th Fibonacci number. "
        "If you cannot, say which tool is missing.",
        server_label="compute-agent",
        url=consumer_endpoint(),
    )
    print("\nagent tools seen:", tools_seen, "| tool calls:", tool_calls)
    print("agent said:", answer[:200])


if __name__ == "__main__":
    main()

"""Connect two agents to the same knowledge base and verify shared, cited answers.

Builds two agents (hr-assistant, onboarding-assistant), each consuming the KB via the MCP tool.
Asks a multi-part question that forces the KB to decompose the query, and confirms both agents
return cited answers from the shared KB. A final off-topic question confirms grounding discipline.

See the README for the managed-identity role requirements.
"""

import common

MULTI_PART = "What is Contoso's 401k match, and how many PTO days do new employees get?"
OFF_TOPIC = "What is the capital of France?"


def _contains_both_policy_facts(answer: str) -> bool:
    text = answer.lower()
    has_match = any(value in text for value in ("4%", "4 percent", "four percent"))
    has_pto = (
        any(value in text for value in ("15", "fifteen"))
        and "pto" in text
        and "day" in text
    )
    return has_match and has_pto


def main():
    agents = [common.build_agent(name) for name in common.AGENT_NAMES]
    print("agents on the shared KB: " + ", ".join(f"{a.name} v{a.version}" for a in agents) + "\n")

    for agent in agents:
        print(f"===== {agent.name} =====")
        answer, tool_used, annotations = common.run_agent(agent, MULTI_PART)
        print(f"Q (multi-part): {MULTI_PART}")
        print(f"   tool_used={tool_used} citations={annotations}")
        print(f"   A: {answer}\n")
        assert tool_used, "expected the knowledge base MCP tool to be called"
        assert annotations > 0, "expected at least one citation"
        assert _contains_both_policy_facts(answer), (
            "expected the answer to include the 4% 401k match and 15 PTO days"
        )

    # Negative case: not in the KB -> the agent should decline, not answer from memory.
    for agent in agents:
        answer, tool_used, annotations = common.run_agent(agent, OFF_TOPIC)
        print(f"Q (off-topic, {agent.name}): {OFF_TOPIC}")
        print(f"   tool_used={tool_used} citations={annotations}")
        print(f"   A: {answer}\n")
        normalized_answer = answer.lower().replace("\u2019", "'")
        declined = "don't know" in normalized_answer or "do not know" in normalized_answer
        assert tool_used, "expected the knowledge base MCP tool to be called"
        assert declined, f"expected a decline for the off-topic question, got: {answer!r}"
        assert "paris" not in answer.lower(), (
            f"agent answered from memory instead of declining: {answer!r}"
        )

    print(
        "PASS: both agents share one KB, answer a multi-part question with citations,\n"
        "      and decline an off-topic question."
    )


if __name__ == "__main__":
    main()

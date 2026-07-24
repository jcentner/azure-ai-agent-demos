"""Phase 3 - Build the grounded agent and verify cited answers.

(Phase 2 is RBAC - see README. The agent reaches AI Search as the PROJECT managed identity, which
needs Search Index Data Reader + Search Service Contributor on the search service.)

Builds one agent with the AzureAISearch tool bound to the index, asks grounded questions, and checks
that the tool was called and the answer carries citations. A final off-topic question confirms the
agent stays grounded (answers "I don't know" instead of using model memory).
"""

import common
from common import AzureAISearchQueryType


def main():
    agent = common.build_agent("hr-benefits-agent", AzureAISearchQueryType.SEMANTIC)
    print(f"agent: {agent.name} v{agent.version} (query_type=semantic, top_k=5)\n")

    grounded = [
        "How many PTO days do new employees get?",
        "What is Contoso's 401k match?",
        "How much is the home office stipend?",
    ]
    for q in grounded:
        answer, tool_used, annotations = common.run_agent(agent, q)
        print(f"Q: {q}")
        print(f"   tool_used={tool_used} citations={annotations}")
        print(f"   A: {answer}\n")
        assert tool_used, "expected the AI Search tool to be called"
        assert annotations > 0, "expected at least one citation"

    # Negative case: not in the docs -> the agent should decline, not answer from memory.
    off_topic = "What is the capital of France?"
    answer, tool_used, annotations = common.run_agent(agent, off_topic)
    print(f"Q (off-topic): {off_topic}")
    print(f"   tool_used={tool_used} citations={annotations}")
    print(f"   A: {answer}\n")
    normalized_answer = answer.lower().replace("\u2019", "'")
    declined = "don't know" in normalized_answer or "do not know" in normalized_answer
    assert declined, f"expected a decline for the off-topic question, got: {answer!r}"
    assert "paris" not in answer.lower(), f"agent answered from memory instead of declining: {answer!r}"

    print("PASS: grounded answers are cited; off-topic question is declined.")


if __name__ == "__main__":
    main()

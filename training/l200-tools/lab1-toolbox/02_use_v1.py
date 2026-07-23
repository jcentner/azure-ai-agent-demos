"""Phase 2 - Two agents share one toolbox.

Both agents point at the same consumer endpoint. Neither declares any tool of its
own; they discover Web Search from the toolbox. This is the toolbox value prop:
configure tools once, reuse across agents.
"""

from common import consumer_endpoint, run_agent


def main():
    url = consumer_endpoint()

    for label, prompt in [
        ("news-agent", "Use web search: give one current headline about Azure, with the source URL."),
        ("research-agent", "Use web search: what did Microsoft announce most recently about Foundry? Cite a URL."),
    ]:
        tools_seen, tool_calls, answer = run_agent(prompt, server_label=label, url=url)
        print(f"\n[{label}] tools discovered: {tools_seen}")
        print(f"[{label}] tool calls: {tool_calls}")
        print(f"[{label}] {answer[:200]}")


if __name__ == "__main__":
    main()

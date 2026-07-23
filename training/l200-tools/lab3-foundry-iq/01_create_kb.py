"""Create the Foundry IQ knowledge base and project connection.

Creates:
- a knowledge source over the Lab 2 `contoso-benefits` index,
- the knowledge base (with the configured model for query planning + answer synthesis),
- the RemoteTool project connection that targets the KB's MCP endpoint.

Prerequisite: run Lab 2 first so the `contoso-benefits` index exists. See README for required roles.
"""

import common


def main():
    common.create_knowledge_source()
    print(f"knowledge source: {common.KS_NAME} (over index {common.INDEX_NAME})")

    common.create_knowledge_base()
    print(
        f"knowledge base:   {common.KB_NAME} "
        f"(model={common.MODEL_DEPLOYMENT_NAME}, answerSynthesis, effort=medium)"
    )

    common.create_kb_connection()
    print(f"project connection: {common.KB_CONNECTION_NAME} -> {common.mcp_endpoint()}")

    print("\nBuilt. Next: python 02_query.py")


if __name__ == "__main__":
    main()

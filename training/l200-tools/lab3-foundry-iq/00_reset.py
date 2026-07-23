"""Reset Lab 3 by deleting its agents, connection, knowledge base, and knowledge source.

Leaves the Lab 2 `contoso-benefits` index in place (this lab reuses it). Order matters: the KB
references the knowledge source, so delete the KB before the source.
"""

import common
import requests


def main():
    for name in common.AGENT_NAMES:
        try:
            common.project.agents.delete(name)
            print(f"deleted agent {name}")
        except Exception as exc:
            print(f"agent {name} not deleted ({str(exc)[:80]})")

    try:
        resp = requests.delete(
            f"https://management.azure.com{common.PROJECT_RESOURCE_ID}/connections/"
            f"{common.KB_CONNECTION_NAME}?api-version=2025-10-01-preview",
            headers={"Authorization": f"Bearer {common._arm_token()}"},
        )
        print(f"deleted connection {common.KB_CONNECTION_NAME} (status {resp.status_code})")
    except Exception as exc:
        print(f"connection not deleted ({str(exc)[:80]})")

    ic = common.index_client()
    try:
        ic.delete_knowledge_base(common.KB_NAME)
        print(f"deleted knowledge base {common.KB_NAME}")
    except Exception as exc:
        print(f"knowledge base not deleted ({str(exc)[:80]})")
    try:
        ic.delete_knowledge_source(common.KS_NAME)
        print(f"deleted knowledge source {common.KS_NAME}")
    except Exception as exc:
        print(f"knowledge source not deleted ({str(exc)[:80]})")


if __name__ == "__main__":
    main()

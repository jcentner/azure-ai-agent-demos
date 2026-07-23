"""Phase 0 (optional) - Reset. Delete the index and the lab agent for a clean re-run."""

import common
from azure.search.documents.indexes import SearchIndexClient


def main():
    try:
        SearchIndexClient(endpoint=common.SEARCH_ENDPOINT, credential=common._credential).delete_index(
            common.INDEX_NAME
        )
        print(f"deleted index {common.INDEX_NAME}")
    except Exception as exc:
        print(f"index not deleted ({str(exc)[:80]})")
    try:
        common.project.agents.delete("hr-benefits-agent")
        print("deleted agent hr-benefits-agent")
    except Exception as exc:
        print(f"agent not deleted ({str(exc)[:80]})")


if __name__ == "__main__":
    main()

"""Phase 1 - Create the index and load the document set.

Creates the contoso-benefits index (keyword + semantic, no vectors) on the project's AI Search
service and uploads the markdown files in data/. Re-runnable: create_or_update + upsert.
"""

import time

import common


def main():
    common.create_index()
    print(f"index ready: {common.INDEX_NAME} on {common.SEARCH_ENDPOINT}")
    n = common.upload_docs()
    print(f"uploaded {n} documents")
    time.sleep(3)  # let the index catch up before a sanity query
    hits = list(
        common._search_client().search(
            search_text="PTO days for new employees",
            top=1,
            query_type="semantic",
            semantic_configuration_name=common.SEMANTIC_CONFIG,
        )
    )
    print("sanity search top hit:", hits[0]["id"] if hits else None)


if __name__ == "__main__":
    main()

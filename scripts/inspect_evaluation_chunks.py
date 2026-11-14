
import os

from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient


load_dotenv()

CHUNK_IDS = [
    "insight-science-highlights-chunk-004",
    "insight-instruments-chunk-002",
    "insight-instruments-chunk-003",
    "lunar-module-history-chunk-002",
    "apollo-program-chunk-001",
    "lunar-module-history-chunk-005",
]


def main():
    client = SearchClient(
        endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
        index_name=os.getenv(
            "AZURE_SEARCH_INDEX_NAME",
            "space-buddies-knowledge",
        ),
        credential=AzureKeyCredential(
            os.environ["AZURE_SEARCH_API_KEY"]
        ),
    )

    print("\nSPACE BUDDIES - EVIDENCE INSPECTION")
    print("=" * 60)

    for chunk_id in CHUNK_IDS:
        print(f"\nCHUNK: {chunk_id}")

        try:
            chunk = client.get_document(
                key=chunk_id,
                selected_fields=[
                    "chunk_id",
                    "explorer_id",
                    "topic",
                    "content",
                    "source_title",
                    "source_url",
                ],
            )

            print(f"Explorer: {chunk['explorer_id']}")
            print(f"Topic: {chunk['topic']}")
            print(f"Source: {chunk['source_title']}")
            print(f"URL: {chunk['source_url']}")
            print(f"\nCONTENT:\n{chunk['content']}")

        except Exception as exc:
            print(
                f"ERROR retrieving {chunk_id}: "
                f"{type(exc).__name__}: {exc}"
            )

        print("-" * 60)


if __name__ == "__main__":
    main()

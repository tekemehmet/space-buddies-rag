
import os

from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
)

load_dotenv()

INDEX_NAME = os.getenv(
    "AZURE_SEARCH_INDEX_NAME",
    "space-buddies-knowledge",
)

EMBEDDING_DIMENSIONS = 1536


def main():
    endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
    api_key = os.environ["AZURE_SEARCH_API_KEY"]

    client = SearchIndexClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(api_key),
    )

    fields = [
        SimpleField(
            name="chunk_id",
            type=SearchFieldDataType.String,
            key=True,
            filterable=True,
        ),
        SimpleField(
            name="explorer_id",
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True,
        ),
        SearchableField(
            name="content",
            type=SearchFieldDataType.String,
        ),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(
                SearchFieldDataType.Single
            ),
            searchable=True,
            vector_search_dimensions=EMBEDDING_DIMENSIONS,
            vector_search_profile_name="vector-profile",
        ),
        SimpleField(
            name="topic",
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True,
        ),
        SearchableField(
            name="source_title",
            type=SearchFieldDataType.String,
        ),
        SimpleField(
            name="source_url",
            type=SearchFieldDataType.String,
        ),
    ]

    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="hnsw-config"
            ),
        ],
        profiles=[
            VectorSearchProfile(
                name="vector-profile",
                algorithm_configuration_name="hnsw-config",
            ),
        ],
    )

    index = SearchIndex(
        name=INDEX_NAME,
        fields=fields,
        vector_search=vector_search,
    )

    result = client.create_or_update_index(index)

    print("\nSPACE BUDDIES - AZURE AI SEARCH")
    print("=" * 45)
    print(f"Index created: {result.name}")
    print(f"Embedding dimensions: {EMBEDDING_DIMENSIONS}")
    print(f"Fields: {len(fields)}")
    print("\nPASS: Search index is ready.")


if __name__ == "__main__":
    main()

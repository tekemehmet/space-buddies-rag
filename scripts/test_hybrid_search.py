
import os
import re

from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery


load_dotenv()

INDEX_NAME = os.getenv(
    "AZURE_SEARCH_INDEX_NAME",
    "space-buddies-knowledge",
)


def rerank_results(question, results):
    question_lower = question.lower()

    # Small, explicit domain vocabulary.
    # This is a heuristic, not a semantic reranker.
    concepts = {
        "stop flying": [
            "rotor",
            "damage",
            "final flight",
            "unable to fly",
            "mission ends",
        ],
        "water": [
            "water",
            "hematite",
            "carbonate",
            "silica",
        ],
        "wheels": [
            "wheel",
            "wire mesh",
            "electric motor",
        ],
    }

    active_terms = []

    for phrase, terms in concepts.items():
        if phrase in question_lower:
            active_terms.extend(terms)

    # Also recognize alternative wording.
    if (
        "flying" in question_lower
        and any(
            word in question_lower
            for word in ("stop", "stopped", "end", "ended", "why")
        )
    ):
        active_terms.extend(concepts["stop flying"])

    def score(result):
        content = result["content"].lower()

        keyword_score = sum(
            1
            for term in set(active_terms)
            if re.search(r"\b" + re.escape(term) + r"\b", content)
        )

        return (
            keyword_score,
            result.get("@search.score", 0),
        )

    return sorted(results, key=score, reverse=True)


def main():
    openai_client = AzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version="2024-02-01",
    )

    search_client = SearchClient(
        endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(
            os.environ["AZURE_SEARCH_API_KEY"]
        ),
    )

    question = "Why did you stop flying on Mars?"
    explorer_id = "ingenuity"

    embedding = openai_client.embeddings.create(
        model=os.environ[
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
        ],
        input=question,
    ).data[0].embedding

    results = list(
        search_client.search(
            search_text=question,
            vector_queries=[
                VectorizedQuery(
                    vector=embedding,
                    k_nearest_neighbors=30,
                    fields="content_vector",
                )
            ],
            filter=f"explorer_id eq '{explorer_id}'",
            select=[
                "chunk_id",
                "explorer_id",
                "topic",
                "content",
                "source_title",
                "source_url",
            ],
            top=30,
        )
    )

    ranked = rerank_results(question, results)

    print("\nSPACE BUDDIES - RERANKING TEST")
    print("=" * 55)

    for index, result in enumerate(ranked[:5], start=1):
        print(f"\nRESULT {index}")
        print(f"Chunk: {result['chunk_id']}")
        print(f"Topic: {result['topic']}")
        print(f"Azure score: {result.get('@search.score')}")
        print(f"Source: {result['source_title']}")
        print(f"Content: {result['content'][:350]}")

    target = "ingenuity-final-flight-chunk-001"

    if ranked and ranked[0]["chunk_id"] == target:
        print("\nPASS: Final-flight evidence ranked first.")
    else:
        print("\nREVIEW: Final-flight evidence not ranked first.")


if __name__ == "__main__":
    main()


import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery


load_dotenv()

DATASET_PATH = Path("data/evaluation/questions.json")
INDEX_NAME = os.getenv(
    "AZURE_SEARCH_INDEX_NAME",
    "space-buddies-knowledge",
)


def rerank_results(question, results):
    question_lower = question.lower()

    concepts = {
        "stop flying": [
            "rotor", "damage", "final flight",
            "unable to fly", "mission ends",
        ],
        "water": [
            "water", "hematite", "carbonate", "silica",
        ],
        "wheels": [
            "wheel", "wire mesh", "electric motor",
        ],
    }

    active_terms = []

    for phrase, terms in concepts.items():
        if phrase in question_lower:
            active_terms.extend(terms)

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
            if re.search(
                r"\b" + re.escape(term) + r"\b",
                content,
            )
        )

        return (
            keyword_score,
            result.get("@search.score", 0),
        )

    return sorted(results, key=score, reverse=True)


def is_useful_chunk(chunk):
    content = chunk["content"].lower()

    navigation_phrases = [
        "more opportunity and mars resources",
        "eyes on the solar system",
        "use this online application",
        "immersive apps for mac",
    ]

    if any(phrase in content for phrase in navigation_phrases):
        return False

    return len(content.split()) >= 40


def main():
    questions = json.loads(
        DATASET_PATH.read_text(encoding="utf-8")
    )

    openai_client = AzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version="2024-10-21",
    )

    search_client = SearchClient(
        endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(
            os.environ["AZURE_SEARCH_API_KEY"]
        ),
    )

    labeled_count = 0
    recall_hits = 0
    reciprocal_rank_total = 0.0
    isolation_passes = 0

    print("\nSPACE BUDDIES - RETRIEVAL EVALUATION")
    print("=" * 60)

    for index, item in enumerate(questions, start=1):
        explorer_id = item["explorer_id"]
        question = item["question"]
        expected = item["expected_chunk_id"]

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
                    "content",
                    "topic",
                    "source_title",
                ],
                top=30,
            )
        )

        filtered = [
            chunk for chunk in results
            if is_useful_chunk(chunk)
        ]

        ranked = rerank_results(question, filtered)
        top_three = ranked[:3]

        isolation_ok = all(
            chunk["explorer_id"] == explorer_id
            for chunk in top_three
        )

        if isolation_ok and top_three:
            isolation_passes += 1

        retrieved_ids = [
            chunk["chunk_id"] for chunk in top_three
        ]

        print(f"\nTEST {index}: {explorer_id}")
        print(f"Question: {question}")

        for rank, chunk in enumerate(top_three, start=1):
            print(
                f"  {rank}. {chunk['chunk_id']} "
                f"({chunk['topic']})"
            )

        if expected is None:
            print("  STATUS: UNLABELED - manual review needed")
            continue

        labeled_count += 1

        if expected in retrieved_ids:
            rank = retrieved_ids.index(expected) + 1
            recall_hits += 1
            reciprocal_rank_total += 1.0 / rank
            print(f"  STATUS: PASS - expected chunk at rank {rank}")
        else:
            print(f"  STATUS: FAIL - expected {expected}")

    recall_at_3 = (
        recall_hits / labeled_count
        if labeled_count else 0.0
    )

    mrr_at_3 = (
        reciprocal_rank_total / labeled_count
        if labeled_count else 0.0
    )

    print("\nEVALUATION SUMMARY")
    print("=" * 60)
    print(f"Total questions: {len(questions)}")
    print(f"Labeled questions: {labeled_count}")
    print(f"Recall@3: {recall_at_3:.1%}")
    print(f"MRR@3: {mrr_at_3:.3f}")
    print(
        f"Explorer isolation: "
        f"{isolation_passes}/{len(questions)}"
    )


if __name__ == "__main__":
    main()

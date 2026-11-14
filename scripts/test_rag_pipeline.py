
import os
import re

from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from test_speech import generate_audio
import argparse
from explorer_config import get_explorer


load_dotenv()

INDEX_NAME = os.getenv(
    "AZURE_SEARCH_INDEX_NAME",
    "space-buddies-knowledge",
)


def rerank_results(question, results):
    question_lower = question.lower()

    concepts = {
        "stop flying": [
            "rotor",
            "damage",
            "final flight",
            "unable to fly",
            "mission ends",
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


def main():
    parser = argparse.ArgumentParser(
    description="Test Space Buddies RAG with any NASA explorer."
    )

    parser.add_argument(
        "--explorer",
        default="ingenuity",
        help="Explorer ID from explorer_config.py",
    )

    parser.add_argument(
        "--question",
        default="Why did you stop flying on Mars?",
        help="Student's question",
    )

    args = parser.parse_args()

    explorer_id = args.explorer
    question = args.question
    explorer = get_explorer(explorer_id)

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

    embedding_response = openai_client.embeddings.create(
        model=os.environ[
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
        ],
        input=question,
    )

    question_vector = embedding_response.data[0].embedding

    results = list(
        search_client.search(
            search_text=question,
            vector_queries=[
                VectorizedQuery(
                    vector=question_vector,
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
                "source_url",
            ],
            top=30,
        )
    )

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


    filtered_results = [
        chunk for chunk in results
        if is_useful_chunk(chunk)
    ]

    ranked = rerank_results(question, filtered_results)
    selected = ranked[:3]

    if not selected:
        raise RuntimeError("No NASA evidence found.")

    context_parts = []

    for index, chunk in enumerate(selected, start=1):
        context_parts.append(
            f"[{index}] {chunk['content']}\n"
            f"Source: {chunk['source_title']}\n"
            f"URL: {chunk['source_url']}"
        )

    context = "\n\n".join(context_parts)

    print("\nFULL NASA EVIDENCE")
    print("=" * 55)

    for index, chunk in enumerate(selected, start=1):
        print(f"\nSOURCE [{index}]")
        print(f"Chunk ID: {chunk['chunk_id']}")
        print(f"Title: {chunk['source_title']}")
        print(f"Content:\n{chunk['content']}")
        print("-" * 55)

    system_prompt = (
        f"You are {explorer['name']}, "
        f"{explorer['description']}, "
        "speaking to a middle school student. "
        "Answer in first person using simple, friendly, "
        "engaging English. "
        "Use ONLY the NASA evidence provided. "
        "Do not invent facts, dates, discoveries, "
        "feelings, or experiences. "
        "If the evidence does not answer the question, "
        "say you do not have enough information. "
        "Keep the answer to approximately 3-5 sentences. "
        "Include citation markers like [1] or [2] "
        "for factual claims. "
        "Do not include raw URLs in the answer."
    )

    user_prompt = (
        f"NASA EVIDENCE:\n{context}\n\n"
        f"STUDENT QUESTION:\n{question}"
    )

    response = openai_client.chat.completions.create(
        model=os.environ[
            "AZURE_OPENAI_CHAT_DEPLOYMENT"
        ],
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=350,
    )

    answer = response.choices[0].message.content

    if not answer:
        raise RuntimeError("Chat model returned no answer.")

    print("\nSPACE BUDDIES - RAG PIPELINE TEST")
    print("=" * 55)

    print(f"Explorer: {explorer_id}")
    print(f"Question: {question}")

    print("\nRETRIEVED EVIDENCE")
    for index, chunk in enumerate(selected, start=1):
        print(
            f"[{index}] {chunk['chunk_id']} "
            f"({chunk['topic']})"
        )

    print("\nAI ANSWER")
    print(answer)

    print("\nGENERATING AUDIO...")

    audio_path = generate_audio(
        text=answer,
        output_file=f"output/{explorer_id}_rag_answer.mp3",
        voice=explorer["voice"],
    )

    print(f"Audio saved: {audio_path.resolve()}")

    print("\nNASA SOURCES")
    for index, chunk in enumerate(selected, start=1):
        print(
            f"[{index}] {chunk['source_title']}\n"
            f"    {chunk['source_url']}"
        )


if __name__ == "__main__":
    main()

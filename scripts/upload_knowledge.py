
import json
import os
import time
from pathlib import Path

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from dotenv import load_dotenv
from openai import AzureOpenAI


load_dotenv()

INPUT_FILE = Path("data/processed/chunks.jsonl")
BATCH_SIZE = 10
EMBEDDING_DIMENSIONS = 1536

INDEX_NAME = os.getenv(
    "AZURE_SEARCH_INDEX_NAME",
    "space-buddies-knowledge",
)


def load_chunks():
    chunks = []

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            chunk = json.loads(line)

            if chunk.get("indexable", True):
                chunks.append(chunk)

    return chunks


def create_clients():
    openai_client = AzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version="2024-02-01",
        max_retries=5,
    )

    search_client = SearchClient(
        endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(
            os.environ["AZURE_SEARCH_API_KEY"]
        ),
    )

    return openai_client, search_client


def main():
    chunks = load_chunks()
    openai_client, search_client = create_clients()

    print("\nSPACE BUDDIES - KNOWLEDGE UPLOAD")
    print("=" * 50)
    print(f"Chunks to upload: {len(chunks)}")
    print(f"Target index: {INDEX_NAME}")

    uploaded = 0

    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start:start + BATCH_SIZE]

        texts = [chunk["content"] for chunk in batch]

        response = openai_client.embeddings.create(
            model=os.environ[
                "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
            ],
            input=texts,
        )

        vectors = {
            item.index: item.embedding
            for item in response.data
        }

        documents = []

        for index, chunk in enumerate(batch):
            vector = vectors[index]

            if len(vector) != EMBEDDING_DIMENSIONS:
                raise ValueError(
                    f"Invalid embedding dimensions "
                    f"for {chunk['chunk_id']}"
                )

            documents.append({
                "chunk_id": chunk["chunk_id"],
                "explorer_id": chunk["explorer_id"],
                "content": chunk["content"],
                "content_vector": vector,
                "topic": chunk["topic"],
                "source_title": chunk["source_title"],
                "source_url": chunk["source_url"],
            })

        pending = documents

        for attempt in range(1, 6):
            results = search_client.upload_documents(
                documents=pending
            )

            failed_ids = {
                result.key
                for result in results
                if not result.succeeded
            }

            uploaded += len(pending) - len(failed_ids)

            if not failed_ids:
                break

            pending = [
                document
                for document in pending
                if document["chunk_id"] in failed_ids
            ]

            if attempt == 5:
                raise RuntimeError(
                    f"Failed to upload: {sorted(failed_ids)}"
                )

            time.sleep(min(2 ** attempt, 16))

        print(
            f"Uploaded {uploaded}/{len(chunks)} chunks"
        )

        time.sleep(0.5)

    print("\nWaiting for index updates...")

    indexed_count = 0

    for _ in range(12):
        indexed_count = search_client.get_document_count()

        if indexed_count == len(chunks):
            break

        time.sleep(5)

    print("\nUPLOAD SUMMARY")
    print("=" * 50)
    print(f"Uploaded: {uploaded}")
    print(f"Indexed documents: {indexed_count}")

    if indexed_count == len(chunks):
        print("\nPASS: All knowledge chunks indexed.")
    else:
        print(
            "\nWARNING: Document count differs from "
            "the local chunk count. Check for existing "
            "documents or indexing delays."
        )


if __name__ == "__main__":
    main()

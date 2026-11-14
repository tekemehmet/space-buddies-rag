
import os

from dotenv import load_dotenv
from openai import AzureOpenAI


load_dotenv()

EMBEDDING_DIMENSIONS = 1536


def main():
    client = AzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version="2024-02-01",
    )

    question = "Why did Ingenuity stop flying on Mars?"

    response = client.embeddings.create(
        model=os.environ[
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
        ],
        input=question,
    )

    vector = response.data[0].embedding

    print("\nSPACE BUDDIES - EMBEDDING TEST")
    print("=" * 45)

    print(f"Question: {question}")
    print(f"Embedding dimensions: {len(vector)}")
    print(f"First 5 values: {vector[:5]}")

    if len(vector) != EMBEDDING_DIMENSIONS:
        raise ValueError(
            f"Expected {EMBEDDING_DIMENSIONS} dimensions, "
            f"received {len(vector)}"
        )

    print("\nPASS: Embedding generated successfully.")


if __name__ == "__main__":
    main()

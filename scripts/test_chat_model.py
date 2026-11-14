
import os

from dotenv import load_dotenv
from openai import AzureOpenAI


load_dotenv()


def main():
    client = AzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version="2024-10-21",
    )

    deployment = os.environ[
        "AZURE_OPENAI_CHAT_DEPLOYMENT"
    ]

    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a friendly educational assistant "
                    "for the Space Buddies NASA project. "
                    "Explain space science in simple English "
                    "suitable for middle school students. "
                    "Keep answers concise and engaging."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Explain what a Mars rover is "
                    "in two sentences."
                ),
            },
        ],
        temperature=0.4,
        max_tokens=150,
    )

    answer = response.choices[0].message.content

    if not answer:
        raise RuntimeError("The chat model returned no text.")

    print("\nSPACE BUDDIES - CHAT MODEL TEST")
    print("=" * 50)
    print(f"Deployment: {deployment}")
    print(f"\nAnswer:\n{answer}")
    print("\nPASS: Chat model responded successfully.")


if __name__ == "__main__":
    main()

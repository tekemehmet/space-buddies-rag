import json
from pathlib import Path


INPUT_FILE = Path("data/processed/chunks.jsonl")


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        for line in file:
            chunk = json.loads(line)

            chunk_id = chunk.get("chunk_id", "unknown")
            topic = chunk.get("topic", "unknown")
            content = chunk.get("content", "")

            word_count = len(content.split())
            preview = content[:200].replace("\n", " ")

            print(f"ID: {chunk_id}")
            print(f"Topic: {topic}")
            print(f"Words: {word_count}")
            print(f"Preview: {preview}")
            print("-" * 80)


if __name__ == "__main__":
    main()
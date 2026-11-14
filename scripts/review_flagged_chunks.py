
import json
from pathlib import Path

INPUT_FILE = Path("data/processed/chunks.jsonl")
OUTPUT_FILE = Path("data/processed/flagged_chunks.txt")

flagged = []

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    for line in file:
        chunk = json.loads(line)

        if not chunk.get("indexable", True):
            flagged.append(chunk)

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    for chunk in flagged:
        file.write("=" * 80 + "\n")
        file.write(f"CHUNK: {chunk['chunk_id']}\n")
        file.write(f"EXPLORER: {chunk['explorer_id']}\n")
        file.write(f"REASON: {chunk['review_reason']}\n")
        file.write(f"SOURCE: {chunk['source_title']}\n")
        file.write(f"URL: {chunk['source_url']}\n")
        file.write("-" * 80 + "\n")
        file.write(chunk["content"] + "\n\n")

print(f"Exported {len(flagged)} flagged chunks to {OUTPUT_FILE}")

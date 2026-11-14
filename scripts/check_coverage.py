
import json
from collections import Counter, defaultdict
from pathlib import Path

INPUT_FILE = Path("data/processed/chunks.jsonl")

counts = Counter()
topics = defaultdict(Counter)

with INPUT_FILE.open("r", encoding="utf-8") as file:
    for line in file:
        chunk = json.loads(line)

        if not chunk.get("indexable", True):
            continue

        explorer = chunk["explorer_id"]
        topic = chunk["topic"]

        counts[explorer] += 1
        topics[explorer][topic] += 1

print("\nSPACE BUDDIES - KNOWLEDGE COVERAGE")
print("=" * 50)

for explorer in sorted(counts):
    print(f"\n{explorer.upper()}")
    print(f"Total chunks: {counts[explorer]}")

    for topic, count in topics[explorer].most_common():
        print(f"  {topic}: {count}")

print("\nTOTAL INDEXABLE CHUNKS:", sum(counts.values()))


import json
from pathlib import Path
from urllib.parse import urlparse
from collections import defaultdict

INPUT_FILE = Path("data/processed/chunks.jsonl")

sources = defaultdict(list)

with INPUT_FILE.open("r", encoding="utf-8") as file:
    for line in file:
        chunk = json.loads(line)

        if not chunk.get("indexable", True):
            continue

        url = chunk.get("source_url", "")
        sources[url].append(chunk)

print("\nSPACE BUDDIES - SOURCE AUDIT")
print("=" * 60)

for url, chunks in sorted(sources.items()):
    parsed = urlparse(url)

    valid_format = (
        parsed.scheme == "https"
        and parsed.netloc.endswith("nasa.gov")
    )

    status = "OK" if valid_format else "REVIEW"

    explorers = sorted({
        chunk["explorer_id"]
        for chunk in chunks
    })

    print(f"\n[{status}] {url}")
    print(f"  Explorers: {', '.join(explorers)}")
    print(f"  Chunks: {len(chunks)}")
    print(f"  Source: {chunks[0]['source_title']}")

print("\nTotal unique source URLs:", len(sources))

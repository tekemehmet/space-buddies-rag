
import json
from collections import Counter
from pathlib import Path

INPUT_FILE = Path("data/processed/chunks.jsonl")

REQUIRED_FIELDS = [
    "chunk_id",
    "explorer_id",
    "content",
    "source_title",
    "source_url",
    "topic",
]

EXPECTED_EXPLORERS = {
    "opportunity",
    "spirit",
    "insight",
    "ingenuity",
    "lunar-module",
    "lunar-rover",
}


def main():
    errors = []
    counts = Counter()
    seen_ids = set()
    total = 0

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            chunk = json.loads(line)

            if not chunk.get("indexable", True):
                continue

            total += 1

            for field in REQUIRED_FIELDS:
                if not chunk.get(field):
                    errors.append(
                        f"Line {line_number}: Missing {field}"
                    )

            chunk_id = chunk.get("chunk_id")

            if chunk_id in seen_ids:
                errors.append(
                    f"Line {line_number}: Duplicate chunk_id"
                )

            seen_ids.add(chunk_id)

            explorer = chunk.get("explorer_id")

            if explorer not in EXPECTED_EXPLORERS:
                errors.append(
                    f"Line {line_number}: Unknown explorer {explorer}"
                )

            counts[explorer] += 1

            content = chunk.get("content", "")
            if not isinstance(content, str):
                errors.append(
                    f"Line {line_number}: Content must be text"
                )
            elif len(content.split()) < 40:
                errors.append(
                    f"Line {line_number}: Chunk has fewer than 40 words"
                )

    print("\nSPACE BUDDIES - CHUNK VALIDATION")
    print("=" * 50)

    for explorer in sorted(EXPECTED_EXPLORERS):
        print(f"{explorer}: {counts[explorer]} chunks")

        if counts[explorer] == 0:
            errors.append(f"No chunks for {explorer}")

    print(f"\nTotal indexable chunks: {total}")
    print(f"Validation errors: {len(errors)}")

    if errors:
        print("\nERROR DETAILS:")
        for error in errors:
            print(f"  - {error}")
        raise SystemExit(1)

    print("\nPASS: All chunks have valid required metadata.")


if __name__ == "__main__":
    main()

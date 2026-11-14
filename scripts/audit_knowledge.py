
import json
import re
from pathlib import Path

INPUT_FILE = Path("data/processed/chunks.jsonl")

REQUIRED_FACTS = {
    "opportunity": {
        "Hematite blueberries": [
            "blueberries", "hematite", "spherules"
        ],
        "Ancient water": [
            "ancient water", "liquid water",
            "evidence of water"
        ],
        "Endeavour Crater": [
            "endeavour crater"
        ],
        "Mission-ending dust storm": [
            "dust storm"
        ],
    },
    "spirit": {
        "Silica discovery": ["silica"],
        "Home Plate": ["home plate"],
        "Comanche carbonates": [
            "comanche", "carbonates"
        ],
        "Stuck in sand": [
            "stuck", "embedded", "soft soil"
        ],
    },
    "insight": {
        "Marsquakes": ["marsquake", "seismic"],
        "SEIS": ["seis", "seismometer"],
        "HP3": ["hp3", "hp^3", "heat probe"],
        "RISE": [
            "rise", "rotation and interior structure"
        ],
    },
    "ingenuity": {
        "First flight": ["first flight", "first powered flight"],
        "72 flights": ["72 flights", "72nd flight"],
        "Rotor damage": [
            "rotor damage", "damaged rotor", "rotor blade"
        ],
        "Autonomous navigation": [
            "autonomous", "navigation"
        ],
    },
    "lunar-module": {
        "Descent stage": ["descent stage"],
        "Ascent stage": ["ascent stage"],
        "Apollo 11": ["apollo 11"],
        "Astronaut crew": ["astronaut", "crew"],
    },
    "lunar-rover": {
        "Deployment": ["deployment", "deployed", "unfolded"],
        "Wire mesh wheels": [
            "wire mesh", "wire-mesh"
        ],
        "Electric motors": ["electric motor"],
        "Navigation system": [
            "navigation system", "directional gyro"
        ],
    },
}


def contains_term(text, term):
    return re.search(
        r"(?<!\w)" + re.escape(term) + r"(?!\w)",
        text,
        re.IGNORECASE,
    ) is not None


def main():
    chunks = []

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            chunk = json.loads(line)
            if chunk.get("indexable", True):
                chunks.append(chunk)

    print("\nSPACE BUDDIES - KNOWLEDGE AUDIT")
    print("=" * 55)

    for explorer, facts in REQUIRED_FACTS.items():
        explorer_chunks = [
            chunk for chunk in chunks
            if chunk["explorer_id"] == explorer
        ]

        print(f"\n{explorer.upper()}")

        for fact, keywords in facts.items():
            matches = [
                chunk for chunk in explorer_chunks
                if any(
                    contains_term(chunk["content"], keyword)
                    for keyword in keywords
                )
            ]

            status = "FOUND" if matches else "MISSING"

            print(
                f"  {status:7} | {fact:30} "
                f"| {len(matches)} chunks"
            )

            if matches:
                print(
                    f"          Example: {matches[0]['chunk_id']}"
                )


if __name__ == "__main__":
    main()

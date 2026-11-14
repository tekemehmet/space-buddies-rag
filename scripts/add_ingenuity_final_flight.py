
import json
from datetime import datetime, timezone
from pathlib import Path


OUTPUT_FILE = Path("data/raw/ingenuity-final-flight.json")

document = {
    "document_id": "ingenuity-final-flight",
    "explorer_id": "ingenuity",
    "explorer_name": "Ingenuity",
    "mission_family": "Mars 2020",
    "body": "Mars",
    "equipment_type": "helicopter",
    "topic": "final_flight",
    "source_agency": "NASA",
    "source_title": (
        "NASA's Ingenuity Mars Helicopter Ends Mission"
    ),
    "source_url": (
        "https://www.nasa.gov/news-release/"
        "after-three-years-on-mars-nasas-ingenuity-"
        "helicopter-mission-ends/"
    ),
    "retrieved_at": datetime.now(
        timezone.utc
    ).isoformat(),
    "content": (
        "NASA's Ingenuity Mars Helicopter completed "
        "its final flight on January 18, 2024. "
        "This was Ingenuity's 72nd flight on Mars. "
        "During the final flight, Ingenuity climbed "
        "to approximately 40 feet (12 meters) "
        "above the Martian surface. "
        "After landing, images showed damage to "
        "one or more of its rotor blades. "
        "The rotor damage made Ingenuity unable "
        "to fly again, ending its flight mission. "
        "Ingenuity was originally designed to "
        "perform only five experimental flights "
        "over approximately 30 days. "
        "Instead, it completed 72 flights over "
        "nearly three years, demonstrating that "
        "powered, controlled flight was possible "
        "in the thin atmosphere of Mars. "
        "The helicopter's achievements helped "
        "pave the way for future aerial exploration "
        "of other worlds."
    ),
}

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

with OUTPUT_FILE.open(
    "w",
    encoding="utf-8",
) as file:
    json.dump(
        document,
        file,
        indent=2,
        ensure_ascii=False,
    )

print(f"Created: {OUTPUT_FILE}")

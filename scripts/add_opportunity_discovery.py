
import json
from datetime import datetime, timezone
from pathlib import Path


OUTPUT_FILE = Path(
    "data/raw/opportunity-blueberries.json"
)

document = {
    "document_id": "opportunity-blueberries",
    "explorer_id": "opportunity",
    "explorer_name": "Opportunity",
    "mission_family": "Mars Exploration Rover",
    "body": "Mars",
    "equipment_type": "rover",
    "topic": "blueberries",
    "source_agency": "NASA",
    "source_title": (
        "Mars Exploration Rovers - Science Highlights"
    ),
    "source_url": (
        "https://science.nasa.gov/mission/"
        "mars-exploration-rovers-spirit-and-opportunity/"
        "science-highlights/"
    ),
    "retrieved_at": datetime.now(
        timezone.utc
    ).isoformat(),
    "content": (
        "NASA's Opportunity rover discovered small, "
        "spherical mineral deposits nicknamed "
        "'blueberries' near its landing site on Mars. "
        "These spherules contained hematite, a mineral "
        "that commonly forms in the presence of water. "
        "Opportunity investigated these hematite-rich "
        "concretions during its early mission in 2004. "
        "The discovery provided important evidence "
        "that liquid water had affected the Martian "
        "environment in the distant past. "
        "The rover studied these features near "
        "Fram Crater using its microscopic imager "
        "and panoramic camera."
    ),
}

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

with OUTPUT_FILE.open(
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        document,
        file,
        indent=2,
        ensure_ascii=False
    )

print(f"Created: {OUTPUT_FILE}")

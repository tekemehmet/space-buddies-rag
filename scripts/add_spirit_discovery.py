
import json
from datetime import datetime, timezone
from pathlib import Path


OUTPUT_FILE = Path(
    "data/raw/spirit-comanche.json"
)

document = {
    "document_id": "spirit-comanche",
    "explorer_id": "spirit",
    "explorer_name": "Spirit",
    "mission_family": "Mars Exploration Rover",
    "body": "Mars",
    "equipment_type": "rover",
    "topic": "water_discovery",
    "source_agency": "NASA",
    "source_title": "Carbonate-Containing Martian Rocks",
    "source_url": (
        "https://science.nasa.gov/resource/"
        "carbonate-containing-martian-rocks/"
    ),
    "retrieved_at": datetime.now(
        timezone.utc
    ).isoformat(),
    "content": (
        "NASA's Spirit rover investigated a Martian rock "
        "outcrop called Comanche in December 2005. "
        "Scientists later discovered that the rocks "
        "contained unusually high concentrations of "
        "magnesium and iron carbonates. "
        "These carbonate minerals provided evidence "
        "that liquid water once existed in a relatively "
        "neutral, non-acidic environment on Mars. "
        "Such conditions could have been more favorable "
        "for microbial life than the strongly acidic "
        "environments identified elsewhere on Mars. "
        "Spirit used several scientific instruments "
        "to study Comanche, including its Mossbauer "
        "spectrometer, miniature thermal emission "
        "spectrometer, and alpha particle X-ray "
        "spectrometer. "
        "Scientists reported the carbonate findings "
        "in 2010."
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

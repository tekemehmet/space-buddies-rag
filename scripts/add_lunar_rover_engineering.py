
import json
from datetime import datetime, timezone
from pathlib import Path


OUTPUT_FILE = Path("data/raw/lunar-rover-engineering.json")

document = {
    "document_id": "lunar-rover-engineering",
    "explorer_id": "lunar-rover",
    "explorer_name": "Lunar Roving Vehicle",
    "mission_family": "Apollo",
    "body": "Moon",
    "equipment_type": "rover",
    "topic": "engineering",
    "source_agency": "NASA",
    "source_title": "The Apollo Lunar Roving Vehicle",
    "source_url": (
    "https://nssdc.gsfc.nasa.gov/"
    "planetary/lunar/apollo_lrv.html"
    ),
    "retrieved_at": datetime.now(
        timezone.utc
    ).isoformat(),
    "content": (
        "The Apollo Lunar Roving Vehicle was an "
        "electric-powered vehicle designed to "
        "transport astronauts across the Moon. "
        "It used four wheels with wire-mesh tires "
        "instead of conventional rubber tires. "
        "The wheels were constructed with woven "
        "metal wire to provide traction on loose "
        "lunar soil while keeping the vehicle "
        "lightweight. "
        "Each wheel had its own electric motor, "
        "allowing the rover to drive across "
        "the lunar surface. "
        "The electric motors were powered by "
        "onboard batteries. "
        "The Lunar Roving Vehicle was used during "
        "Apollo 15, Apollo 16, and Apollo 17. "
        "Its design allowed astronauts to travel "
        "farther from their lunar modules and "
        "explore more of the Moon than they "
        "could have reached on foot."
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


import json
import re
from pathlib import Path
from collections import Counter


INPUT_DIR = Path("data/raw")
OUTPUT_FILE = Path("data/processed/chunks.jsonl")

MAX_WORDS = 180
MIN_WORDS = 40


# Shared NASA pages contain information about both
# Spirit and Opportunity. Keep them excluded until
# we implement section-level extraction.
EXCLUDED_FILES = {
    "opportunity-mer-overview.json",
    "opportunity-science-highlights.json",
    "opportunity-science-objectives.json",
    "spirit-mer-overview.json",
    "spirit-science-highlights.json",
    "spirit-science-objectives.json",
}


# Topics available to all explorers.
COMMON_TOPICS = {
    "mission_goal": [
        "mission objective",
        "mission objectives",
        "mission goal",
        "primary objective",
        "mission was designed to",
        "mission was intended to",
    ],
    "launch": [
        "launch date",
        "launched aboard",
        "launched from",
        "launch vehicle",
        "liftoff",
    ],
    "landing": [
        "landing site",
        "landed on",
        "touchdown",
        "landing sequence",
        "landing system",
    ],
    "instruments": [
        "scientific instruments",
        "science instruments",
        "instrument suite",
        "spectrometer",
        "microscopic imager",
    ],
    "mission_end": [
        "mission ended",
        "end of mission",
        "last communication",
        "last contact",
        "mission concluded",
        "ceased operations",
    ],
    "legacy": [
        "mission legacy",
        "scientific legacy",
        "lasting legacy",
        "historic achievement",
        "world record",
    ],
}


# Explorer-specific topics.
EXPLORER_TOPICS = {
    "opportunity": {
        "water_discovery": [
            "evidence of water",
            "liquid water",
            "ancient water",
            "groundwater",
            "sedimentary rock",
            "sedimentary rocks",
            "aqueous",
            "wet environment",
        ],
        "blueberries": [
            "blueberries",
            "hematite",
            "spherules",
            "concretions",
        ],
        "journey": [
            "distance traveled",
            "distance driven",
            "kilometers traveled",
            "miles traveled",
            "endurance crater",
            "victoria crater",
            "endeavour crater",
            "perseverance valley",
            "traverse",
            "odometry",
        ],
        "dust_storm": [
            "global dust storm",
            "planet-wide dust storm",
            "mars-wide dust storm",
            "dust storm",
            "atmospheric opacity",
        ],
    },

    "spirit": {
        "water_discovery": [
            "evidence of water",
            "ancient water",
            "liquid water",
            "wet environment",
            "carbonates",
            "comanche",
        ],
        "silica": [
            "silica",
            "silica-rich",
            "hot springs",
            "hydrothermal",
            "steam vents",
        ],
        "home_plate": [
            "home plate",
            "volcanic deposits",
            "volcanic activity",
            "explosive volcanism",
        ],
        "wheel_damage": [
            "broken wheel",
            "damaged wheel",
            "right front wheel",
            "wheel failure",
            "dragging a wheel",
        ],
        "stuck": [
            "stuck in sand",
            "embedded in soil",
            "soft soil",
            "free spirit",
            "became stuck",
            "trapped in sand",
        ],
        "dust_devils": [
            "dust devils",
            "dust devil",
            "wind cleaning",
            "cleaning event",
        ],
        "journey": [
            "columbia hills",
            "husband hill",
            "gusev crater",
            "distance traveled",
            "distance driven",
            "traverse",
        ],
    },

    "insight": {
        "marsquakes": [
            "marsquake",
            "marsquakes",
            "seismic activity",
            "seismic waves",
            "seismic event",
            "seismic events",
        ],
        "seis": [
            "seismic experiment for interior structure",
            "seismometer",
            "seismic sensor",
            "seis instrument",
        ],
        "hp3": [
            "heat flow and physical properties",
            "hp3",
            "hp^3",
            "the mole",
            "heat probe",
            "heat flow probe",
        ],
        "rise": [
            "rotation and interior structure experiment",
            "radio science",
            "planetary wobble",
            "rotation axis",
            "rotation experiment",
        ],
        "mars_interior": [
            "martian core",
            "mars core",
            "crust thickness",
            "martian crust",
            "mantle",
            "interior structure",
        ],
        "weather": [
            "weather station",
            "air temperature",
            "air pressure",
            "wind speed",
            "meteorological",
        ],
        "solar_dust": [
            "solar panels",
            "solar arrays",
            "dust accumulation",
            "dust-covered",
            "power generation",
        ],
    },

    "ingenuity": {
        "first_flight": [
            "first powered flight",
            "first flight",
            "april 19, 2021",
            "first aircraft",
        ],
        "flight_history": [
            "flight number",
            "flights completed",
            "flight log",
            "flight duration",
            "flight distance",
            "72 flights",
        ],
        "mars_flight": [
            "thin atmosphere",
            "rotor blades",
            "rotor speed",
            "rotors",
            "aerodynamic",
            "lift",
        ],
        "perseverance": [
            "perseverance rover",
            "perseverance mission",
            "rover companion",
            "scouting",
        ],
        "navigation": [
            "navigation camera",
            "autonomous navigation",
            "flight control",
            "visual navigation",
            "terrain tracking",
        ],
        "final_flight": [
            "final flight",
            "last flight",
            "rotor damage",
            "damaged rotor",
            "january 18, 2024",
            "flight 72",
        ],
    },

    "lunar-module": {
        "descent_stage": [
            "descent stage",
            "descent engine",
            "landing legs",
            "landing gear",
            "descent propulsion",
        ],
        "ascent_stage": [
            "ascent stage",
            "ascent engine",
            "ascent propulsion",
            "rendezvous",
            "lunar orbit",
        ],
        "crew": [
            "astronauts",
            "lunar module pilot",
            "commander",
            "two crew members",
            "crew compartment",
        ],
        "apollo_landing": [
            "apollo 11",
            "apollo 12",
            "apollo 14",
            "apollo 15",
            "apollo 16",
            "apollo 17",
        ],
        "moon_surface": [
            "lunar surface",
            "surface operations",
            "moon landing",
            "moon surface",
            "lunar exploration",
        ],
    },

    "lunar-rover": {
        "deployment": [
            "deployed",
            "deployment",
            "unfolded",
            "folded",
            "stored in the lunar module",
            "unloaded",
        ],
        "wheels": [
            "wire mesh wheels",
            "wire-mesh wheels",
            "wheel design",
            "wheel assembly",
            "tire",
            "traction",
        ],
        "electric_drive": [
            "electric motor",
            "electric motors",
            "battery",
            "batteries",
            "electric drive",
            "drive motor",
        ],
        "apollo_drives": [
            "driving distance",
            "distance driven",
            "traverse",
            "driving on the moon",
            "lunar excursions",
        ],
        "navigation": [
            "navigation system",
            "directional gyro",
            "odometer",
            "heading indicator",
            "navigation computer",
        ],
        "moon_environment": [
            "lunar dust",
            "lunar terrain",
            "lunar gravity",
            "moon dust",
            "lunar regolith",
        ],
    },
}


# Detect suspicious Spirit/Opportunity references.
EXPLORER_PATTERNS = {
    "spirit": re.compile(
        r"\b(?:spirit rover|rover spirit|spirit's|MER-A)\b",
        re.IGNORECASE,
    ),
    "opportunity": re.compile(
        r"\b(?:opportunity rover|rover opportunity|opportunity's|MER-B)\b",
        re.IGNORECASE,
    ),
}


def check_explorer_assignment(text, document_explorer_id):
    """
    Flag possible cross-rover contamination.

    This is a heuristic and does not guarantee that
    every chunk belongs to the correct explorer.
    """
    if document_explorer_id not in EXPLORER_PATTERNS:
        return True, None

    mentioned = {
        explorer_id: len(pattern.findall(text))
        for explorer_id, pattern in EXPLORER_PATTERNS.items()
    }

    own_count = mentioned[document_explorer_id]

    other_explorer = (
        "spirit"
        if document_explorer_id == "opportunity"
        else "opportunity"
    )

    other_count = mentioned[other_explorer]

    if other_count == 0:
        return True, None

    if own_count >= other_count * 2:
        return True, None

    if other_count > own_count:
        return False, f"possible_wrong_explorer:{other_explorer}"

    return False, "shared_or_comparative_content"


def split_sentences(text):
    """
    Split text into sentences using a lightweight regex.
    """
    text = re.sub(r"\s+", " ", text).strip()

    return [
        sentence.strip()
        for sentence in re.split(
            r"(?<=[.!?])\s+(?=[A-Z0-9])",
            text,
        )
        if sentence.strip()
    ]


def keyword_matches(text, keyword):
    """
    Count keyword occurrences with word boundaries.

    Prevents short keywords from matching inside
    unrelated words.
    """
    pattern = (
        r"(?<!\w)"
        + re.escape(keyword.lower())
        + r"(?!\w)"
    )

    return len(re.findall(pattern, text))


def assign_topic(text, explorer_id, default_topic="overview"):
    """
    Classify a chunk using explorer-specific topics.

    Specific topics take priority over generic topics
    when their scores are equal.
    """
    lower_text = text.lower()

    specific_topics = EXPLORER_TOPICS.get(explorer_id, {})

    scores = {}

    for topic, keywords in specific_topics.items():
        scores[topic] = sum(
            keyword_matches(lower_text, keyword)
            for keyword in keywords
        )

    for topic, keywords in COMMON_TOPICS.items():
        scores[topic] = sum(
            keyword_matches(lower_text, keyword)
            for keyword in keywords
        )

    best_topic = max(scores, key=scores.get)

    if scores[best_topic] == 0:
        return default_topic

    return best_topic


def create_chunks(sentences):
    """
    Create chunks with one-sentence overlap.
    """
    chunks = []

    current_sentences = []
    current_word_count = 0

    for sentence in sentences:
        sentence_words = len(sentence.split())

        if (
            current_word_count + sentence_words > MAX_WORDS
            and current_word_count >= MIN_WORDS
        ):
            chunks.append(" ".join(current_sentences))

            # Preserve one sentence as overlap.
            current_sentences = [current_sentences[-1]]
            current_word_count = len(
                current_sentences[0].split()
            )

        current_sentences.append(sentence)
        current_word_count += sentence_words

    if current_sentences:
        text = " ".join(current_sentences)

        if len(text.split()) >= MIN_WORDS:
            chunks.append(text)

    return chunks


def process_document(document):
    explorer_id = document["explorer_id"]

    sentences = split_sentences(document["content"])

    text_chunks = create_chunks(sentences)

    processed = []

    for index, text in enumerate(text_chunks, start=1):
        topic = assign_topic(
            text=text,
            explorer_id=explorer_id,
            default_topic=document.get("topic") or "overview",
        )

        indexable, review_reason = check_explorer_assignment(
            text,
            explorer_id,
        )

        chunk = {
            "chunk_id": (
                f"{document['document_id']}"
                f"-chunk-{index:03d}"
            ),
            "explorer_id": explorer_id,
            "explorer_name": document["explorer_name"],
            "mission_family": document.get("mission_family"),
            "body": document.get("body"),
            "equipment_type": document.get("equipment_type"),
            "topic": topic,
            "source_agency": document.get("source_agency"),
            "source_title": document.get("source_title"),
            "source_url": document.get("source_url"),
            "document_id": document["document_id"],
            "retrieved_at": document.get("retrieved_at"),
            "indexable": indexable,
            "review_reason": review_reason,
            "content": text,
        }

        processed.append(chunk)

    return processed


def main():
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    raw_files = sorted(
        file_path
        for file_path in INPUT_DIR.glob("*.json")
        if file_path.name not in EXCLUDED_FILES
    )

    if not raw_files:
        raise FileNotFoundError(
            f"No usable JSON files found in {INPUT_DIR}"
        )

    all_chunks = []

    for file_path in raw_files:
        print(f"Processing: {file_path}")

        with file_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            document = json.load(file)

        chunks = process_document(document)

        all_chunks.extend(chunks)

        print(f"  Created {len(chunks)} chunks")

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as output:
        for chunk in all_chunks:
            output.write(
                json.dumps(
                    chunk,
                    ensure_ascii=False,
                )
                + "\n"
            )

    flagged_chunks = [
        chunk
        for chunk in all_chunks
        if not chunk["indexable"]
    ]

    topic_counts = Counter(
        chunk["topic"]
        for chunk in all_chunks
        if chunk["indexable"]
    )

    print("\nCHUNK GENERATION SUMMARY")
    print("=" * 45)
    print(f"Total chunks: {len(all_chunks)}")
    print(f"Flagged for review: {len(flagged_chunks)}")
    print(
        "Indexable chunks: "
        f"{len(all_chunks) - len(flagged_chunks)}"
    )
    print(f"Saved to: {OUTPUT_FILE}")

    print("\nTopic distribution:")
    for topic, count in topic_counts.most_common():
        print(f"  {topic}: {count}")


if __name__ == "__main__":
    main()

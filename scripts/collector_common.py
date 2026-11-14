import json
import re
from pathlib import Path
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup


OUTPUT_DIR = Path("data/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


def download_page(url):
    headers = {
        "User-Agent": "SpaceBuddies-RAG-POC/1.0"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for element in soup([
        "script",
        "style",
        "nav",
        "footer",
        "form",
        "noscript"
    ]):
        element.decompose()

    main = soup.find("main")

    if main:
        text = main.get_text(" ", strip=True)
    else:
        text = soup.get_text(" ", strip=True)

    return clean_text(text)


def collect_sources(
    sources,
    explorer_id,
    explorer_name,
    mission_family,
    body,
    equipment_type
):
    for source in sources:

        print(f"Collecting: {source['title']}")

        text = download_page(source["url"])

        document = {
            "document_id": source["id"],
            "explorer_id": explorer_id,
            "explorer_name": explorer_name,
            "mission_family": mission_family,
            "body": body,
            "equipment_type": equipment_type,
            "topic": source["topic"],
            "source_agency": "NASA",
            "source_title": source["title"],
            "source_url": source["url"],
            "retrieved_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "content": text
        }

        output_file = (
            OUTPUT_DIR /
            f"{source['id']}.json"
        )

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                document,
                file,
                indent=2,
                ensure_ascii=False
            )

        print(f"Saved: {output_file}")
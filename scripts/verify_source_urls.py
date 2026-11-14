
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests


INPUT_FILE = Path("data/processed/chunks.jsonl")
OUTPUT_FILE = Path("data/processed/source_verification.json")

HEADERS = {
    "User-Agent": "SpaceBuddiesResearch/1.0"
}


def load_sources():
    sources = {}

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            chunk = json.loads(line)

            if not chunk.get("indexable", True):
                continue

            url = chunk.get("source_url", "").strip()

            if url:
                sources.setdefault(url, set()).add(
                    chunk["explorer_id"]
                )

    return sources


def verify_url(url, explorers):
    result = {
        "url": url,
        "explorers": sorted(explorers),
        "status": "ERROR",
        "http_status": None,
        "final_url": None,
        "error": None,
    }

    parsed = urlparse(url)

    if (
        parsed.scheme != "https"
        or parsed.hostname is None
        or not (
            parsed.hostname == "nasa.gov"
            or parsed.hostname.endswith(".nasa.gov")
        )
    ):
        result["error"] = "Invalid NASA HTTPS URL"
        return result

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20,
            allow_redirects=True,
            stream=True,
        )

        result["http_status"] = response.status_code
        result["final_url"] = response.url

        final_host = urlparse(response.url).hostname or ""
        trusted = (
            final_host == "nasa.gov"
            or final_host.endswith(".nasa.gov")
        )

        if response.ok and trusted:
            result["status"] = "PASS"
        elif response.ok:
            result["status"] = "REVIEW"
            result["error"] = "Redirected outside NASA domain"
        else:
            result["status"] = "FAIL"

        response.close()

    except requests.RequestException as exc:
        result["error"] = str(exc)

    return result


def main():
    sources = load_sources()
    results = []

    print("\nSPACE BUDDIES - HTTP SOURCE VERIFICATION")
    print("=" * 55)

    for index, (url, explorers) in enumerate(
        sorted(sources.items()), start=1
    ):
        result = verify_url(url, explorers)
        results.append(result)

        print(
            f"[{index}/{len(sources)}] "
            f"{result['status']} "
            f"HTTP {result['http_status']} "
            f"{url}"
        )

        if result["error"]:
            print(f"  Reason: {result['error']}")

        if result["final_url"] != url and result["final_url"]:
            print(f"  Redirect: {result['final_url']}")

        time.sleep(0.3)

    report = {
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "total_sources": len(results),
        "results": results,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print("\nSUMMARY")
    print("=" * 55)

    for status in ("PASS", "FAIL", "REVIEW", "ERROR"):
        count = sum(
            result["status"] == status
            for result in results
        )
        print(f"{status}: {count}")

    print(f"\nReport saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

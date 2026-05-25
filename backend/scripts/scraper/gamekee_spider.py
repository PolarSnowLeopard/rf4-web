"""
Gamekee RF4 Wiki Scraper

Fetches all fish species data from the Gamekee RF4 wiki API.
Outputs raw JSON for each fish to backend/scripts/scraper/output/raw/

Usage:
    python gamekee_spider.py

API info:
    - Entry tree: GET /v1/entry/getEntryTreeById?id=127214
    - Detail: GET /v1/content/detail/{content_id}
    - Required header: game-id: 50209
"""

import json
import os
import time
import urllib.request

BASE_URL = "https://www.gamekee.com"
GAME_ID = "50209"
FISH_ENTRY_ID = "127214"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "raw")
HEADERS = {
    "game-id": GAME_ID,
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}
REQUEST_DELAY = 0.5  # seconds between requests


def _get_json(url: str) -> dict:
    """Make a GET request and return parsed JSON."""
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_entry_tree() -> list[dict]:
    """Fetch the fish entry tree and extract all content_ids."""
    url = f"{BASE_URL}/v1/entry/getEntryTreeById?id={FISH_ENTRY_ID}"
    data = _get_json(url)

    if data["code"] != 0:
        raise RuntimeError(f"Failed to fetch entry tree: {data['msg']}")

    entries = []
    for group in data["data"]:
        children = group.get("child") or []
        for child in children:
            if child.get("content_id") and child["content_id"] != 0:
                entries.append({
                    "content_id": child["content_id"],
                    "name": child["name"],
                    "icon": child.get("icon", ""),
                })
    return entries


def fetch_fish_detail(content_id: int) -> dict:
    """Fetch detailed data for a single fish."""
    url = f"{BASE_URL}/v1/content/detail/{content_id}"
    data = _get_json(url)

    if data["code"] != 0:
        raise RuntimeError(f"Failed to fetch detail {content_id}: {data['msg']}")

    return data["data"]


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Fetching entry tree...")
    entries = fetch_entry_tree()
    print(f"Found {len(entries)} fish entries")

    # Save entry index
    index_path = os.path.join(OUTPUT_DIR, "_index.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    print(f"Saved index to {index_path}")

    # Fetch each fish detail
    success = 0
    failed = []
    for i, entry in enumerate(entries):
        content_id = entry["content_id"]
        name = entry["name"]
        out_path = os.path.join(OUTPUT_DIR, f"{content_id}.json")

        if os.path.exists(out_path):
            print(f"  [{i+1}/{len(entries)}] {name} — already fetched, skipping")
            success += 1
            continue

        try:
            print(f"  [{i+1}/{len(entries)}] {name} (id={content_id})...", end=" ")
            detail = fetch_fish_detail(content_id)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(detail, f, ensure_ascii=False, indent=2)
            print("OK")
            success += 1
        except Exception as e:
            print(f"FAILED: {e}")
            failed.append({"content_id": content_id, "name": name, "error": str(e)})

        time.sleep(REQUEST_DELAY)

    print(f"\nDone: {success} succeeded, {len(failed)} failed")
    if failed:
        failed_path = os.path.join(OUTPUT_DIR, "_failed.json")
        with open(failed_path, "w", encoding="utf-8") as f:
            json.dump(failed, f, ensure_ascii=False, indent=2)
        print(f"Failed entries saved to {failed_path}")


if __name__ == "__main__":
    main()

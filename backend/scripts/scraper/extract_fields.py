"""
Fish data field extractor using LLM.

Processes raw Gamekee JSON files and extracts structured fish data
using an LLM to parse the complex nested content_json structure.

Usage:
    python extract_fields.py [--limit N] [--model MODEL]

Requires env vars:
    OPENROUTER_API_KEY
    OPENROUTER_BASE_URL (optional, defaults to https://openrouter.ai/api/v1)

Output:
    backend/scripts/scraper/output/extracted/{content_id}.json
    backend/scripts/scraper/output/extracted/_all.json  (merged result)
"""

import json
import os
import sys
import time
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
RAW_DIR = SCRIPT_DIR / "output" / "raw"
OUT_DIR = SCRIPT_DIR / "output" / "extracted"

DEFAULT_MODEL = "google/gemini-2.5-flash"
API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
API_BASE = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

EXTRACTION_PROMPT = """\
You are a data extraction assistant. Given the raw JSON data from a fish wiki page,
extract the following structured fields. The data comes from a Russian Fishing 4 game wiki.

Extract these fields:
- name_cn: Chinese name
- name_en: English name (if available, empty string otherwise)
- description: Brief description of the fish (Chinese)
- rarity: One of "常见", "稀有", "稀有鱼种", "传说", "独特" (look for 收藏 stars or rarity text)
- rare_weight: Weight threshold for star rating (上星重量), e.g. "3kg"
- super_rare_weight: Weight threshold for blue crown (蓝冠重量), e.g. "4kg"
- habitats: List of habitat/water body names where this fish can be found
- fishing_method: Fishing method (e.g. "手竿", "路亚", "海钓" etc.)
- day_activity: Day activity level description or icon indicator
- night_activity: Night activity level description or icon indicator
- img_url: Primary fish image URL (the largest one from thumb or imageList)

Important notes:
- The content_json field contains nested editor data. Look for "attrList" entries.
- Rarity is often indicated by stars (⭐️) in "收藏" field or color-coded text.
- Weight thresholds are in attrList items with orange/blue background colors.
- Habitats are in "relation-info" sections with title "栖息地".
- Image URLs start with "//cdnimg-v2.gamekee.com/..." — return them as-is (without adding http:).
- If a field cannot be determined, use empty string "" for strings or [] for lists.

Return ONLY valid JSON with the fields above. No markdown, no explanation.
"""


def call_llm(content: str, model: str) -> str:
    """Call OpenRouter-compatible API."""
    url = f"{API_BASE}/chat/completions"
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": EXTRACTION_PROMPT},
            {"role": "user", "content": content},
        ],
        "temperature": 0.0,
        "max_tokens": 2048,
        "response_format": {"type": "json_object"},
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    })

    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    return result["choices"][0]["message"]["content"]


def prepare_input(raw: dict) -> str:
    """Prepare LLM input from raw fish data — include only relevant fields."""
    data = raw.get("data", raw)
    relevant = {
        "title": data.get("title", ""),
        "thumb": data.get("thumb", ""),
        "content_json": data.get("content_json", ""),
    }
    return json.dumps(relevant, ensure_ascii=False)


def parse_llm_output(raw_output: str) -> dict:
    """Parse LLM JSON output, handling possible markdown wrapping."""
    s = raw_output.strip()
    if s.startswith("```"):
        s = s.strip("`")
        if s.lower().startswith("json"):
            s = s[4:].lstrip()
    return json.loads(s)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="Process only N entries (0=all)")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--delay", type=float, default=0.3, help="Delay between API calls")
    args = parser.parse_args()

    if not API_KEY:
        print("ERROR: OPENROUTER_API_KEY env var is required")
        sys.exit(1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Find all raw JSON files (excluding _-prefixed index files)
    raw_files = sorted(f for f in RAW_DIR.glob("*.json") if not f.name.startswith("_"))
    print(f"Found {len(raw_files)} raw files")

    if args.limit:
        raw_files = raw_files[:args.limit]
        print(f"Processing first {args.limit} only")

    success = 0
    failed = []
    results = []

    for i, raw_path in enumerate(raw_files):
        content_id = raw_path.stem
        out_path = OUT_DIR / f"{content_id}.json"

        if out_path.exists():
            with open(out_path) as f:
                results.append(json.load(f))
            print(f"  [{i+1}/{len(raw_files)}] {content_id} — skipping (exists)")
            success += 1
            continue

        try:
            with open(raw_path) as f:
                raw = json.load(f)

            title = raw.get("data", raw).get("title", content_id)
            print(f"  [{i+1}/{len(raw_files)}] {title} (id={content_id})...", end=" ", flush=True)

            llm_input = prepare_input(raw)
            llm_output = call_llm(llm_input, args.model)
            extracted = parse_llm_output(llm_output)
            extracted["content_id"] = int(content_id)
            extracted["source_url"] = f"https://www.gamekee.com/rf4/{content_id}.html"

            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(extracted, f, ensure_ascii=False, indent=2)

            results.append(extracted)
            print("OK")
            success += 1

        except Exception as e:
            print(f"FAILED: {e}")
            failed.append({"content_id": content_id, "error": str(e)})

        time.sleep(args.delay)

    # Save merged output
    all_path = OUT_DIR / "_all.json"
    with open(all_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nDone: {success} succeeded, {len(failed)} failed")
    print(f"Merged output: {all_path}")

    if failed:
        failed_path = OUT_DIR / "_failed.json"
        with open(failed_path, "w", encoding="utf-8") as f:
            json.dump(failed, f, ensure_ascii=False, indent=2)
        print(f"Failed entries: {failed_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env /usr/bin/python3
"""
Deterministic field extractor for Gamekee fish data.

Parses the structured content_json without needing LLM — the wiki uses a
consistent template so fields can be extracted by position/pattern.

Usage:
    /usr/bin/python3 parse_fields.py

Output:
    backend/scripts/scraper/output/extracted/_all.json
"""

import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
RAW_DIR = SCRIPT_DIR / "output" / "raw"
OUT_DIR = SCRIPT_DIR / "output" / "extracted"


def get_text_from_editor(editor_data):
    """Recursively extract plain text from a simpleEditor structure."""
    if not editor_data:
        return ""
    texts = []
    if isinstance(editor_data, dict):
        if editor_data.get("type") == "simpleEditor":
            return get_text_from_editor(editor_data.get("data", []))
        if "text" in editor_data:
            t = editor_data["text"].strip()
            if t:
                texts.append(t)
        for child in editor_data.get("children", []):
            texts.append(get_text_from_editor(child))
        if "data" in editor_data and isinstance(editor_data["data"], list):
            for item in editor_data["data"]:
                texts.append(get_text_from_editor(item))
    elif isinstance(editor_data, list):
        for item in editor_data:
            texts.append(get_text_from_editor(item))
    return " ".join(t for t in texts if t).strip()


def count_images_in_editor(editor_data):
    """Count image nodes in editor data (for star rating)."""
    count = 0
    if isinstance(editor_data, dict):
        if editor_data.get("type") == "image":
            count += 1
        for child in editor_data.get("children", []):
            count += count_images_in_editor(child)
        if "data" in editor_data and isinstance(editor_data["data"], list):
            for item in editor_data["data"]:
                count += count_images_in_editor(item)
        if "content" in editor_data and isinstance(editor_data["content"], dict):
            count += count_images_in_editor(editor_data["content"])
    elif isinstance(editor_data, list):
        for item in editor_data:
            count += count_images_in_editor(item)
    return count


def extract_from_content_json(content_json_str):
    """Extract structured fields from the content_json string."""
    result = {
        "name_cn": "",
        "name_en": "",
        "description": "",
        "rarity": "",
        "stars": 0,
        "rare_weight": "",
        "super_rare_weight": "",
        "habitats": [],
        "fishing_method": "",
        "baits": [],
        "img_url": "",
    }

    try:
        content = json.loads(content_json_str)
    except (json.JSONDecodeError, TypeError):
        return result

    if not isinstance(content, list):
        return result

    for block in content:
        if not isinstance(block, dict):
            continue
        block_type = block.get("type")
        block_data = block.get("data", [])

        if block_type == "illustrated-book" and isinstance(block_data, list):
            for section in block_data:
                if not isinstance(section, dict):
                    continue
                section_type = section.get("type")
                section_data = section.get("data", {})

                if section_type == "character-profile":
                    _parse_profile(section_data, result)
                elif section_type == "relation-info":
                    _parse_habitats(section_data, result)
                elif section_type == "character-info":
                    _parse_baits(section_data, result)

    return result


def _parse_profile(data, result):
    """Parse character-profile section for basic info."""
    if not isinstance(data, dict):
        return

    # Name
    name_raw = get_text_from_editor(data.get("name"))
    if name_raw:
        parts = name_raw.replace("\t", " ").split()
        cn_parts = []
        en_parts = []
        for p in parts:
            if all(ord(c) < 128 or c in "- " for c in p):
                en_parts.append(p)
            else:
                cn_parts.append(p)
        result["name_cn"] = "".join(cn_parts) if cn_parts else name_raw
        result["name_en"] = " ".join(en_parts) if en_parts else ""

    # Description
    result["description"] = get_text_from_editor(data.get("desc"))

    # Image
    image_list = data.get("imageList", [])
    if image_list and isinstance(image_list, list):
        result["img_url"] = image_list[0]

    # Attributes — parsed by position and content keywords
    # Standard template order: [0]收藏, [1]稀有度, [2]上星重量, [3]蓝冠重量,
    #   [4]日间活跃度, [5]夜间活跃度, [6]钓法, [7]玩家点位
    attr_list = data.get("attrList", [])
    if not isinstance(attr_list, list):
        return

    RARITY_KEYWORDS = ("常见", "稀有", "罕见", "传说", "独特", "稀有鱼种", "罕见鱼种")

    for i, attr in enumerate(attr_list):
        if not isinstance(attr, dict):
            continue
        title_text = get_text_from_editor(attr.get("title"))
        content_text = get_text_from_editor(attr.get("content"))

        if "收藏" in title_text:
            result["stars"] = count_images_in_editor(attr.get("content"))
        elif "钓法" in title_text:
            result["fishing_method"] = content_text
        elif any(kw in content_text for kw in RARITY_KEYWORDS):
            if not result["rarity"]:
                result["rarity"] = content_text
        elif _has_icon(attr.get("title"), "30432"):
            result["rare_weight"] = content_text
        elif _has_icon(attr.get("title"), "598251"):
            result["super_rare_weight"] = content_text
        elif i == 1 and not result["rarity"]:
            # Position-based fallback: attr[1] is usually rarity
            if content_text and content_text != "-":
                result["rarity"] = content_text
        elif i == 2 and not result["rare_weight"]:
            # Position-based fallback: attr[2] is rare_weight
            result["rare_weight"] = content_text
        elif i == 3 and not result["super_rare_weight"]:
            # Position-based fallback: attr[3] is super_rare_weight
            result["super_rare_weight"] = content_text


def _has_icon(editor_data, icon_id):
    """Check if editor data contains an image with given icon ID substring."""
    if not editor_data:
        return False
    s = json.dumps(editor_data)
    return icon_id in s


def _parse_habitats(data, result):
    """Parse relation-info section for habitats."""
    if not isinstance(data, dict):
        return
    if "栖息" not in data.get("title", ""):
        return
    for item in data.get("list", []):
        if not isinstance(item, dict):
            continue
        for content_item in item.get("content", []):
            if isinstance(content_item, dict) and content_item.get("name"):
                result["habitats"].append(content_item["name"])


def _parse_baits(data, result):
    """Parse character-info section for common baits."""
    if not isinstance(data, dict):
        return
    title = data.get("title", "")
    if "喜好" not in title and "饵料" not in title:
        return
    for info in data.get("infoList", []):
        if not isinstance(info, dict):
            continue
        bait_text = get_text_from_editor(info.get("content"))
        if bait_text:
            result["baits"].append(bait_text)


def process_file(raw_path):
    """Process a single raw JSON file and return extracted data."""
    with open(raw_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    data = raw.get("data", raw)
    content_id = int(raw_path.stem)

    # Extract from content_json
    content_json_str = data.get("content_json", "")
    extracted = extract_from_content_json(content_json_str)

    # Supplement with top-level fields
    extracted["content_id"] = content_id
    extracted["title"] = data.get("title", "")
    extracted["source_url"] = f"https://www.gamekee.com/rf4/{content_id}.html"

    # Use title as fallback for name_cn
    if not extracted["name_cn"] and extracted["title"]:
        extracted["name_cn"] = extracted["title"]

    # Image from thumb if not found in content_json
    if not extracted["img_url"]:
        thumb = data.get("thumb", "")
        if thumb:
            # First thumb is usually the main large image
            extracted["img_url"] = thumb.split(",")[0]

    return extracted


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    raw_files = sorted(f for f in RAW_DIR.glob("*.json") if not f.name.startswith("_"))
    print(f"Found {len(raw_files)} raw files")

    results = []
    failed = []

    for i, raw_path in enumerate(raw_files):
        try:
            extracted = process_file(raw_path)
            results.append(extracted)
            if (i + 1) % 50 == 0:
                print(f"  [{i+1}/{len(raw_files)}] processed...")
        except Exception as e:
            failed.append({"file": raw_path.name, "error": str(e)})
            print(f"  FAILED {raw_path.name}: {e}", file=sys.stderr)

    # Save merged output
    all_path = OUT_DIR / "_all.json"
    with open(all_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nDone: {len(results)} succeeded, {len(failed)} failed")
    print(f"Output: {all_path}")

    if failed:
        print(f"Failed: {failed}")

    # Print a sample
    if results:
        print("\n=== Sample (first entry) ===")
        print(json.dumps(results[0], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

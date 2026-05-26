#!/usr/bin/env python3
"""Parse lure detail JSON files and extract structured fields."""
import json
import os
import glob


OUTPUT_DIR = "output/raw"
RESULT_FILE = "output/extracted/_all.json"


def get_text_from_editor(editor_data):
    if not editor_data or not isinstance(editor_data, dict):
        return ""
    if editor_data.get("type") != "simpleEditor":
        return ""
    texts = []
    for para in editor_data.get("data", []):
        for child in para.get("children", []):
            if "text" in child:
                texts.append(child["text"])
    return "".join(texts).strip()


def find_profile(obj):
    if isinstance(obj, dict):
        if obj.get("type") == "character-profile":
            return obj.get("data", {})
        for v in obj.values():
            r = find_profile(v)
            if r:
                return r
    elif isinstance(obj, list):
        for item in obj:
            r = find_profile(item)
            if r:
                return r
    return None


def parse_lure(filepath):
    with open(filepath) as f:
        data = json.load(f)

    content = data.get("data", {})
    title = content.get("title", "")
    thumb = content.get("thumb", "")
    content_id = os.path.basename(filepath).replace(".json", "")

    cj = content.get("content_json", "")
    if not cj:
        return None

    try:
        parsed = json.loads(cj)
    except (json.JSONDecodeError, TypeError):
        return None

    profile = find_profile(parsed)
    if not profile:
        return None

    name_text = get_text_from_editor(profile.get("name", {}))
    desc_text = get_text_from_editor(profile.get("desc", {}))

    result = {
        "content_id": content_id,
        "name": title or name_text,
        "description": desc_text,
        "lure_type": "",
        "length": "",
        "size": "",
        "weight": "",
        "hook_size": "",
        "unlock_skill": "",
        "level_limit": "",
        "hook_component": "",
    }

    # Image from imageList or thumb
    img_url = ""
    image_list = profile.get("imageList", [])
    if image_list and isinstance(image_list, list) and image_list[0]:
        img_url = image_list[0]
    elif thumb:
        img_url = thumb.split(",")[0]

    if img_url and not img_url.startswith("http"):
        img_url = "https:" + img_url
    result["img"] = img_url

    attrs = profile.get("attrList", [])
    for attr in attrs:
        attr_title = get_text_from_editor(attr.get("title", {}))
        attr_content = get_text_from_editor(attr.get("content", {}))

        if attr_title == "形式":
            result["lure_type"] = attr_content
        elif attr_title == "长度":
            result["length"] = attr_content
        elif attr_title == "大小":
            result["size"] = attr_content
        elif attr_title == "质量":
            result["weight"] = attr_content
        elif attr_title in ("鱼钩允许的尺寸", "鱼钩允许的尺寸："):
            result["hook_size"] = attr_content
        elif attr_title in ("需解锁技能", "需解锁能力"):
            result["unlock_skill"] = attr_content
        elif attr_title in ("限制", "等级限制"):
            result["level_limit"] = attr_content
        elif attr_title in ("钓钩组件", "组件钓钩"):
            result["hook_component"] = attr_content
        else:
            # Hook size values like "小型的（16）"
            if "（" in attr_title and "）" in attr_title:
                if not result["hook_size"]:
                    result["hook_size"] = attr_title

    return result


def main():
    os.makedirs(os.path.dirname(RESULT_FILE), exist_ok=True)

    files = glob.glob(os.path.join(OUTPUT_DIR, "*.json"))
    files = [f for f in files if not f.endswith("_tree.json")]

    results = []
    failed = []

    for f in sorted(files):
        parsed = parse_lure(f)
        if parsed:
            results.append(parsed)
        else:
            failed.append(os.path.basename(f))

    with open(RESULT_FILE, "w", encoding="utf-8") as out:
        json.dump(results, out, ensure_ascii=False, indent=2)

    print(f"Parsed: {len(results)}, Failed: {len(failed)}")
    if failed[:10]:
        print(f"Failed samples: {failed[:10]}")

    fields = ["lure_type", "length", "size", "weight", "hook_size", "unlock_skill", "hook_component", "description"]
    print("\nField coverage:")
    for field in fields:
        filled = sum(1 for d in results if d.get(field))
        print(f"  {field}: {filled}/{len(results)} ({100*filled//len(results)}%)")


if __name__ == "__main__":
    main()

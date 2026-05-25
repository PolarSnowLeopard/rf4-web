#!/usr/bin/env bash
# Gamekee RF4 fish data scraper (shell version)
# Uses curl + jq — no Python dependency, low memory footprint
#
# Usage: bash fetch_all.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR/output/raw"
TREE_FILE="$OUTPUT_DIR/_tree.json"
INDEX_FILE="$OUTPUT_DIR/_index.json"
DELAY=0.5

HEADERS=(-H "game-id: 50209" -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")

mkdir -p "$OUTPUT_DIR"

# Step 1: Fetch entry tree
if [ ! -f "$TREE_FILE" ]; then
    echo "Fetching entry tree..."
    curl -s "${HEADERS[@]}" "https://www.gamekee.com/v1/entry/getEntryTreeById?id=127214" > "$TREE_FILE"
fi

# Step 2: Extract content_ids into index
echo "Extracting index..."
# Fields in tree JSON are ordered: "name":<name>,...,"content_id":<id> within each entry object
grep -o '"name":"[^"]*","name_alias":"[^"]*","pid":[0-9]*,"uid":[0-9]*,"updated_uid":[0-9]*,"status":[0-9]*,"font_color":"[^"]*","bg_color":"[^"]*","tab_num":[0-9]*,"grad":[0-9]*,"is_max_icon":[0-9]*,"sort":[0-9]*,"type":[0-9]*,"is_hot":[0-9]*,"content_id":[0-9]*' "$TREE_FILE" | \
    grep -v '"content_id":0' | \
    sed 's/"name":"\([^"]*\)".*"content_id":\([0-9]*\)/\2	\1/' > "$OUTPUT_DIR/_ids.tsv"

TOTAL=$(wc -l < "$OUTPUT_DIR/_ids.tsv")
echo "Found $TOTAL fish entries"

# Step 3: Fetch each detail
SUCCESS=0
FAILED=0
COUNT=0

while IFS=$'\t' read -r content_id name; do
    COUNT=$((COUNT + 1))
    OUT_FILE="$OUTPUT_DIR/${content_id}.json"

    if [ -f "$OUT_FILE" ]; then
        echo "  [$COUNT/$TOTAL] $name — skipping (exists)"
        SUCCESS=$((SUCCESS + 1))
        continue
    fi

    printf "  [%d/%d] %s (id=%s)... " "$COUNT" "$TOTAL" "$name" "$content_id"
    HTTP_CODE=$(curl -s -w "%{http_code}" -o "$OUT_FILE" \
        "${HEADERS[@]}" \
        "https://www.gamekee.com/v1/content/detail/$content_id")

    if [ "$HTTP_CODE" = "200" ]; then
        echo "OK"
        SUCCESS=$((SUCCESS + 1))
    else
        echo "FAILED (HTTP $HTTP_CODE)"
        rm -f "$OUT_FILE"
        FAILED=$((FAILED + 1))
    fi

    sleep "$DELAY"
done < "$OUTPUT_DIR/_ids.tsv"

echo ""
echo "Done: $SUCCESS succeeded, $FAILED failed out of $TOTAL"

#!/bin/bash
# Fetch all reel detail pages from Gamekee wiki
# Usage: bash fetch_all.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR/output/raw"
ITEMS_FILE="/tmp/reel_items.json"

mkdir -p "$OUTPUT_DIR"

# Extract content_ids from items file
CONTENT_IDS=$(python3 -c "
import json
with open('$ITEMS_FILE') as f:
    items = json.load(f)
for item in items:
    print(item['content_id'])
")

TOTAL=$(echo "$CONTENT_IDS" | wc -l | tr -d ' ')
COUNT=0
SKIPPED=0

for content_id in $CONTENT_IDS; do
    COUNT=$((COUNT + 1))
    OUTPUT_FILE="$OUTPUT_DIR/${content_id}.json"

    if [ -f "$OUTPUT_FILE" ]; then
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    HTTP_CODE=$(curl -s -o "$OUTPUT_FILE" -w "%{http_code}" \
        "https://www.gamekee.com/v1/content/detail/$content_id" \
        -H "game-id: 50209")

    if [ "$HTTP_CODE" != "200" ]; then
        echo "[$COUNT/$TOTAL] FAILED $content_id (HTTP $HTTP_CODE)"
        rm -f "$OUTPUT_FILE"
    else
        echo "[$COUNT/$TOTAL] OK $content_id"
    fi

    sleep 0.5
done

echo ""
echo "Done. Fetched: $((COUNT - SKIPPED)), Skipped: $SKIPPED, Total: $TOTAL"

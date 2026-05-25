#!/usr/bin/env bash
# Download all fish images from Gamekee CDN
# Requires Referer header to bypass CDN protection
#
# Usage: bash download_images.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
EXTRACTED="$SCRIPT_DIR/output/extracted/_all.json"
IMG_DIR="$SCRIPT_DIR/output/images"
DELAY=0.3

mkdir -p "$IMG_DIR"

if [ ! -f "$EXTRACTED" ]; then
    echo "ERROR: Run parse_fields.py first to generate $EXTRACTED"
    exit 1
fi

# Extract content_id and img_url pairs
# Format in JSON: "content_id": 599613, ... "img_url": "//cdnimg-v2..."
grep -o '"content_id": [0-9]*' "$EXTRACTED" > /tmp/fish_ids.txt
grep -o '"img_url": "[^"]*"' "$EXTRACTED" | sed 's/"img_url": "//;s/"$//' > /tmp/fish_urls.txt

TOTAL=$(wc -l < /tmp/fish_ids.txt)
echo "Found $TOTAL images to download"

SUCCESS=0
FAILED=0
COUNT=0

paste /tmp/fish_ids.txt /tmp/fish_urls.txt | while IFS=$'\t' read -r id_line url; do
    COUNT=$((COUNT + 1))
    CONTENT_ID=$(echo "$id_line" | grep -o '[0-9]*')

    # Determine file extension from URL
    EXT="${url##*.}"
    [ "$EXT" = "$url" ] && EXT="png"
    OUT_FILE="$IMG_DIR/${CONTENT_ID}.${EXT}"

    if [ -f "$OUT_FILE" ]; then
        SUCCESS=$((SUCCESS + 1))
        continue
    fi

    # Add https: prefix if protocol-relative
    FULL_URL="$url"
    if [[ "$url" == //* ]]; then
        FULL_URL="https:$url"
    fi

    HTTP_CODE=$(curl -s -w "%{http_code}" -o "$OUT_FILE" \
        -H "Referer: https://www.gamekee.com/" \
        -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
        "$FULL_URL")

    if [ "$HTTP_CODE" = "200" ] && [ -s "$OUT_FILE" ]; then
        SUCCESS=$((SUCCESS + 1))
        if [ $((COUNT % 50)) -eq 0 ]; then
            echo "  [$COUNT/$TOTAL] downloaded..."
        fi
    else
        rm -f "$OUT_FILE"
        FAILED=$((FAILED + 1))
        echo "  FAILED: $CONTENT_ID (HTTP $HTTP_CODE)"
    fi

    sleep "$DELAY"
done

echo ""
echo "Done: $SUCCESS succeeded, $FAILED failed out of $TOTAL"
echo "Images saved to: $IMG_DIR"
du -sh "$IMG_DIR"

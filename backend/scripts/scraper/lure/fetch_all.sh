#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
DELAY=0.5
IDS_FILE="output/raw/_ids.tsv"
OUT_DIR="output/raw"

HEADERS=(
  -H "game-id: 50209"
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
)

total=$(wc -l < "$IDS_FILE")
count=0
skipped=0

while IFS=$'\t' read -r content_id name; do
  count=$((count + 1))
  OUT_FILE="${OUT_DIR}/${content_id}.json"

  if [ -f "$OUT_FILE" ]; then
    skipped=$((skipped + 1))
    continue
  fi

  HTTP_CODE=$(curl -s --noproxy '*' -w "%{http_code}" -o "$OUT_FILE" \
    "${HEADERS[@]}" \
    "https://www.gamekee.com/v1/content/detail/$content_id")

  if [ "$HTTP_CODE" != "200" ]; then
    echo "FAIL [$HTTP_CODE]: $content_id ($name)"
    rm -f "$OUT_FILE"
  else
    printf "\r[%d/%d] %s" "$count" "$total" "$name"
  fi

  sleep "$DELAY"
done < "$IDS_FILE"

echo ""
echo "Done. Fetched: $((count - skipped)), Skipped: $skipped"

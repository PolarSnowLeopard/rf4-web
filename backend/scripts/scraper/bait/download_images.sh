#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
DELAY=0.3
IMG_DIR="output/images"
DATA_FILE="output/extracted/_all.json"

mkdir -p "$IMG_DIR"

HEADERS=(
  -H "Referer: https://www.gamekee.com/"
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
)

total=$(/usr/bin/python3 -c "import json; d=json.load(open('$DATA_FILE')); print(len(d))")
count=0
skipped=0
failed=0

/usr/bin/python3 -c "
import json
data = json.load(open('$DATA_FILE'))
for item in data:
    cid = item['content_id']
    img = item.get('img', '')
    if img:
        print(f\"{cid}\t{img}\")
" | while IFS=$'\t' read -r content_id img_url; do
  count=$((count + 1))
  OUT_FILE="${IMG_DIR}/${content_id}.png"

  if [ -f "$OUT_FILE" ]; then
    skipped=$((skipped + 1))
    continue
  fi

  HTTP_CODE=$(curl -s --noproxy '*' -w "%{http_code}" -o "$OUT_FILE" \
    "${HEADERS[@]}" \
    "$img_url")

  if [ "$HTTP_CODE" != "200" ]; then
    echo "FAIL [$HTTP_CODE]: $content_id"
    rm -f "$OUT_FILE"
    failed=$((failed + 1))
  fi

  sleep "$DELAY"
done

echo ""
echo "Image download complete."
ls "$IMG_DIR" | wc -l | xargs echo "Total images:"

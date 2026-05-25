#!/usr/bin/env bash
# Quick test: extract fields from one fish using LLM
# Usage: OPENROUTER_API_KEY=sk-... bash test_extract.sh
#
# Uses the nginx reverse proxy if OPENROUTER_BASE_URL is set,
# otherwise calls OpenRouter directly.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RAW_DIR="$SCRIPT_DIR/output/raw"

: "${OPENROUTER_API_KEY:?Set OPENROUTER_API_KEY}"
BASE_URL="${OPENROUTER_BASE_URL:-https://openrouter.ai/api/v1}"
MODEL="${MODEL:-google/gemini-2.5-flash}"

# Pick first raw file
SAMPLE=$(ls "$RAW_DIR"/*.json | grep -v '_' | head -1)
echo "Testing with: $SAMPLE"

# Extract title and content_json from raw file
# Build a minimal JSON payload for the LLM
TITLE=$(grep -o '"title":"[^"]*"' "$SAMPLE" | head -1 | cut -d'"' -f4)
echo "Fish: $TITLE"

# Prepare the content (just title + thumb + content_json)
CONTENT=$(cat "$SAMPLE" | sed 's/.*"data":{/"data":{/' | head -c 15000)

PROMPT='You are a data extraction assistant. Given raw JSON from a fish wiki page (Russian Fishing 4 game), extract: name_cn, name_en, description, rarity (常见/稀有/稀有鱼种/传说/独特), rare_weight, super_rare_weight, habitats (list), fishing_method, img_url. Return ONLY valid JSON.'

# Call the API
RESPONSE=$(curl -s "$BASE_URL/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENROUTER_API_KEY" \
    -d "$(cat <<ENDJSON
{
    "model": "$MODEL",
    "messages": [
        {"role": "system", "content": "$PROMPT"},
        {"role": "user", "content": $(echo "$CONTENT" | head -c 10000 | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))' 2>/dev/null || echo '""')}
    ],
    "temperature": 0.0,
    "max_tokens": 2048
}
ENDJSON
)")

echo ""
echo "=== LLM Response ==="
echo "$RESPONSE" | grep -o '"content":"[^"]*"' | head -1 | sed 's/"content":"//;s/"$//' | sed 's/\\n/\n/g; s/\\"/"/g'

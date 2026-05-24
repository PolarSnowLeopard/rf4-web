import json
import logging

from PIL import Image

from services.llm.client import chat_completion
from services.llm.vision import build_vision_message
from services.llm.config import get_llm_settings
from services.llm.exceptions import LlmInvalidResponseError
from services.recognition.prompts import CATCH_EXTRACT_PROMPT

log = logging.getLogger(__name__)

FIELDS = ("freshness", "name", "weight", "price")


def extract_fishes(
    *,
    image: Image.Image | None = None,
    image_path: str | None = None,
) -> tuple[Image.Image, list[list[str]]]:
    """Single VLM call to extract catch data from a game screenshot.

    Returns (image, fishes):
      - image: the original image (no annotation in VLM mode)
      - fishes: list of [freshness, name, weight, price] lists
    """
    if image is None and image_path is None:
        raise ValueError("image or image_path is required")
    if image is None:
        image = Image.open(image_path).convert("RGB")

    settings = get_llm_settings()
    messages = build_vision_message(CATCH_EXTRACT_PROMPT, image)

    raw = chat_completion(
        model=settings.default_vlm_model,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.0,
        max_tokens=4096,
        timeout=60.0,
    )

    fishes_dicts = _parse_fishes_json(raw)
    fishes = [
        [d.get(k, "") or "" for k in FIELDS]
        for d in fishes_dicts
    ]
    return image, fishes


def _parse_fishes_json(raw: str) -> list[dict]:
    """Parse VLM output, tolerating ```json wrapping and {fishes:[...]} envelopes."""
    s = raw.strip()
    if s.startswith("```"):
        s = s.strip("`")
        if s.lower().startswith("json"):
            s = s[4:].lstrip()
    try:
        data = json.loads(s)
    except json.JSONDecodeError as e:
        raise LlmInvalidResponseError(f"Model output is not valid JSON: {raw[:500]}") from e

    if isinstance(data, dict):
        for key in ("fishes", "result", "data", "items"):
            if isinstance(data.get(key), list):
                data = data[key]
                break
    if not isinstance(data, list):
        raise LlmInvalidResponseError(f"Model output JSON is not a list: {raw[:500]}")
    return [d for d in data if isinstance(d, dict)]

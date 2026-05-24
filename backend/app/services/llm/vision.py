import base64
from io import BytesIO

from PIL import Image


def image_to_data_url(image: Image.Image, fmt: str = "PNG") -> str:
    """Convert a PIL Image to a base64 data URL."""
    buf = BytesIO()
    image.save(buf, format=fmt)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/{fmt.lower()};base64,{b64}"


def build_vision_message(prompt: str, image: Image.Image) -> list[dict]:
    """Build an OpenAI-compatible vision message with text + image."""
    return [{
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": image_to_data_url(image)}},
        ],
    }]

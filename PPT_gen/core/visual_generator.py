from openai import OpenAI
from config import OPENAI_API_KEY
from pathlib import Path
import base64
import re

client = OpenAI(api_key=OPENAI_API_KEY)


def safe_filename(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9_\\-]", "_", text)
    return text[:40]


def generate_slide_visual(slide, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)

    prompt = f"""
Create a professional presentation visual.

Slide Title: {slide.title}
Slide Context: {slide.visual_hint}

Design Style:
- Clean corporate presentation graphic
- Minimalist
- Professional consulting-style visual
- White or subtle gradient background
- Suitable for executive PowerPoint
"""

    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024"
    )

    image_base64 = result.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)

    filename = safe_filename(slide.title) + ".png"
    image_path = output_dir / filename
    image_path.write_bytes(image_bytes)

    return image_path
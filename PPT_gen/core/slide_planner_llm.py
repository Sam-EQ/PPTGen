from openai import AsyncOpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL_SLIDES
from core.schemas import Deck
import json

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are a presentation architect.

Convert the input into a structured slide deck.

STRICT RULES:
- Return ONLY valid JSON
- No markdown
- No commentary
- No explanations

Format:
{
  "slides": [
    {
      "title": "Slide title",
      "bullets": ["Bullet 1", "Bullet 2"],
      "notes": "Optional speaker notes",
      "visual_hint": "Optional visual suggestion"
    }
  ]
}
"""


async def plan_slides(summary: str) -> Deck:
    response = await client.responses.create(
        model=OPENAI_MODEL_SLIDES,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": summary},
        ],
        temperature=0.3,
    )

    raw_output = response.output_text.strip()

    try:
        data = json.loads(raw_output)
        return Deck(**data)
    except Exception as e:
        raise ValueError(
            f"\nSlide JSON parsing failed\n"
            f"Error: {e}\n\n"
            f"Raw model output:\n{raw_output}"
        )
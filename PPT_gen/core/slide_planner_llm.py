from openai import AsyncOpenAI
from config import OPENAI_API_KEY
from core.schemas import Deck

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


SYSTEM_PROMPT = """
You are a presentation architect.

Convert the input into a structured slide deck.

Rules:
- Clear slide titles
- Concise bullets
- Logical narrative flow
- Executive-level tone
- Include speaker notes where useful
- Suggest visuals when appropriate
"""


async def plan_slides(summary: str) -> Deck:
    response = await client.responses.parse(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": summary},
        ],
        response_format=Deck,
        temperature=0.3,
    )

    return response.output_parsed
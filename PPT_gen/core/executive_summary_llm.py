from openai import AsyncOpenAI
from config import OPENAI_API_KEY

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


SYSTEM_PROMPT = """
You are an executive design strategist.

Summarize the provided markdown into a concise executive briefing:
- Opportunity / document purpose
- Key themes
- Critical risks
- Budget / schedule signals
- Strategic implications
"""


async def generate_executive_summary(markdown: str) -> str:
    response = await client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": markdown},
        ],
        temperature=0.2,
    )

    return response.output_text.strip()
import base64
import io
from PIL import Image
from openai import AsyncOpenAI
from config import OPENAI_API_KEY, VLM_MODEL

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

VLM_PROMPT = """
You are an expert document analyst. I am providing you with a full page image from a PDF.
Your task: Identify all visual elements (charts, diagrams, tables, photos, or maps) on this page.

For each visual element:
1. Provide a highly detailed description.
2. If it is a chart/graph: Describe the axes, labels, data points, and the trend.
3. If it is a table: Reconstruct the data accurately in Markdown format.
4. If it is a diagram/flowchart: Explain the logic, steps, and connections.
5. Extract every minute detail, number, and label exactly as shown.

STRICT RULE: Do not describe or transcribe the standard running body text of the page. ONLY describe the visual assets and their internal content.
"""

async def describe_page_visuals(page_image: Image.Image) -> str:
    # Convert PIL to Base64
    buffered = io.BytesIO()
    page_image.save(buffered, format="JPEG", quality=90)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    response = await client.chat.completions.create(
        model=VLM_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": VLM_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img_str}"},
                    },
                ],
            }
        ],
        max_tokens=2000,
    )
    return response.choices[0].message.content
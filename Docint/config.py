import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR / "tmp"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VLM_MODEL = "gpt-4o" 

DEVICE = "cuda" if os.getenv("USE_CUDA") == "true" else "cpu"
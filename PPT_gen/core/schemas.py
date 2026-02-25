from pydantic import BaseModel
from typing import List, Optional


class Slide(BaseModel):
    title: str
    bullets: List[str]
    notes: Optional[str] = None
    visual_hint: Optional[str] = None


class Deck(BaseModel):
    slides: List[Slide]
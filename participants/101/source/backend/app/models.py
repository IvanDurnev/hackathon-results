from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class Style(str, Enum):
    CORPORATE = "corporate"
    CREATIVE = "creative"
    MINIMAL = "minimal"

class Tone(str, Enum):
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    ACADEMIC = "academic"

class PresentationRequest(BaseModel):
    prompt: str
    num_slides: int
    style: Style
    tone: Tone
    include_images: bool

class SlideContent(BaseModel):
    title: str
    content: str
    image_prompt: Optional[str] = None
    image_url: Optional[str] = None

class PresentationResponse(BaseModel):
    slides: List[SlideContent]
    file_url: str
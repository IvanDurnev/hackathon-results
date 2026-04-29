"""Models for the internal AI generation API."""

from __future__ import annotations

from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from .models import SlideTypeT


StyleIdT = Literal["business", "friendly", "academic", "promo"]


class LayoutGenerationBasis(BaseModel):
    kind: Literal["layout"]
    templateId: str
    layoutIds: Optional[list[str]] = None

    model_config = ConfigDict(extra="forbid")


class StyleGenerationBasis(BaseModel):
    kind: Literal["style"]
    styleId: StyleIdT

    model_config = ConfigDict(extra="forbid")


GenerationBasis = Annotated[
    Union[LayoutGenerationBasis, StyleGenerationBasis],
    Field(discriminator="kind"),
]


class OutlineSlide(BaseModel):
    order: int
    title: str
    purpose: str = ""
    keyPoints: list[str] = Field(default_factory=list)
    visualIntent: Optional[str] = None
    needsImage: bool = False
    slideType: Optional[SlideTypeT] = None
    imagePrompt: Optional[str] = None
    speakerNotes: Optional[str] = None


class PresentationOutline(BaseModel):
    title: str
    audience: Optional[str] = None
    goal: Optional[str] = None
    slides: list[OutlineSlide] = Field(default_factory=list)


class OutlineGenerationRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=4000)
    slideCount: int = Field(ge=1, le=40)
    language: str = "ru"
    basis: GenerationBasis


class OutlineRetryRequest(BaseModel):
    feedback: str = Field(min_length=1, max_length=2000)
    outline: PresentationOutline


class OutlineGenerationResponse(BaseModel):
    generationId: str
    status: Literal["outline_ready"] = "outline_ready"
    outline: PresentationOutline


class ImagePolicy(BaseModel):
    generateImages: bool = True
    imageType: Literal["png", "bmp", "gif", "tiff", "jpeg"] = "png"


class PresentationBuildRequest(BaseModel):
    outline: PresentationOutline
    imagePolicy: ImagePolicy = Field(default_factory=ImagePolicy)


class SlideRegenerateRequest(BaseModel):
    instructions: Optional[str] = Field(default=None, max_length=2000)


class ImageRegenerateRequest(BaseModel):
    prompt: Optional[str] = Field(default=None, max_length=2000)
    imageType: Optional[Literal["png", "bmp", "gif", "tiff", "jpeg"]] = None


class ImageJobAsset(BaseModel):
    id: str
    type: Literal["image"] = "image"
    mimeType: str
    url: Optional[str] = None
    fileName: Optional[str] = None


class ImageJobView(BaseModel):
    id: str
    slideId: str
    elementId: str
    prompt: str
    imageType: str
    status: Literal["pending", "in_progress", "ready", "failed"]
    assetId: Optional[str] = None
    url: Optional[str] = None
    asset: Optional[ImageJobAsset] = None
    error: Optional[str] = None
    version: int = 1
    createdAt: int
    updatedAt: int


class ImageJobsResponse(BaseModel):
    presentationId: str
    jobs: list[ImageJobView] = Field(default_factory=list)

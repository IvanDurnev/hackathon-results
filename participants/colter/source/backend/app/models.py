"""Pydantic models for presentation/template documents.

Mirrors the TypeScript types described in the spec. JSON is the single source of truth.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

# ----- common geometry & enums --------------------------------------------------

SlideTypeT = Literal["title", "text", "image", "bullets", "conclusion"]
ElementTypeT = Literal["text", "image", "shape", "line", "icon", "group"]
ElementRoleT = Literal[
    "title",
    "subtitle",
    "body",
    "caption",
    "bulletList",
    "image",
    "logo",
    "footer",
    "slideNumber",
    "decorative",
    "custom",
]
ContentBehaviorKindT = Literal["static", "placeholder", "generated", "manual"]
TextOverflowT = Literal["clip", "shrink", "ellipsis", "error"]
SplitStrategyT = Literal["none", "new_slide", "duplicate_layout", "summarize"]
RatioT = Literal["16:9", "4:3", "custom"]
ImageFitT = Literal["cover", "contain", "stretch"]
ShapeKindT = Literal["rect", "roundRect", "ellipse", "triangle"]


class Frame(BaseModel):
    xEmu: int
    yEmu: int
    wEmu: int
    hEmu: int
    rotate: float = 0


class SlideSize(BaseModel):
    widthEmu: int
    heightEmu: int
    ratio: RatioT


class ThemeFonts(BaseModel):
    heading: str
    body: str


class ThemeColors(BaseModel):
    background: str
    text: str
    primary: str
    secondary: str
    accent: str


class PresentationTheme(BaseModel):
    fonts: ThemeFonts
    colors: ThemeColors


class BackgroundColor(BaseModel):
    type: Literal["color"]
    value: str


class BackgroundImage(BaseModel):
    type: Literal["image"]
    assetId: str
    fit: ImageFitT


class BackgroundGradient(BaseModel):
    type: Literal["gradient"]
    from_: str = Field(alias="from")
    to: str
    angle: float

    model_config = ConfigDict(populate_by_name=True)


SlideBackground = Annotated[
    Union[BackgroundColor, BackgroundImage, BackgroundGradient],
    Field(discriminator="type"),
]


class ElementContentBehavior(BaseModel):
    kind: ContentBehaviorKindT
    readonly: bool = False
    fillRole: Optional[ElementRoleT] = None


class ElementConstraints(BaseModel):
    minWEmu: Optional[int] = None
    minHEmu: Optional[int] = None
    maxWEmu: Optional[int] = None
    maxHEmu: Optional[int] = None
    preserveAspectRatio: Optional[bool] = None
    maxChars: Optional[int] = None
    maxLines: Optional[int] = None
    overflow: Optional[TextOverflowT] = None
    minFontSize: Optional[int] = None
    splitStrategy: Optional[SplitStrategyT] = None


class BoxSpacing(BaseModel):
    topEmu: int = 0
    rightEmu: int = 0
    bottomEmu: int = 0
    leftEmu: int = 0


class TextStyle(BaseModel):
    fontFamily: str
    fontSize: int
    fontWeight: Optional[int] = None
    italic: Optional[bool] = None
    underline: Optional[bool] = None
    color: str
    align: Literal["left", "center", "right", "justify"]
    lineHeight: Optional[float] = None
    letterSpacing: Optional[float] = None
    padding: Optional[BoxSpacing] = None


class ShadowStyle(BaseModel):
    color: str
    opacity: float
    blurEmu: int
    offsetXEmu: int
    offsetYEmu: int


class ShapeStyle(BaseModel):
    fill: Optional[str] = None
    stroke: Optional[str] = None
    strokeWidth: Optional[int] = None
    radiusEmu: Optional[int] = None
    shadow: Optional[ShadowStyle] = None


class LineStyle(BaseModel):
    color: str
    widthEmu: int
    dash: Optional[Literal["solid", "dash", "dot"]] = None
    startArrow: Optional[bool] = None
    endArrow: Optional[bool] = None


class ImageCrop(BaseModel):
    xEmu: int
    yEmu: int
    wEmu: int
    hEmu: int


class ImageGenerationMeta(BaseModel):
    prompt: str
    negativePrompt: Optional[str] = None
    model: Optional[str] = None
    seed: Optional[str] = None
    version: Optional[int] = None


# ----- elements -----------------------------------------------------------------


class _BaseElement(BaseModel):
    id: str
    name: Optional[str] = None
    role: Optional[ElementRoleT] = None
    contentBehavior: ElementContentBehavior
    sourcePlaceholderId: Optional[str] = None
    frame: Frame
    zIndex: int = 0
    locked: bool = False
    visible: bool = True
    opacity: Optional[float] = None
    constraints: Optional[ElementConstraints] = None
    meta: Optional[dict[str, Any]] = None


class TextElement(_BaseElement):
    type: Literal["text"]
    text: str = ""
    placeholder: Optional[str] = None
    style: TextStyle


class ImageElement(_BaseElement):
    type: Literal["image"]
    assetId: Optional[str] = None
    placeholder: Optional[str] = None
    fit: ImageFitT = "cover"
    crop: Optional[ImageCrop] = None
    alt: Optional[str] = None
    generation: Optional[ImageGenerationMeta] = None


class ShapeElement(_BaseElement):
    type: Literal["shape"]
    shape: ShapeKindT
    style: ShapeStyle


class LineElement(_BaseElement):
    type: Literal["line"]
    style: LineStyle


class IconElementStyle(BaseModel):
    color: Optional[str] = None


class IconElement(_BaseElement):
    type: Literal["icon"]
    assetId: Optional[str] = None
    iconName: Optional[str] = None
    style: Optional[IconElementStyle] = None


class GroupElement(_BaseElement):
    type: Literal["group"]
    children: list[str] = Field(default_factory=list)


SlideElement = Annotated[
    Union[
        TextElement,
        ImageElement,
        ShapeElement,
        LineElement,
        IconElement,
        GroupElement,
    ],
    Field(discriminator="type"),
]


# ----- slides & docs ------------------------------------------------------------


class LayoutDocument(BaseModel):
    id: str
    name: str
    slideType: SlideTypeT
    background: SlideBackground
    elements: list[SlideElement] = Field(default_factory=list)
    meta: Optional[dict[str, Any]] = None


class SlideDocument(BaseModel):
    id: str
    name: Optional[str] = None
    slideType: SlideTypeT
    layoutId: Optional[str] = None
    background: SlideBackground
    elements: list[SlideElement] = Field(default_factory=list)
    notes: Optional[str] = None
    meta: Optional[dict[str, Any]] = None


class Asset(BaseModel):
    id: str
    type: Literal["image", "icon", "font"]
    mimeType: str
    url: Optional[str] = None
    base64: Optional[str] = None
    widthEmu: Optional[int] = None
    heightEmu: Optional[int] = None
    fileName: Optional[str] = None
    meta: Optional[dict[str, Any]] = None


class TemplateDocument(BaseModel):
    schemaVersion: str = "1.0.0"
    documentType: Literal["template"]
    id: str
    name: str
    slideSize: SlideSize
    theme: PresentationTheme
    layouts: list[LayoutDocument] = Field(default_factory=list)
    assets: list[Asset] = Field(default_factory=list)
    meta: Optional[dict[str, Any]] = None


class PresentationDocument(BaseModel):
    schemaVersion: str = "1.0.0"
    documentType: Literal["presentation"]
    id: str
    name: str
    templateId: Optional[str] = None
    slideSize: SlideSize
    theme: PresentationTheme
    slides: list[SlideDocument] = Field(default_factory=list)
    assets: list[Asset] = Field(default_factory=list)
    meta: Optional[dict[str, Any]] = None


# ----- summaries returned by list endpoints ------------------------------------


class TemplateSummary(BaseModel):
    id: str
    name: str
    slideSize: SlideSize


class PresentationSummary(BaseModel):
    id: str
    name: str
    templateId: Optional[str] = None
    slideCount: int

"""Seed default template and one starter presentation when storage is empty."""

from __future__ import annotations

from .models import (
    BackgroundColor,
    ElementContentBehavior,
    Frame,
    LayoutDocument,
    PresentationDocument,
    PresentationTheme,
    ShapeStyle,
    SlideDocument,
    SlideSize,
    TemplateDocument,
    TextStyle,
    ThemeColors,
    ThemeFonts,
)
from .storage import (
    get_presentation,
    get_template,
    list_presentations,
    list_templates,
    save_presentation,
    save_template,
)


SLIDE_W = 12192000
SLIDE_H = 6858000

_THEME = PresentationTheme(
    fonts=ThemeFonts(heading="Inter", body="Inter"),
    colors=ThemeColors(
        background="#FFFFFF",
        text="#111827",
        primary="#2563EB",
        secondary="#64748B",
        accent="#F97316",
    ),
)


def _bg_white() -> BackgroundColor:
    return BackgroundColor(type="color", value="#FFFFFF")


def _title_layout() -> LayoutDocument:
    return LayoutDocument(
        id="layout_title_01",
        name="Title",
        slideType="title",
        background=_bg_white(),
        elements=[
            {
                "id": "title_placeholder",
                "name": "Title",
                "type": "text",
                "role": "title",
                "contentBehavior": {"kind": "placeholder", "readonly": False, "fillRole": "title"},
                "text": "",
                "placeholder": "Название презентации",
                "frame": {"xEmu": 914400, "yEmu": 2400000, "wEmu": 10363200, "hEmu": 1100000, "rotate": 0},
                "style": {"fontFamily": "Inter", "fontSize": 56, "fontWeight": 700,
                          "color": "#111827", "align": "left", "lineHeight": 1.1},
                "constraints": {"maxChars": 80, "maxLines": 2, "overflow": "shrink", "minFontSize": 40, "splitStrategy": "none"},
                "zIndex": 10, "locked": False, "visible": True,
            },
            {
                "id": "subtitle_placeholder",
                "name": "Subtitle",
                "type": "text",
                "role": "subtitle",
                "contentBehavior": {"kind": "placeholder", "readonly": False, "fillRole": "subtitle"},
                "text": "",
                "placeholder": "Подзаголовок",
                "frame": {"xEmu": 914400, "yEmu": 3700000, "wEmu": 10363200, "hEmu": 700000, "rotate": 0},
                "style": {"fontFamily": "Inter", "fontSize": 28, "fontWeight": 400, "color": "#64748B",
                          "align": "left", "lineHeight": 1.2},
                "constraints": {"maxChars": 120, "maxLines": 2, "overflow": "shrink", "minFontSize": 18},
                "zIndex": 11, "locked": False, "visible": True,
            },
        ],
    )


def _text_layout() -> LayoutDocument:
    return LayoutDocument(
        id="layout_text_01",
        name="Text",
        slideType="text",
        background=_bg_white(),
        elements=[
            {
                "id": "heading_placeholder",
                "name": "Heading",
                "type": "text",
                "role": "title",
                "contentBehavior": {"kind": "placeholder", "readonly": False, "fillRole": "title"},
                "text": "",
                "placeholder": "Заголовок раздела",
                "frame": {"xEmu": 914400, "yEmu": 700000, "wEmu": 10363200, "hEmu": 800000, "rotate": 0},
                "style": {"fontFamily": "Inter", "fontSize": 40, "fontWeight": 700, "color": "#111827", "align": "left"},
                "constraints": {"maxChars": 80, "maxLines": 2, "overflow": "shrink", "minFontSize": 28},
                "zIndex": 10, "locked": False, "visible": True,
            },
            {
                "id": "body_placeholder",
                "name": "Body",
                "type": "text",
                "role": "body",
                "contentBehavior": {"kind": "placeholder", "readonly": False, "fillRole": "body"},
                "text": "",
                "placeholder": "Текст слайда",
                "frame": {"xEmu": 914400, "yEmu": 1700000, "wEmu": 10363200, "hEmu": 4400000, "rotate": 0},
                "style": {"fontFamily": "Inter", "fontSize": 22, "fontWeight": 400, "color": "#111827", "align": "left", "lineHeight": 1.5},
                "constraints": {"maxChars": 800, "maxLines": 12, "overflow": "shrink", "minFontSize": 14},
                "zIndex": 11, "locked": False, "visible": True,
            },
        ],
    )


def _bullets_layout() -> LayoutDocument:
    return LayoutDocument(
        id="layout_bullets_01",
        name="Bullets",
        slideType="bullets",
        background=_bg_white(),
        elements=[
            {
                "id": "heading_placeholder",
                "name": "Heading",
                "type": "text",
                "role": "title",
                "contentBehavior": {"kind": "placeholder", "readonly": False, "fillRole": "title"},
                "text": "",
                "placeholder": "Заголовок",
                "frame": {"xEmu": 914400, "yEmu": 700000, "wEmu": 10363200, "hEmu": 800000, "rotate": 0},
                "style": {"fontFamily": "Inter", "fontSize": 40, "fontWeight": 700, "color": "#111827", "align": "left"},
                "zIndex": 10, "locked": False, "visible": True,
            },
            {
                "id": "bullets_placeholder",
                "name": "Bullets",
                "type": "text",
                "role": "bulletList",
                "contentBehavior": {"kind": "placeholder", "readonly": False, "fillRole": "bulletList"},
                "text": "",
                "placeholder": "• Пункт 1\n• Пункт 2\n• Пункт 3",
                "frame": {"xEmu": 914400, "yEmu": 1700000, "wEmu": 10363200, "hEmu": 4400000, "rotate": 0},
                "style": {"fontFamily": "Inter", "fontSize": 24, "fontWeight": 400, "color": "#111827", "align": "left", "lineHeight": 1.6},
                "constraints": {"maxLines": 8, "overflow": "shrink", "minFontSize": 16},
                "zIndex": 11, "locked": False, "visible": True,
            },
        ],
    )


def _image_layout() -> LayoutDocument:
    return LayoutDocument(
        id="layout_image_01",
        name="Image",
        slideType="image",
        background=_bg_white(),
        elements=[
            {
                "id": "heading_placeholder",
                "name": "Heading",
                "type": "text",
                "role": "title",
                "contentBehavior": {"kind": "placeholder", "readonly": False, "fillRole": "title"},
                "text": "",
                "placeholder": "Заголовок",
                "frame": {"xEmu": 914400, "yEmu": 700000, "wEmu": 10363200, "hEmu": 700000, "rotate": 0},
                "style": {"fontFamily": "Inter", "fontSize": 36, "fontWeight": 700, "color": "#111827", "align": "left"},
                "zIndex": 10, "locked": False, "visible": True,
            },
            {
                "id": "image_placeholder",
                "name": "Image",
                "type": "image",
                "role": "image",
                "contentBehavior": {"kind": "placeholder", "readonly": False, "fillRole": "image"},
                "fit": "cover",
                "frame": {"xEmu": 914400, "yEmu": 1600000, "wEmu": 10363200, "hEmu": 4500000, "rotate": 0},
                "zIndex": 11, "locked": False, "visible": True,
            },
        ],
    )


def _conclusion_layout() -> LayoutDocument:
    return LayoutDocument(
        id="layout_conclusion_01",
        name="Conclusion",
        slideType="conclusion",
        background=BackgroundColor(type="color", value="#111827"),
        elements=[
            {
                "id": "heading_placeholder",
                "name": "Heading",
                "type": "text",
                "role": "title",
                "contentBehavior": {"kind": "placeholder", "readonly": False, "fillRole": "title"},
                "text": "",
                "placeholder": "Спасибо за внимание",
                "frame": {"xEmu": 914400, "yEmu": 2700000, "wEmu": 10363200, "hEmu": 1100000, "rotate": 0},
                "style": {"fontFamily": "Inter", "fontSize": 56, "fontWeight": 700, "color": "#FFFFFF", "align": "center"},
                "zIndex": 10, "locked": False, "visible": True,
            },
        ],
    )


def default_template() -> TemplateDocument:
    return TemplateDocument(
        schemaVersion="1.0.0",
        documentType="template",
        id="template_business_01",
        name="Business Minimal",
        slideSize=SlideSize(widthEmu=SLIDE_W, heightEmu=SLIDE_H, ratio="16:9"),
        theme=_THEME,
        layouts=[_title_layout(), _text_layout(), _bullets_layout(), _image_layout(), _conclusion_layout()],
        assets=[],
    )


def starter_presentation() -> PresentationDocument:
    return PresentationDocument(
        schemaVersion="1.0.0",
        documentType="presentation",
        id="presentation_starter",
        name="Стартовая презентация",
        templateId="template_business_01",
        slideSize=SlideSize(widthEmu=SLIDE_W, heightEmu=SLIDE_H, ratio="16:9"),
        theme=_THEME,
        slides=[
            SlideDocument(
                id="slide_001",
                name="Титульный слайд",
                slideType="title",
                layoutId="layout_title_01",
                background=_bg_white(),
                elements=[
                    {
                        "id": "el_001",
                        "type": "text",
                        "role": "title",
                        "sourcePlaceholderId": "title_placeholder",
                        "contentBehavior": {"kind": "manual", "readonly": False, "fillRole": "title"},
                        "text": "ИИ-генератор презентаций",
                        "frame": {"xEmu": 914400, "yEmu": 2400000, "wEmu": 10363200, "hEmu": 1100000, "rotate": 0},
                        "style": {"fontFamily": "Inter", "fontSize": 56, "fontWeight": 700, "color": "#111827", "align": "left"},
                        "zIndex": 10, "locked": False, "visible": True,
                    },
                    {
                        "id": "el_002",
                        "type": "text",
                        "role": "subtitle",
                        "sourcePlaceholderId": "subtitle_placeholder",
                        "contentBehavior": {"kind": "manual", "readonly": False, "fillRole": "subtitle"},
                        "text": "MVP редактора по техническому заданию",
                        "frame": {"xEmu": 914400, "yEmu": 3700000, "wEmu": 10363200, "hEmu": 700000, "rotate": 0},
                        "style": {"fontFamily": "Inter", "fontSize": 28, "fontWeight": 400, "color": "#64748B", "align": "left"},
                        "zIndex": 11, "locked": False, "visible": True,
                    },
                ],
            )
        ],
    )


def seed_if_empty() -> None:
    if not list_templates():
        save_template(default_template())
    if not list_presentations():
        save_presentation(starter_presentation())

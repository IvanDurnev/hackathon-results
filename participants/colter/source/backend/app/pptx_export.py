"""PPTX export.

Coordinates are already in EMU, which python-pptx uses natively (Emu()).
We add slides, apply backgrounds, sort elements by zIndex, and emit
editable text/image/shape/line elements.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Pt

from .models import PresentationDocument, SlideDocument, SlideElement
from .storage import asset_dir

ALIGN_MAP = {
    "left": PP_ALIGN.LEFT,
    "center": PP_ALIGN.CENTER,
    "right": PP_ALIGN.RIGHT,
    "justify": PP_ALIGN.JUSTIFY,
}

SHAPE_MAP = {
    "rect": MSO_SHAPE.RECTANGLE,
    "roundRect": MSO_SHAPE.ROUNDED_RECTANGLE,
    "ellipse": MSO_SHAPE.OVAL,
    "triangle": MSO_SHAPE.ISOSCELES_TRIANGLE,
}


def _hex_to_rgb(value: str) -> RGBColor:
    v = value.lstrip("#")
    if len(v) == 3:
        v = "".join(ch * 2 for ch in v)
    return RGBColor(int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16))


def _resolve_asset_path(asset_id: str | None, doc: PresentationDocument) -> Path | None:
    if not asset_id:
        return None
    asset = next((a for a in doc.assets if a.id == asset_id), None)
    folder = asset_dir(asset_id)
    if not asset or not folder:
        return None
    if asset.fileName:
        candidate = folder / asset.fileName
        if candidate.exists():
            return candidate
    files = [p for p in folder.iterdir() if p.is_file()]
    return files[0] if files else None


def _apply_background(slide, bg, doc: PresentationDocument) -> None:
    if bg.type == "color":
        fill = slide.background.fill
        fill.solid()
        fill.fore_color.rgb = _hex_to_rgb(bg.value)
    elif bg.type == "image":
        path = _resolve_asset_path(bg.assetId, doc)
        if path is not None:
            slide.shapes.add_picture(
                str(path), 0, 0, width=Emu(doc.slideSize.widthEmu), height=Emu(doc.slideSize.heightEmu)
            )


def _add_text(slide, el, theme_text_color: str) -> None:
    box = slide.shapes.add_textbox(
        Emu(el.frame.xEmu),
        Emu(el.frame.yEmu),
        Emu(el.frame.wEmu),
        Emu(el.frame.hEmu),
    )
    tf = box.text_frame
    tf.word_wrap = True
    lines = (el.text or "").split("\n") if el.text else [""]
    for i, line in enumerate(lines):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = ALIGN_MAP.get(el.style.align, PP_ALIGN.LEFT)
        run = para.add_run()
        run.text = line
        run.font.name = el.style.fontFamily
        run.font.size = Pt(el.style.fontSize)
        if el.style.fontWeight and el.style.fontWeight >= 600:
            run.font.bold = True
        if el.style.italic:
            run.font.italic = True
        if el.style.underline:
            run.font.underline = True
        run.font.color.rgb = _hex_to_rgb(el.style.color or theme_text_color)


def _add_image(slide, el, doc: PresentationDocument) -> None:
    path = _resolve_asset_path(el.assetId, doc)
    if path is None:
        return
    slide.shapes.add_picture(
        str(path),
        Emu(el.frame.xEmu),
        Emu(el.frame.yEmu),
        width=Emu(el.frame.wEmu),
        height=Emu(el.frame.hEmu),
    )


def _add_shape(slide, el) -> None:
    shape_type = SHAPE_MAP.get(el.shape, MSO_SHAPE.RECTANGLE)
    sh = slide.shapes.add_shape(
        shape_type,
        Emu(el.frame.xEmu),
        Emu(el.frame.yEmu),
        Emu(el.frame.wEmu),
        Emu(el.frame.hEmu),
    )
    if el.style.fill:
        sh.fill.solid()
        sh.fill.fore_color.rgb = _hex_to_rgb(el.style.fill)
    else:
        sh.fill.background()
    if el.style.stroke:
        sh.line.color.rgb = _hex_to_rgb(el.style.stroke)
        if el.style.strokeWidth:
            sh.line.width = Emu(el.style.strokeWidth)
    else:
        sh.line.fill.background()


def _add_line(slide, el) -> None:
    connector = slide.shapes.add_connector(
        1,  # straight
        Emu(el.frame.xEmu),
        Emu(el.frame.yEmu),
        Emu(el.frame.xEmu + el.frame.wEmu),
        Emu(el.frame.yEmu + el.frame.hEmu),
    )
    connector.line.color.rgb = _hex_to_rgb(el.style.color)
    connector.line.width = Emu(el.style.widthEmu)


def _emit(slide, el: SlideElement, doc: PresentationDocument) -> None:
    if not el.visible:
        return
    if el.type == "text":
        _add_text(slide, el, doc.theme.colors.text)
    elif el.type == "image":
        _add_image(slide, el, doc)
    elif el.type == "shape":
        _add_shape(slide, el)
    elif el.type == "line":
        _add_line(slide, el)
    elif el.type == "icon":
        # icons fall back to image rendering when an asset is provided
        _add_image(slide, el, doc)
    elif el.type == "group":
        # groups are exploded in v1
        return


def export_to_pptx(doc: PresentationDocument) -> bytes:
    prs = Presentation()
    prs.slide_width = Emu(doc.slideSize.widthEmu)
    prs.slide_height = Emu(doc.slideSize.heightEmu)
    blank_layout = prs.slide_layouts[6]  # blank
    for slide_doc in doc.slides:
        slide = prs.slides.add_slide(blank_layout)
        _apply_background(slide, slide_doc.background, doc)
        ordered = sorted(slide_doc.elements, key=lambda e: e.zIndex)
        for el in ordered:
            _emit(slide, el, doc)
        if slide_doc.notes:
            slide.notes_slide.notes_text_frame.text = slide_doc.notes
    buf = BytesIO()
    prs.save(buf)
    return buf.getvalue()

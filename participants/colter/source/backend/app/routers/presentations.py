from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Response

from ..models import PresentationDocument, PresentationSummary
from ..pptx_export import export_to_pptx
from ..storage import (
    delete_presentation,
    get_presentation,
    list_presentations,
    save_presentation,
)
from ..validation import export_blocking_errors, validate_presentation

router = APIRouter(prefix="/api/presentations", tags=["presentations"])


@router.get("", response_model=list[PresentationSummary])
def index():
    return [
        PresentationSummary(
            id=p.id, name=p.name, templateId=p.templateId, slideCount=len(p.slides)
        )
        for p in list_presentations()
    ]


@router.get("/{presentation_id}", response_model=PresentationDocument)
def show(presentation_id: str):
    doc = get_presentation(presentation_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Presentation not found")
    return doc


@router.post("", response_model=PresentationDocument)
def create(doc: PresentationDocument):
    issues = validate_presentation(doc)
    blocking = export_blocking_errors(issues)
    if blocking:
        raise HTTPException(status_code=422, detail={"issues": blocking})
    return save_presentation(doc)


@router.put("/{presentation_id}", response_model=PresentationDocument)
def update(presentation_id: str, doc: PresentationDocument):
    if doc.id != presentation_id:
        raise HTTPException(status_code=400, detail="Path id and body id mismatch")
    issues = validate_presentation(doc)
    blocking = export_blocking_errors(issues)
    if blocking:
        raise HTTPException(status_code=422, detail={"issues": blocking})
    return save_presentation(doc)


@router.delete("/{presentation_id}")
def destroy(presentation_id: str):
    ok = delete_presentation(presentation_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Presentation not found")
    return {"ok": True}


@router.post("/{presentation_id}/export/pptx")
def export(presentation_id: str):
    doc = get_presentation(presentation_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Presentation not found")
    issues = validate_presentation(doc)
    blocking = export_blocking_errors(issues)
    if blocking:
        raise HTTPException(status_code=422, detail={"issues": blocking})
    data = export_to_pptx(doc)
    raw_name = (doc.name or doc.id) + ".pptx"
    ascii_fallback = (doc.id or "presentation") + ".pptx"
    headers = {
        "Content-Disposition": (
            f"attachment; filename=\"{ascii_fallback}\"; "
            f"filename*=UTF-8''{quote(raw_name)}"
        )
    }
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers=headers,
    )

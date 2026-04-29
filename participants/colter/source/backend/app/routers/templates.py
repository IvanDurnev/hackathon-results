from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ..models import TemplateDocument, TemplateSummary
from ..pptx_import import import_pptx_as_template
from ..storage import get_template, list_templates, save_template
from ..validation import validate_template

router = APIRouter(prefix="/api/templates", tags=["templates"])


@router.get("", response_model=list[TemplateSummary])
def index():
    return [
        TemplateSummary(id=t.id, name=t.name, slideSize=t.slideSize)
        for t in list_templates()
    ]


@router.get("/{template_id}", response_model=TemplateDocument)
def show(template_id: str):
    doc = get_template(template_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Template not found")
    return doc


@router.post("", response_model=TemplateDocument)
def create(doc: TemplateDocument):
    issues = validate_template(doc)
    blocking = [i for i in issues if i.get("level") == "error"]
    if blocking:
        raise HTTPException(status_code=422, detail={"issues": blocking})
    return save_template(doc)


@router.put("/{template_id}", response_model=TemplateDocument)
def update(template_id: str, doc: TemplateDocument):
    if doc.id != template_id:
        raise HTTPException(status_code=400, detail="Path id and body id mismatch")
    issues = validate_template(doc)
    blocking = [i for i in issues if i.get("level") == "error"]
    if blocking:
        raise HTTPException(status_code=422, detail={"issues": blocking})
    return save_template(doc)


@router.post("/import/pptx", response_model=TemplateDocument)
async def import_pptx(
    file: UploadFile = File(...),
    name: str | None = Form(None),
):
    filename = (file.filename or "").lower()
    if not filename.endswith(".pptx"):
        raise HTTPException(status_code=400, detail="Файл должен быть .pptx")
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Пустой файл")
    try:
        doc = import_pptx_as_template(
            contents,
            name=name or (file.filename or "").rsplit(".", 1)[0],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Не удалось разобрать PPTX: {exc}",
        ) from exc

    issues = validate_template(doc)
    blocking = [i for i in issues if i.get("level") == "error"]
    if blocking:
        raise HTTPException(status_code=422, detail={"issues": blocking})
    return save_template(doc)

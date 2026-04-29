from fastapi import APIRouter, File, HTTPException, UploadFile

from ..ai_generation import (
    AiApiError,
    build_presentation,
    create_outline,
    get_image_jobs_status,
    regenerate_slide_content,
    regenerate_slide_image,
    retry_outline,
)
from ..ai_models import (
    ImageJobsResponse,
    ImageRegenerateRequest,
    OutlineGenerationRequest,
    OutlineGenerationResponse,
    OutlineRetryRequest,
    PresentationBuildRequest,
    SlideRegenerateRequest,
)
from ..document_extract import extract_text
from ..models import PresentationDocument

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/documents/extract")
async def extract_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Не указано имя файла")
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Пустой файл")
    try:
        text = extract_text(file.filename, file.content_type, contents)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Не удалось извлечь текст: {exc}",
        ) from exc
    return {"fileName": file.filename, "text": text, "length": len(text)}


@router.post("/generations/outline", response_model=OutlineGenerationResponse)
def outline(payload: OutlineGenerationRequest):
    try:
        return create_outline(payload)
    except AiApiError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


@router.post(
    "/generations/{generation_id}/outline/retry",
    response_model=OutlineGenerationResponse,
)
def retry(generation_id: str, payload: OutlineRetryRequest):
    try:
        return retry_outline(generation_id, payload)
    except AiApiError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


@router.post(
    "/generations/{generation_id}/presentation",
    response_model=PresentationDocument,
)
def presentation(generation_id: str, payload: PresentationBuildRequest):
    try:
        return build_presentation(generation_id, payload)
    except AiApiError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


@router.get(
    "/presentations/{presentation_id}/images/status",
    response_model=ImageJobsResponse,
)
def image_status(presentation_id: str):
    return get_image_jobs_status(presentation_id)


@router.post(
    "/presentations/{presentation_id}/slides/{slide_id}/regenerate",
    response_model=PresentationDocument,
)
def regenerate_slide(
    presentation_id: str,
    slide_id: str,
    payload: SlideRegenerateRequest,
):
    try:
        return regenerate_slide_content(presentation_id, slide_id, payload.instructions)
    except AiApiError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


@router.post(
    "/presentations/{presentation_id}/slides/{slide_id}/image/regenerate"
)
def regenerate_image(
    presentation_id: str,
    slide_id: str,
    payload: ImageRegenerateRequest,
):
    try:
        return regenerate_slide_image(
            presentation_id,
            slide_id,
            prompt_override=payload.prompt,
            image_type=payload.imageType,
        )
    except AiApiError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc

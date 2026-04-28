from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from ..models import Asset
from ..storage import asset_path, store_asset

router = APIRouter(prefix="/api/assets", tags=["assets"])


@router.post("", response_model=Asset)
async def upload(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")
    contents = await file.read()
    return store_asset(contents, file.filename, file.content_type or "application/octet-stream")


# served as a sibling /assets/{asset_id}/{file_name} route on the app, see main.py

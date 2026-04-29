from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .routers import ai, assets, presentations, templates
from .seed import seed_if_empty
from .storage import asset_path

app = FastAPI(title="Presentation Editor", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(templates.router)
app.include_router(presentations.router)
app.include_router(assets.router)
app.include_router(ai.router)


@app.on_event("startup")
def _startup() -> None:
    seed_if_empty()


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/assets/{asset_id}/{file_name}")
def serve_asset(asset_id: str, file_name: str):
    p = asset_path(asset_id, file_name)
    if not p:
        raise HTTPException(status_code=404, detail="Asset not found")
    return FileResponse(p)

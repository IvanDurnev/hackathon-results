"""File-based storage for templates, presentations and assets.

The contract is intentionally narrow so we can swap to PostgreSQL later
without changing API responses.
"""

from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path
from typing import Iterable

from .models import Asset, PresentationDocument, TemplateDocument

ROOT = Path(__file__).resolve().parents[1] / "storage"
TEMPLATES_DIR = ROOT / "templates"
PRESENTATIONS_DIR = ROOT / "presentations"
ASSETS_DIR = ROOT / "assets"
GENERATIONS_DIR = ROOT / "generations"
IMAGE_JOBS_DIR = ROOT / "image_jobs"

for _d in (
    TEMPLATES_DIR,
    PRESENTATIONS_DIR,
    ASSETS_DIR,
    GENERATIONS_DIR,
    IMAGE_JOBS_DIR,
):
    _d.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _write_json(path: Path, payload: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    tmp.replace(path)


# --- templates ---------------------------------------------------------------


def list_templates() -> list[TemplateDocument]:
    docs: list[TemplateDocument] = []
    for p in sorted(TEMPLATES_DIR.glob("*.json")):
        try:
            docs.append(TemplateDocument.model_validate(_read_json(p)))
        except Exception:
            continue
    return docs


def get_template(template_id: str) -> TemplateDocument | None:
    p = TEMPLATES_DIR / f"{template_id}.json"
    if not p.exists():
        return None
    return TemplateDocument.model_validate(_read_json(p))


def save_template(doc: TemplateDocument) -> TemplateDocument:
    p = TEMPLATES_DIR / f"{doc.id}.json"
    _write_json(p, doc.model_dump(mode="json", by_alias=True))
    return doc


# --- presentations -----------------------------------------------------------


def list_presentations() -> list[PresentationDocument]:
    docs: list[PresentationDocument] = []
    for p in sorted(PRESENTATIONS_DIR.glob("*.json")):
        try:
            docs.append(PresentationDocument.model_validate(_read_json(p)))
        except Exception:
            continue
    return docs


def get_presentation(presentation_id: str) -> PresentationDocument | None:
    p = PRESENTATIONS_DIR / f"{presentation_id}.json"
    if not p.exists():
        return None
    return PresentationDocument.model_validate(_read_json(p))


def save_presentation(doc: PresentationDocument) -> PresentationDocument:
    p = PRESENTATIONS_DIR / f"{doc.id}.json"
    _write_json(p, doc.model_dump(mode="json", by_alias=True))
    return doc


def delete_presentation(presentation_id: str) -> bool:
    p = PRESENTATIONS_DIR / f"{presentation_id}.json"
    if p.exists():
        p.unlink()
        return True
    return False


# --- ai generation state -----------------------------------------------------


def get_generation(generation_id: str) -> dict | None:
    p = GENERATIONS_DIR / f"{generation_id}.json"
    if not p.exists():
        return None
    return _read_json(p)


def save_generation(generation_id: str, payload: dict) -> dict:
    p = GENERATIONS_DIR / f"{generation_id}.json"
    _write_json(p, payload)
    return payload


# --- image generation jobs ---------------------------------------------------


def get_image_jobs(presentation_id: str) -> dict | None:
    p = IMAGE_JOBS_DIR / f"{presentation_id}.json"
    if not p.exists():
        return None
    return _read_json(p)


def save_image_jobs(presentation_id: str, payload: dict) -> dict:
    p = IMAGE_JOBS_DIR / f"{presentation_id}.json"
    _write_json(p, payload)
    return payload


def delete_image_jobs(presentation_id: str) -> bool:
    p = IMAGE_JOBS_DIR / f"{presentation_id}.json"
    if p.exists():
        p.unlink()
        return True
    return False


# --- assets ------------------------------------------------------------------


def store_asset(file_bytes: bytes, file_name: str, mime_type: str) -> Asset:
    asset_id = f"asset_{uuid.uuid4().hex[:12]}"
    folder = ASSETS_DIR / asset_id
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / file_name
    with target.open("wb") as fh:
        fh.write(file_bytes)
    return Asset(
        id=asset_id,
        type="image" if mime_type.startswith("image/") else "icon",
        mimeType=mime_type,
        url=f"/assets/{asset_id}/{file_name}",
        fileName=file_name,
    )


def asset_path(asset_id: str, file_name: str) -> Path | None:
    p = ASSETS_DIR / asset_id / file_name
    return p if p.exists() else None


def asset_dir(asset_id: str) -> Path | None:
    p = ASSETS_DIR / asset_id
    return p if p.exists() else None

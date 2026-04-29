from pathlib import Path
from uuid import uuid4

from flask import request
from werkzeug.utils import secure_filename

from app.core.errors import ValidationAppError


def json_payload() -> dict:
    payload = request.get_json(silent=True)
    if payload is None:
        return {}
    if not isinstance(payload, dict):
        raise ValidationAppError("JSON-тело запроса должно быть объектом.")
    return payload


def make_stored_filename(original_name: str) -> str:
    safe_name = secure_filename(original_name) or "file"
    suffix = Path(safe_name).suffix
    stem = Path(safe_name).stem[:80] or "file"
    return f"{uuid4().hex}-{stem}{suffix}"


def safe_upload_path(upload_root: str, stored_name: str) -> Path:
    root = Path(upload_root).resolve()
    path = (root / stored_name).resolve()
    if root not in path.parents and path != root:
        raise ValidationAppError("Некорректный путь загрузки.")
    return path

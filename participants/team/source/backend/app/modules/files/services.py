from pathlib import Path

from flask import current_app, request
from werkzeug.datastructures import FileStorage

from app.core.errors import AuthenticationRequired, PermissionDenied, ResourceNotFound, ValidationAppError
from app.core.security import make_stored_filename, safe_upload_path
from app.extensions import db
from app.modules.auth.models import User
from app.modules.files.models import FILE_ACCESS_LEVELS, FILE_ACCESS_PRIVATE, FILE_ACCESS_PUBLIC, FileAsset


def normalize_access_scope(value: str | None) -> str:
    cleaned = (value or FILE_ACCESS_PRIVATE).strip().lower()
    if cleaned not in FILE_ACCESS_LEVELS:
        raise ValidationAppError("Доступ к файлу должен быть public или private.")
    return cleaned


def build_file_url(file_id: int) -> str:
    return f"{request.host_url.rstrip('/')}/api/v1/files/{file_id}"


def file_storage_path(file_asset: FileAsset) -> Path:
    return safe_upload_path(current_app.config["UPLOAD_FOLDER"], file_asset.stored_name)


def get_file_or_404(file_id: int) -> FileAsset:
    file_asset = db.session.get(FileAsset, file_id)
    if file_asset is None:
        raise ResourceNotFound("Файл не найден.")
    return file_asset


def can_access_file(actor: User | None, file_asset: FileAsset) -> bool:
    if file_asset.access_scope == FILE_ACCESS_PUBLIC:
        return True

    if actor is None or not getattr(actor, "is_authenticated", False):
        return False

    return bool(getattr(actor, "is_admin", False) or file_asset.owner_id == actor.id)


def can_manage_file(actor: User | None, file_asset: FileAsset) -> bool:
    if actor is None or not getattr(actor, "is_authenticated", False):
        return False

    return bool(getattr(actor, "is_admin", False) or file_asset.owner_id == actor.id)


def require_file_access(actor: User | None, file_asset: FileAsset) -> None:
    if can_access_file(actor, file_asset):
        return

    if actor is None or not getattr(actor, "is_authenticated", False):
        raise AuthenticationRequired()

    raise PermissionDenied("Нет доступа к выбранному файлу.")


def require_file_management(actor: User | None, file_asset: FileAsset) -> None:
    if can_manage_file(actor, file_asset):
        return

    if actor is None or not getattr(actor, "is_authenticated", False):
        raise AuthenticationRequired()

    raise PermissionDenied("Нет доступа к выбранному файлу.")


def save_uploaded_file(owner: User, upload: FileStorage, *, access_scope: str | None = None) -> FileAsset:
    if upload is None or not upload.filename:
        raise ValidationAppError("Файл не выбран.")

    original_name = Path(upload.filename).name.strip()[:255] or "file"
    stored_name = make_stored_filename(original_name)
    scope = normalize_access_scope(access_scope)

    storage_path = safe_upload_path(current_app.config["UPLOAD_FOLDER"], stored_name)
    storage_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        upload.save(storage_path)
        file_asset = FileAsset(
            owner=owner,
            original_name=original_name,
            stored_name=stored_name,
            mime_type=upload.mimetype or "application/octet-stream",
            size_bytes=storage_path.stat().st_size,
            access_scope=scope,
        )
        db.session.add(file_asset)
        db.session.commit()
        return file_asset
    except Exception:
        db.session.rollback()
        if storage_path.exists():
            storage_path.unlink(missing_ok=True)
        raise


def update_file_access(file_asset: FileAsset, *, access_scope: str) -> FileAsset:
    file_asset.access_scope = normalize_access_scope(access_scope)
    db.session.commit()
    return file_asset


def delete_file_asset(file_asset: FileAsset) -> None:
    storage_path = file_storage_path(file_asset)
    db.session.delete(file_asset)
    db.session.commit()
    try:
        storage_path.unlink(missing_ok=True)
    except OSError:
        pass

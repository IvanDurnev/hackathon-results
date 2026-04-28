from flask import Blueprint, request, send_file
from flask_login import current_user

from app.core.errors import ResourceNotFound
from app.core.permissions import auth_required
from app.core.responses import json_response, message_response
from app.core.security import json_payload
from app.modules.files.schemas import FileAssetResponse, UpdateFileRequest, UploadFileRequest
from app.modules.files.services import (
    delete_file_asset,
    file_storage_path,
    get_file_or_404,
    require_file_access,
    require_file_management,
    save_uploaded_file,
    update_file_access,
)

bp = Blueprint("files", __name__)


@bp.post("")
@auth_required
def upload_file():
    data = UploadFileRequest.model_validate(request.form.to_dict())
    upload = request.files.get("file")
    file_asset = save_uploaded_file(current_user, upload, access_scope=data.access_scope)
    return json_response({"file": FileAssetResponse.from_file(file_asset)}, 201)


@bp.patch("/<int:file_id>")
@auth_required
def change_file_access(file_id: int):
    file_asset = get_file_or_404(file_id)
    require_file_management(current_user, file_asset)
    data = UpdateFileRequest.model_validate(json_payload())
    file_asset = update_file_access(file_asset, access_scope=data.access_scope)
    return json_response({"file": FileAssetResponse.from_file(file_asset)})


@bp.delete("/<int:file_id>")
@auth_required
def delete_file(file_id: int):
    file_asset = get_file_or_404(file_id)
    require_file_management(current_user, file_asset)
    delete_file_asset(file_asset)
    return message_response("File deleted.")


@bp.get("/<int:file_id>")
def download_file(file_id: int):
    file_asset = get_file_or_404(file_id)
    require_file_access(current_user, file_asset)

    storage_path = file_storage_path(file_asset)
    if not storage_path.exists():
        raise ResourceNotFound("Файл не найден.")

    return send_file(
        storage_path,
        mimetype=file_asset.mime_type,
        as_attachment=False,
        download_name=file_asset.original_name,
        conditional=True,
    )

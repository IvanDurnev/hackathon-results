from flask import Blueprint
from flask_login import current_user

from app.core.permissions import auth_required
from app.core.responses import json_response, message_response
from app.core.security import json_payload
from app.modules.auth.schemas import UserResponse
from app.modules.users.schemas import ChangePasswordRequest, UpdateProfileRequest
from app.modules.users.services import change_password, update_profile

bp = Blueprint("users", __name__)


@bp.get("/me")
@auth_required
def profile():
    return json_response({"user": UserResponse.from_user(current_user)})


@bp.patch("/me")
@auth_required
def update_me():
    data = UpdateProfileRequest.model_validate(json_payload())
    avatar_file_id_set = "avatar_file_id" in data.model_fields_set
    user = update_profile(
        current_user,
        username=data.username,
        display_name=data.display_name,
        avatar_file_id=data.avatar_file_id,
        avatar_file_id_set=avatar_file_id_set,
    )
    return json_response({"user": UserResponse.from_user(user)})


@bp.patch("/me/password")
@auth_required
def update_password():
    data = ChangePasswordRequest.model_validate(json_payload())
    change_password(
        current_user,
        current_password=data.current_password,
        new_password=data.new_password,
    )
    return message_response("Password updated.")

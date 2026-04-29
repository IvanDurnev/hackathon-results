from flask import Blueprint
from flask_login import current_user, logout_user

from app.core.permissions import auth_required
from app.core.responses import json_response, message_response
from app.core.security import json_payload
from app.modules.auth.schemas import AuthResponse, LoginRequest, RegisterRequest, UserResponse
from app.modules.auth.services import authenticate_user, create_user, login_existing_user

bp = Blueprint("auth", __name__)


@bp.post("/register")
def register():
    data = RegisterRequest.model_validate(json_payload())
    user = create_user(
        email=data.email,
        username=data.username,
        password=data.password,
        display_name=data.display_name,
    )
    login_existing_user(user)
    return json_response(AuthResponse(user=UserResponse.from_user(user)), 201)


@bp.post("/login")
def login():
    data = LoginRequest.model_validate(json_payload())
    user = authenticate_user(data.email, data.password)
    login_existing_user(user)
    return json_response(AuthResponse(user=UserResponse.from_user(user)))


@bp.post("/logout")
@auth_required
def logout():
    logout_user()
    return message_response("Logged out.")


@bp.get("/me")
@auth_required
def me():
    return json_response({"user": UserResponse.from_user(current_user)})

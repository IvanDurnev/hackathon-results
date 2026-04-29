from flask import Blueprint, request
from flask_login import current_user

from app.core.pagination import pagination_args, pagination_meta
from app.core.permissions import admin_required
from app.core.responses import json_response, paginated_response
from app.core.security import json_payload
from app.modules.admin.queries import dashboard_metrics, list_users
from app.modules.admin.schemas import AdminCreateUserRequest, AdminUpdateUserRequest
from app.modules.admin.services import (
    create_managed_user,
    delete_user_account,
    get_user_or_404,
    update_user_account,
)
from app.modules.auth.schemas import UserResponse

bp = Blueprint("admin", __name__)


@bp.get("/dashboard")
@admin_required
def dashboard():
    return json_response({"metrics": dashboard_metrics()})


@bp.get("/users")
@admin_required
def users_index():
    page, per_page = pagination_args()
    pagination = list_users(page=page, per_page=per_page, query=request.args.get("q"))
    return paginated_response(
        [UserResponse.from_user(user) for user in pagination.items],
        pagination_meta(pagination),
    )


@bp.post("/users")
@admin_required
def users_create():
    data = AdminCreateUserRequest.model_validate(json_payload())
    user = create_managed_user(
        email=str(data.email),
        username=data.username,
        password=data.password,
        display_name=data.display_name,
        active=data.active,
        is_admin=data.is_admin,
    )
    return json_response({"user": UserResponse.from_user(user)}, 201)


@bp.patch("/users/<int:user_id>")
@admin_required
def users_update(user_id: int):
    target = get_user_or_404(user_id)
    data = AdminUpdateUserRequest.model_validate(json_payload())
    user = update_user_account(current_user, target, data.model_dump(exclude_unset=True))
    return json_response({"user": UserResponse.from_user(user)})


@bp.delete("/users/<int:user_id>")
@admin_required
def users_delete(user_id: int):
    target = get_user_or_404(user_id)
    delete_user_account(current_user, target)
    return json_response({"message": "User deleted."})

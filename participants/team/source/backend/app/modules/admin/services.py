from app.core.errors import ConflictError, PermissionDenied, ResourceNotFound
from app.extensions import db
from app.modules.admin.policies import can_change_user_active, can_change_user_admin, can_delete_user
from app.modules.auth.models import Role, User
from app.modules.auth.services import create_user, ensure_default_roles, normalize_email


def get_user_or_404(user_id: int) -> User:
    user = db.session.get(User, user_id)
    if user is None:
        raise ResourceNotFound("Пользователь не найден.")
    return user


def create_managed_user(
    *,
    email: str,
    username: str,
    password: str,
    display_name: str | None,
    active: bool,
    is_admin: bool,
) -> User:
    return create_user(
        email=email,
        username=username,
        password=password,
        display_name=display_name,
        active=active,
        is_admin=is_admin,
    )


def update_user_flags(
    actor: User,
    target: User,
    *,
    active: bool | None,
    is_admin: bool | None,
) -> User:
    if active is not None:
        if not can_change_user_active(actor, target, active):
            raise PermissionDenied("Администратор не может отключить собственный аккаунт.")
        target.active = active

    if is_admin is not None:
        if not can_change_user_admin(actor, target, is_admin):
            raise PermissionDenied("Администратор не может снять собственную роль администратора.")
        roles = ensure_default_roles()
        admin_role: Role = roles["admin"]
        if is_admin:
            target.add_role(admin_role)
        else:
            target.remove_role("admin")

    db.session.commit()
    return target


def update_user_account(actor: User, target: User, changes: dict) -> User:
    if "email" in changes and changes["email"] is not None:
        normalized_email = normalize_email(str(changes["email"]))
        existing = User.query.filter_by(email=normalized_email).first()
        if existing is not None and existing.id != target.id:
            raise ConflictError("Почта уже зарегистрирована.", {"email": "taken"})
        target.email = normalized_email

    if "username" in changes and changes["username"] is not None:
        username = str(changes["username"]).strip()
        existing = User.query.filter_by(username=username).first()
        if existing is not None and existing.id != target.id:
            raise ConflictError("Имя пользователя уже занято.", {"username": "taken"})
        target.username = username

    if "display_name" in changes:
        value = changes["display_name"]
        if isinstance(value, str):
            target.display_name = value.strip()

    if "password" in changes and changes["password"]:
        target.set_password(changes["password"])

    if "active" in changes:
        active = changes["active"]
        if active is not None:
            if not can_change_user_active(actor, target, active):
                raise PermissionDenied("Администратор не может отключить собственный аккаунт.")
            target.active = active

    if "is_admin" in changes:
        is_admin = changes["is_admin"]
        if is_admin is not None:
            if not can_change_user_admin(actor, target, is_admin):
                raise PermissionDenied("Администратор не может снять собственную роль администратора.")
            roles = ensure_default_roles()
            admin_role: Role = roles["admin"]
            if is_admin:
                target.add_role(admin_role)
            else:
                target.remove_role("admin")

    db.session.commit()
    return target


def delete_user_account(actor: User, target: User) -> None:
    if not can_delete_user(actor, target):
        raise PermissionDenied("Администратор не может удалить собственный аккаунт.")
    db.session.delete(target)
    db.session.commit()

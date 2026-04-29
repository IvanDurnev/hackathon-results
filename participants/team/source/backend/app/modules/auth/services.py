from flask_login import login_user
from pydantic import EmailStr, TypeAdapter, ValidationError

from app.core.errors import AuthenticationRequired, ConflictError, PermissionDenied, ValidationAppError
from app.extensions import db
from app.modules.auth.models import Role, User
from app.modules.auth.policies import can_login


DEFAULT_ROLES = {
    "user": "Обычный авторизованный пользователь.",
    "admin": "Может управлять пользователями и системными данными.",
}
EMAIL_ADAPTER = TypeAdapter(EmailStr)


def normalize_email(email: str) -> str:
    try:
        return str(EMAIL_ADAPTER.validate_python(email.strip())).lower()
    except ValidationError as error:
        raise ValidationAppError("Некорректная почта.", {"email": "invalid"}) from error


def ensure_default_roles() -> dict[str, Role]:
    roles: dict[str, Role] = {}
    for name, description in DEFAULT_ROLES.items():
        role = Role.query.filter_by(name=name).first()
        if role is None:
            role = Role(name=name, description=description)
            db.session.add(role)
            db.session.flush()
        roles[name] = role
    return roles


def create_user(
    email: str,
    username: str,
    password: str,
    *,
    display_name: str | None = None,
    active: bool = True,
    is_admin: bool = False,
) -> User:
    normalized_email = normalize_email(email)
    normalized_username = username.strip()
    normalized_display_name = (
        display_name.strip()
        if isinstance(display_name, str) and display_name.strip()
        else normalized_username
    )

    if User.query.filter_by(email=normalized_email).first():
        raise ConflictError("Почта уже зарегистрирована.", {"email": "taken"})
    if User.query.filter_by(username=normalized_username).first():
        raise ConflictError("Имя пользователя уже занято.", {"username": "taken"})

    roles = ensure_default_roles()
    user = User(
        email=normalized_email,
        username=normalized_username,
        display_name=normalized_display_name,
        active=active,
    )
    user.set_password(password)
    user.add_role(roles["user"])
    if is_admin:
        user.add_role(roles["admin"])

    db.session.add(user)
    db.session.commit()
    return user


def authenticate_user(identifier: str, password: str) -> User:
    cleaned_identifier = identifier.strip()
    user = User.query.filter(
        (User.email == cleaned_identifier.lower()) | (User.username == cleaned_identifier)
    ).first()
    if user is None or not user.check_password(password):
        raise AuthenticationRequired("Неверная почта или пароль.")
    if not can_login(user):
        raise PermissionDenied("Отключенный пользователь не может войти.")
    return user


def login_existing_user(user: User, remember: bool = False) -> User:
    login_user(user, remember=remember)
    return user

from functools import wraps

from flask_login import current_user

from app.core.errors import AuthenticationRequired, PermissionDenied


def require_auth() -> None:
    if not current_user.is_authenticated:
        raise AuthenticationRequired()


def require_admin() -> None:
    require_auth()
    if not current_user.is_admin:
        raise PermissionDenied("Требуется доступ администратора.")


def auth_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        require_auth()
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        require_admin()
        return view(*args, **kwargs)

    return wrapped

from app.modules.auth.models import User


def can_login(user: User) -> bool:
    return user.active

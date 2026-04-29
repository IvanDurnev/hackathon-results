from app.modules.auth.models import User


def can_manage_users(actor: User) -> bool:
    return actor.is_admin


def can_change_user_active(actor: User, target: User, active: bool) -> bool:
    if actor.id == target.id and active is False:
        return False
    return actor.is_admin


def can_change_user_admin(actor: User, target: User, is_admin: bool) -> bool:
    if actor.id == target.id and is_admin is False:
        return False
    return actor.is_admin


def can_delete_user(actor: User, target: User) -> bool:
    if actor.id == target.id:
        return False
    return actor.is_admin

from sqlalchemy import func, or_

from app.extensions import db
from app.modules.auth.models import Role, User, user_roles


ROLE_SEARCH_ALIASES = {
    "админ": "admin",
    "администратор": "admin",
    "admin": "admin",
    "administrator": "admin",
    "пользователь": "user",
    "user": "user",
}


def _searchable_role_names(query: str) -> set[str]:
    normalized = query.strip().casefold()
    role_names: set[str] = set()

    if not normalized:
        return role_names

    for alias, role_name in ROLE_SEARCH_ALIASES.items():
        if alias in normalized or normalized in alias:
            role_names.add(role_name)

    return role_names


def list_users(*, page: int, per_page: int, query: str | None = None):
    statement = User.query.order_by(User.created_at.desc())
    if query:
        cleaned_query = query.strip()
        like = f"%{cleaned_query}%"
        role_names = _searchable_role_names(cleaned_query)
        conditions = [
            User.email.ilike(like),
            User.username.ilike(like),
            User.display_name.ilike(like),
            User.roles.any(Role.name.ilike(like)),
            User.roles.any(Role.description.ilike(like)),
        ]
        conditions.extend(User.roles.any(Role.name == role_name) for role_name in role_names)
        statement = statement.filter(or_(*conditions))
    return statement.paginate(page=page, per_page=per_page, error_out=False)


def dashboard_metrics() -> dict[str, int]:
    admin_role = Role.query.filter_by(name="admin").first()
    admin_users = 0
    if admin_role is not None:
        admin_users = (
            db.session.query(func.count(User.id))
            .join(user_roles, User.id == user_roles.c.user_id)
            .filter(user_roles.c.role_id == admin_role.id)
            .scalar()
            or 0
        )

    return {
        "users": db.session.scalar(db.select(func.count(User.id))) or 0,
        "admins": admin_users,
        "active": db.session.scalar(db.select(func.count(User.id)).where(User.active.is_(True))) or 0,
        "inactive": db.session.scalar(db.select(func.count(User.id)).where(User.active.is_(False))) or 0,
    }

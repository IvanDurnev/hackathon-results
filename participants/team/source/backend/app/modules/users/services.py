from app.core.errors import ConflictError, PermissionDenied, ResourceNotFound
from app.extensions import db
from app.modules.auth.models import User
from app.modules.files.models import FILE_ACCESS_PUBLIC, FileAsset
from app.modules.files.services import can_access_file, delete_file_asset


def update_profile(
    user: User,
    *,
    username: str | None,
    display_name: str | None,
    avatar_file_id: int | None = None,
    avatar_file_id_set: bool = False,
) -> User:
    previous_avatar = user.avatar_file

    if username and username != user.username:
        existing = User.query.filter_by(username=username).first()
        if existing is not None:
            raise ConflictError("Имя пользователя уже занято.", {"username": "taken"})
        user.username = username

    if display_name is not None:
        user.display_name = display_name.strip()

    if avatar_file_id_set:
        if avatar_file_id is None:
            user.avatar_file_id = None
        else:
            avatar_file = db.session.get(FileAsset, avatar_file_id)
            if avatar_file is None:
                raise ResourceNotFound("Файл не найден.")
            if not can_access_file(user, avatar_file):
                raise PermissionDenied("Нет доступа к выбранному файлу.")
            if avatar_file.access_scope != FILE_ACCESS_PUBLIC:
                avatar_file.access_scope = FILE_ACCESS_PUBLIC
            user.avatar_file_id = avatar_file.id
    elif user.avatar_file and user.avatar_file.access_scope != FILE_ACCESS_PUBLIC:
        user.avatar_file.access_scope = FILE_ACCESS_PUBLIC

    db.session.commit()
    if previous_avatar is not None and previous_avatar.id != user.avatar_file_id:
        delete_file_asset(previous_avatar)
    return user


def change_password(user: User, *, current_password: str, new_password: str) -> None:
    if not user.check_password(current_password):
        raise PermissionDenied("Текущий пароль неверный.")
    user.set_password(new_password)
    db.session.commit()

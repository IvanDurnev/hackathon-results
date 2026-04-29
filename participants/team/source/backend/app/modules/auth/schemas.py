from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.modules.auth.models import User
from app.modules.files.schemas import FileAssetResponse


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    username: str
    display_name: str | None = None
    active: bool
    roles: list[str]
    avatar: FileAssetResponse | None = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_user(cls, user: User) -> "UserResponse":
        return cls(
            id=user.id,
            email=user.email,
            username=user.username,
            display_name=user.display_name,
            active=user.active,
            roles=[role.name for role in user.roles],
            avatar=FileAssetResponse.from_file(user.avatar_file) if user.avatar_file else None,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=1, max_length=120)

    @field_validator("username")
    @classmethod
    def username_is_clean(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Имя пользователя обязательно.")
        return cleaned

    @field_validator("display_name")
    @classmethod
    def display_name_is_clean(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Отображаемое имя обязательно.")
        return cleaned


class LoginRequest(BaseModel):
    email: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def identifier_is_not_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Почта или имя пользователя обязательны.")
        return cleaned


class AuthResponse(BaseModel):
    user: UserResponse

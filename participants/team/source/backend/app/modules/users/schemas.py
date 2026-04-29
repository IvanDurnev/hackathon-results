from pydantic import BaseModel, Field, field_validator


class UpdateProfileRequest(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=80)
    display_name: str = Field(min_length=1, max_length=120)
    avatar_file_id: int | None = Field(default=None, ge=1)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Имя пользователя не может быть пустым.")
        return cleaned

    @field_validator("display_name")
    @classmethod
    def normalize_display_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Отображаемое имя обязательно.")
        return cleaned


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)

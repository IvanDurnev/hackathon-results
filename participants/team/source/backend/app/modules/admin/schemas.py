from pydantic import BaseModel, EmailStr, Field, field_validator


class AdminCreateUserRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=1, max_length=120)
    active: bool = True
    is_admin: bool = False

    @field_validator("username")
    @classmethod
    def username_is_not_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Имя пользователя обязательно.")
        return cleaned

    @field_validator("display_name")
    @classmethod
    def display_name_is_not_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Отображаемое имя обязательно.")
        return cleaned


class AdminUpdateUserRequest(BaseModel):
    email: EmailStr | None = None
    username: str | None = Field(default=None, min_length=3, max_length=80)
    display_name: str | None = Field(default=None, max_length=120)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    active: bool | None = None
    is_admin: bool | None = None

    @field_validator("username")
    @classmethod
    def optional_username_is_not_blank(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Имя пользователя обязательно.")
        return cleaned

    @field_validator("display_name")
    @classmethod
    def optional_display_name_is_not_blank(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Отображаемое имя обязательно.")
        return cleaned

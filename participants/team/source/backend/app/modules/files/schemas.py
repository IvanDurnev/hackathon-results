from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.files.models import FILE_ACCESS_LEVELS, FILE_ACCESS_PRIVATE, FileAsset
from app.modules.files.services import build_file_url


class FileAssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_name: str
    mime_type: str
    size_bytes: int
    access_scope: str
    url: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_file(cls, file: FileAsset) -> "FileAssetResponse":
        return cls(
            id=file.id,
            original_name=file.original_name,
            mime_type=file.mime_type,
            size_bytes=file.size_bytes,
            access_scope=file.access_scope,
            url=build_file_url(file.id),
            created_at=file.created_at,
            updated_at=file.updated_at,
        )


class FileAccessRequest(BaseModel):
    access_scope: str = Field(default=FILE_ACCESS_PRIVATE)

    @field_validator("access_scope", mode="before")
    @classmethod
    def normalize_access_scope(cls, value):
        if value is None or value == "":
            return FILE_ACCESS_PRIVATE

        cleaned = str(value).strip().lower()
        if cleaned not in FILE_ACCESS_LEVELS:
            raise ValueError("Доступ к файлу должен быть public или private.")
        return cleaned


class UploadFileRequest(FileAccessRequest):
    pass


class UpdateFileRequest(FileAccessRequest):
    pass


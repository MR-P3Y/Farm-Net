from pydantic import BaseModel, Field


class StoredMediaFile(BaseModel):
    file_key: str
    original_filename: str
    stored_filename: str
    relative_path: str
    storage_disk: str
    mime_type: str
    extension: str
    size_bytes: int
    checksum_sha256: str
    width: int | None = None
    height: int | None = None


class MediaFileOut(BaseModel):
    id: int
    owner_user_id: int | None = None

    file_key: str
    original_filename: str
    stored_filename: str
    relative_path: str
    storage_disk: str

    mime_type: str
    extension: str
    size_bytes: int
    checksum_sha256: str

    visibility: str
    status: str
    purpose: str

    width: int | None = None
    height: int | None = None
    alt_text: str | None = None
    description: str | None = None

    created_at: str
    updated_at: str
    deleted_at: str | None = None


class MediaUploadMetaIn(BaseModel):
    purpose: str = Field(default="general", min_length=2, max_length=80)
    visibility: str = Field(default="private", min_length=2, max_length=30)
    alt_text: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=2000)


class AdminMediaStatusUpdateIn(BaseModel):
    status: str = Field(min_length=3, max_length=30)
    description: str | None = Field(default=None, max_length=2000)

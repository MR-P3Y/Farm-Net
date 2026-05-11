from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator


class ProfileMeOut(BaseModel):
    id: int | None = None
    user_id: int

    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None

    national_id: str | None = None
    birth_date: date | None = None
    gender: str | None = None

    province_id: int | None = None
    county_id: int | None = None
    district_id: int | None = None
    rural_district_id: int | None = None
    city_id: int | None = None
    village_id: int | None = None

    address: str | None = None
    postal_code: str | None = None

    avatar_file_id: str | None = None
    bio: str | None = None

    profile_completed: bool = False


class ProfileUpdateIn(BaseModel):
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    display_name: str | None = Field(default=None, max_length=150)

    national_id: str | None = Field(default=None, max_length=20)
    birth_date: date | None = None
    gender: str | None = Field(default=None, max_length=30)

    province_id: int | None = Field(default=None, ge=1)
    county_id: int | None = Field(default=None, ge=1)
    district_id: int | None = Field(default=None, ge=1)
    rural_district_id: int | None = Field(default=None, ge=1)
    city_id: int | None = Field(default=None, ge=1)
    village_id: int | None = Field(default=None, ge=1)

    address: str | None = Field(default=None, max_length=2000)
    postal_code: str | None = Field(default=None, max_length=20)

    avatar_file_id: str | None = Field(default=None, max_length=255)
    bio: str | None = Field(default=None, max_length=2000)

    @field_validator(
        "first_name",
        "last_name",
        "display_name",
        "national_id",
        "gender",
        "address",
        "postal_code",
        "avatar_file_id",
        "bio",
        mode="before",
    )
    @classmethod
    def empty_string_to_none(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class DocumentCreateIn(BaseModel):
    document_type: str = Field(max_length=80)
    file_path: str = Field(min_length=1, max_length=500)
    file_name: str = Field(min_length=1, max_length=255)
    mime_type: str | None = Field(default=None, max_length=150)
    size_bytes: int | None = Field(default=None, ge=1)

    @field_validator(
        "document_type",
        "file_path",
        "file_name",
        "mime_type",
        mode="before",
    )
    @classmethod
    def normalize_document_strings(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class DocumentOut(BaseModel):
    id: int
    user_id: int
    document_type: str
    file_path: str
    file_name: str
    mime_type: str | None = None
    size_bytes: int | None = None
    status: str
    uploaded_at: datetime
    reviewed_at: datetime | None = None
    reviewed_by: int | None = None
    reject_reason: str | None = None
    created_at: datetime
    updated_at: datetime

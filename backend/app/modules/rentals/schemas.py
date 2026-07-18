from datetime import datetime

from pydantic import BaseModel, Field, field_validator


def _strip(value):
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


class RentalCategoryCreateIn(BaseModel):
    parent_id: int | None = Field(default=None, ge=1)
    code: str = Field(min_length=2, max_length=100, pattern=r"^[a-z0-9_]+$")
    title: str = Field(min_length=2, max_length=180)
    description: str | None = Field(default=None, max_length=2000)
    sort_order: int = Field(default=100, ge=0)
    is_active: bool = True

    _normalize = field_validator("code", "title", "description", mode="before")(_strip)


class RentalCategoryUpdateIn(BaseModel):
    parent_id: int | None = Field(default=None, ge=1)
    code: str | None = Field(default=None, min_length=2, max_length=100, pattern=r"^[a-z0-9_]+$")
    title: str | None = Field(default=None, min_length=2, max_length=180)
    description: str | None = Field(default=None, max_length=2000)
    sort_order: int | None = Field(default=None, ge=0)
    is_active: bool | None = None

    _normalize = field_validator("code", "title", "description", mode="before")(_strip)


class RentalCategoryOut(BaseModel):
    id: int
    parent_id: int | None
    code: str
    title: str
    description: str | None
    sort_order: int
    is_active: bool
    children_count: int = 0
    equipment_count: int = 0
    created_at: datetime
    updated_at: datetime


class LessorProfileInput(BaseModel):
    display_name: str | None = Field(default=None, max_length=150)
    bio: str | None = Field(default=None, max_length=4000)
    phone: str | None = Field(default=None, max_length=30)
    province_id: int | None = Field(default=None, ge=1)
    city_id: int | None = Field(default=None, ge=1)
    address_text: str | None = Field(default=None, max_length=2000)
    avatar_media_file_id: int | None = Field(default=None, ge=1)

    _normalize = field_validator("display_name", "bio", "phone", "address_text", mode="before")(
        _strip
    )


class LessorProfileStatusIn(BaseModel):
    status: str
    admin_note: str | None = Field(default=None, max_length=2000)

    _normalize = field_validator("status", "admin_note", mode="before")(_strip)


class LessorProfileOut(BaseModel):
    id: int
    user_id: int
    display_name: str | None
    bio: str | None
    phone: str | None
    province_id: int | None
    city_id: int | None
    address_text: str | None
    avatar_media_file_id: int | None
    status: str
    admin_note: str | None
    equipment_count: int = 0
    submitted_at: datetime | None
    approved_at: datetime | None
    approved_by: int | None
    created_at: datetime
    updated_at: datetime

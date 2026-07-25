from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator

from app.modules.farms.enums import FarmStatus


def _normalize_required(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError("Value cannot be blank")
    return normalized


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    return value.strip() or None


class FarmCreateIn(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    description: str | None = Field(default=None, max_length=5000)

    _name = field_validator("name")(_normalize_required)
    _description = field_validator("description")(_normalize_optional)


class FarmUpdateIn(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=180)
    description: str | None = Field(default=None, max_length=5000)

    _name = field_validator("name")(_normalize_required)
    _description = field_validator("description")(_normalize_optional)

    @model_validator(mode="after")
    def require_explicit_field(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


class FarmArchiveIn(BaseModel):
    reason: str | None = Field(default=None, max_length=500)

    _reason = field_validator("reason")(_normalize_optional)


class FarmOwnerOut(BaseModel):
    id: int
    name: str
    description: str | None
    status: FarmStatus
    archived_at: datetime | None
    archive_reason: str | None
    can_edit: bool
    can_archive: bool
    can_restore: bool
    created_at: datetime
    updated_at: datetime


class FarmOwnerDetailResponse(BaseModel):
    success: bool
    data: FarmOwnerOut
    message: str
    meta: dict


class FarmOwnerListResponse(BaseModel):
    success: bool
    data: list[FarmOwnerOut]
    message: str
    meta: dict

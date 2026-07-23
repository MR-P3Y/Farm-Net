from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.modules.reviews.enums import ReviewSourceType, ReviewSubjectType


class ReviewCreateIn(BaseModel):
    source_type: ReviewSourceType
    source_id: int = Field(ge=1)
    subject_type: ReviewSubjectType
    subject_id: int = Field(ge=1)
    score: int = Field(ge=1, le=5)
    body: str | None = Field(default=None, max_length=2000)

    @field_validator("body")
    @classmethod
    def normalize_body(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class ReviewUpdateIn(BaseModel):
    score: int | None = Field(default=None, ge=1, le=5)
    body: str | None = Field(default=None, max_length=2000)

    @field_validator("body")
    @classmethod
    def normalize_body(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class ReviewOwnerOut(BaseModel):
    id: int
    source_type: str
    source_id: int
    subject_type: str
    subject_id: int
    score: int
    body: str | None = None
    status: str
    can_edit: bool
    can_delete: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class ReviewOwnerListResponse(BaseModel):
    success: bool
    data: list[ReviewOwnerOut]
    message: str
    meta: dict


class ReviewOwnerDetailResponse(BaseModel):
    success: bool
    data: ReviewOwnerOut
    message: str
    meta: dict

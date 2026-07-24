from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.modules.reviews.enums import (
    ReviewReportReason,
    ReviewReportStatus,
    ReviewSourceType,
    ReviewStatus,
    ReviewSubjectType,
)


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


class ReviewPublicAuthorOut(BaseModel):
    display_name: str


class ReviewPublicOut(BaseModel):
    id: int
    score: int
    body: str | None = None
    author: ReviewPublicAuthorOut
    created_at: datetime
    updated_at: datetime


class RatingSummaryOut(BaseModel):
    subject_type: str
    subject_id: int
    rating_average: Decimal
    reviews_count: int


class ReviewPublicListResponse(BaseModel):
    success: bool
    data: list[ReviewPublicOut]
    message: str
    meta: dict


class ReviewReportCreateIn(BaseModel):
    reason: ReviewReportReason
    description: str | None = Field(default=None, max_length=2000)

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None


class ReviewReportOwnerOut(BaseModel):
    id: int
    review_id: int
    reason: str
    description: str | None
    status: str
    created_at: datetime


class ReviewReportDetailResponse(BaseModel):
    success: bool
    data: ReviewReportOwnerOut
    message: str
    meta: dict


class ReviewModerationIn(BaseModel):
    status: ReviewStatus
    note: str = Field(min_length=2, max_length=2000)


class ReviewReportResolutionIn(BaseModel):
    status: ReviewReportStatus
    resolution_note: str = Field(min_length=2, max_length=2000)


class ReviewAdminOut(BaseModel):
    id: int
    reviewer_user_id: int
    source_type: str
    source_id: int
    subject_type: str
    subject_id: int
    score: int
    body: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    model_config = {"from_attributes": True}


class ReviewReportAdminOut(BaseModel):
    id: int
    review_id: int
    reporter_user_id: int
    reason: str
    description: str | None
    status: str
    reviewed_by_user_id: int | None
    resolution_note: str | None
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReviewModerationLogOut(BaseModel):
    id: int
    review_id: int
    actor_user_id: int | None
    report_id: int | None
    action: str
    from_status: str | None
    to_status: str | None
    note: str | None
    event_key: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewAdminListResponse(BaseModel):
    success: bool
    data: list[ReviewAdminOut]
    message: str
    meta: dict


class ReviewAdminDetailResponse(BaseModel):
    success: bool
    data: ReviewAdminOut
    message: str
    meta: dict


class ReviewReportAdminListResponse(BaseModel):
    success: bool
    data: list[ReviewReportAdminOut]
    message: str
    meta: dict


class ReviewReportAdminDetailResponse(BaseModel):
    success: bool
    data: ReviewReportAdminOut
    message: str
    meta: dict


class ReviewModerationLogListResponse(BaseModel):
    success: bool
    data: list[ReviewModerationLogOut]
    message: str
    meta: dict

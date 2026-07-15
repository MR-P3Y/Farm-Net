from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.modules.consultants.schemas import ConsultSpecialtyOut


class ExpertAnswerCreateIn(BaseModel):
    body: str = Field(min_length=3, max_length=8000)


class ExpertAnswerModerationIn(BaseModel):
    reason: str | None = Field(default=None, max_length=500)


class ExpertAnswerStatusUpdateIn(BaseModel):
    status: str = Field(min_length=2, max_length=40)


class ExpertAnswerOut(BaseModel):
    id: int

    post_id: int
    expert_user_id: int

    body: str
    status: str

    is_accepted: bool
    accepted_at: datetime | None = None
    accepted_by_user_id: int | None = None

    helpful_count: int
    reports_count: int

    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = {"from_attributes": True}


class ExpertAnswerConsultantOut(BaseModel):
    consultant_id: int
    user_id: int
    display_name: str | None = None
    name: str | None = None
    title: str | None = None
    avatar_file_id: str | None = None
    avatar_media_file_id: int | None = None
    avatar_url: str | None = None
    status: str
    is_verified: bool
    verification_status: str
    is_featured: bool
    rating_average: float
    reviews_count: int
    specialties: list[ConsultSpecialtyOut] = Field(default_factory=list)


class ExpertAnswerPublicOut(ExpertAnswerOut):
    answer_id: int
    expert_id: int
    consultant: ExpertAnswerConsultantOut | None = None


class ExpertAnswerAdminOut(BaseModel):
    answer_id: int
    post_id: int
    expert_id: int
    expert_user_id: int

    body: str
    status: str

    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    post_title: str | None = None
    post_preview: str | None = None
    consultant: ExpertAnswerConsultantOut | None = None

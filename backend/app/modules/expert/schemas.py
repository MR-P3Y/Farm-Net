from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ExpertAnswerCreateIn(BaseModel):
    body: str = Field(min_length=3, max_length=8000)


class ExpertAnswerModerationIn(BaseModel):
    reason: str | None = Field(default=None, max_length=500)


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

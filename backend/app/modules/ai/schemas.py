from datetime import datetime

from pydantic import BaseModel, Field


class AIConversationCreateIn(BaseModel):
    title: str | None = Field(default=None, max_length=180)

    model_config = {"extra": "forbid"}


class AIRequestCreateIn(BaseModel):
    idempotency_key: str = Field(min_length=8, max_length=180)
    content: str = Field(min_length=1, max_length=12000)
    feature_code: str = Field(
        default="ai.text_chat",
        pattern="^(ai\\.text_chat|ai\\.farm_context|ai\\.deep_analysis|"
        "ai\\.image_analysis|ai\\.smart_diary|ai\\.report_export)$",
    )
    request_kind: str = Field(
        default="text",
        pattern="^(text|farm_context|deep_analysis|image_analysis|smart_diary|report)$",
    )

    model_config = {"extra": "forbid"}


class AIMessageOut(BaseModel):
    id: int
    request_id: int | None
    role: str
    content: str
    safety_label: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AIRequestOut(BaseModel):
    id: int
    conversation_id: int
    feature_code: str
    request_kind: str
    status: str
    failure_code: str | None
    safety_code: str | None
    requested_at: datetime
    started_at: datetime | None
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class AIConversationOut(BaseModel):
    id: int
    title: str | None
    status: str
    retention_until: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AIConversationDetailOut(AIConversationOut):
    messages: list[AIMessageOut]


class AIConversationResponse(BaseModel):
    success: bool
    data: AIConversationOut
    message: str
    meta: dict


class AIConversationDetailResponse(BaseModel):
    success: bool
    data: AIConversationDetailOut
    message: str
    meta: dict


class AIConversationListResponse(BaseModel):
    success: bool
    data: list[AIConversationOut]
    message: str
    meta: dict


class AIRequestResponse(BaseModel):
    success: bool
    data: AIRequestOut
    message: str
    meta: dict

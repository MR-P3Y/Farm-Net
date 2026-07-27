from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class AIAdminOverviewOut(BaseModel):
    total_requests: int
    queued_requests: int
    running_requests: int
    succeeded_requests: int
    failed_requests: int
    blocked_requests: int
    total_input_tokens: int
    total_output_tokens: int
    total_provider_cost_toman: Decimal
    pending_knowledge_sources: int
    negative_feedback: int
    reconciliation_issues: int


class AIAdminRequestOut(BaseModel):
    id: int
    user_id: int
    feature_code: str
    request_kind: str
    status: str
    processing_priority: str
    prompt_policy_version: str
    routing_policy_version: str
    failure_code: str | None
    safety_code: str | None
    attempt_count: int
    requested_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class AIAdminUsageOut(BaseModel):
    id: int
    request_id: int
    provider_key: str
    model_key: str
    input_tokens: int
    output_tokens: int
    cached_input_tokens: int
    provider_cost_amount: Decimal | None
    provider_cost_currency: str | None
    latency_ms: int
    recorded_at: datetime

    model_config = {"from_attributes": True}


class AIAdminFeedbackOut(BaseModel):
    id: int
    request_id: int
    rating: str
    reason_codes: list | None
    comment: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AIAdminKnowledgeSourceCreateIn(BaseModel):
    code: str = Field(min_length=3, max_length=100, pattern=r"^[a-z0-9][a-z0-9._-]+$")
    title: str = Field(min_length=3, max_length=250)
    publisher: str = Field(min_length=2, max_length=250)
    source_url: str | None = Field(default=None, max_length=1000)
    license_code: str = Field(min_length=2, max_length=80)
    license_evidence: str = Field(min_length=3, max_length=1000)

    model_config = {"extra": "forbid"}


class AIAdminKnowledgeReviewIn(BaseModel):
    decision: str = Field(pattern="^(approved|rejected)$")
    reason: str = Field(min_length=3, max_length=1000)

    model_config = {"extra": "forbid"}


class AIAdminKnowledgeSourceOut(BaseModel):
    id: int
    code: str
    title: str
    publisher: str
    source_url: str | None
    license_code: str
    license_evidence: str
    status: str
    reviewed_by_user_id: int | None
    review_reason: str | None
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AIAdminAuditOut(BaseModel):
    id: int
    action: str
    target_type: str
    target_id: int
    actor_type: str
    actor_user_id: int | None
    request_id: int | None
    safe_metadata: dict | None
    trace_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AIAdminPolicyOut(BaseModel):
    id: int
    policy_key: str
    version: str
    request_kind: str
    status: str
    active_scope: str | None
    activated_at: datetime | None

    model_config = {"from_attributes": True}


class AIAdminModelOut(BaseModel):
    id: int
    provider_key: str
    model_key: str
    model_version: str
    capabilities: dict
    timeout_seconds: int
    max_output_tokens: int
    reasoning_effort: str
    input_cost_per_million_toman: Decimal | None
    cached_input_cost_per_million_toman: Decimal | None
    output_cost_per_million_toman: Decimal | None
    enabled: bool

    model_config = {"from_attributes": True}

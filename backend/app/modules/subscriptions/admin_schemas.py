from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.modules.subscriptions.schemas import FeatureUsageOut, PlanOut


class AdminPlanFeatureIn(BaseModel):
    feature_code: str = Field(min_length=1, max_length=120)
    enabled: bool = True
    unlimited: bool = False
    boolean_value: bool | None = None
    numeric_value: Decimal | None = Field(default=None, ge=0)
    string_value: str | None = Field(default=None, max_length=500)
    json_value: dict[str, Any] | list[Any] | None = None

    model_config = {"extra": "forbid"}


class AdminPlanCreateIn(BaseModel):
    code: str = Field(pattern=r"^[a-z][a-z0-9_]{1,79}$")
    name: str = Field(min_length=2, max_length=160)
    description: str | None = Field(default=None, max_length=4000)
    billing_period: str = Field(pattern="^(free|monthly|yearly|custom)$")
    duration_days: int | None = Field(default=None, ge=1, le=3660)
    price_toman: Decimal = Field(ge=0, max_digits=18, decimal_places=2)
    effective_from: datetime | None = None
    effective_until: datetime | None = None
    features: list[AdminPlanFeatureIn] = Field(min_length=1, max_length=200)

    model_config = {"extra": "forbid"}

    @field_validator("code", mode="before")
    @classmethod
    def normalize_code(cls, value: object) -> object:
        return value.strip().lower() if isinstance(value, str) else value


class AdminPlanUpdateIn(BaseModel):
    expected_version: int = Field(ge=1)
    name: str | None = Field(default=None, min_length=2, max_length=160)
    description: str | None = Field(default=None, max_length=4000)
    billing_period: str | None = Field(default=None, pattern="^(free|monthly|yearly|custom)$")
    duration_days: int | None = Field(default=None, ge=1, le=3660)
    price_toman: Decimal | None = Field(default=None, ge=0, max_digits=18, decimal_places=2)
    effective_from: datetime | None = None
    effective_until: datetime | None = None
    features: list[AdminPlanFeatureIn] | None = Field(default=None, min_length=1, max_length=200)

    model_config = {"extra": "forbid"}


class AdminPlanStatusIn(BaseModel):
    expected_version: int = Field(ge=1)
    status: str = Field(pattern="^(active|retired)$")

    model_config = {"extra": "forbid"}


class AdminManualActivateIn(BaseModel):
    user_id: int = Field(ge=1)
    plan_id: int = Field(ge=1)
    reason: str = Field(min_length=3, max_length=500)

    model_config = {"extra": "forbid"}


class AdminSubscriptionCancelIn(BaseModel):
    expected_version: int = Field(ge=1)
    reason: str = Field(min_length=3, max_length=500)
    cancel_at_period_end: bool = True

    model_config = {"extra": "forbid"}


class AdminPlanOut(PlanOut):
    status: str
    effective_from: datetime | None
    effective_until: datetime | None
    created_at: datetime
    updated_at: datetime


class AdminSubscriptionSummaryOut(BaseModel):
    id: int
    user_id: int
    user_label: str
    status: str
    plan_id: int
    plan_code: str
    plan_name: str
    price_toman: Decimal
    currency: str
    starts_at: datetime | None
    current_period_ends_at: datetime | None
    grace_ends_at: datetime | None
    auto_renew: bool
    cancel_at_period_end: bool
    activation_source: str
    activated_by_user_id: int | None
    activation_reason: str | None
    version: int
    created_at: datetime


class AdminSubscriptionDetailOut(AdminSubscriptionSummaryOut):
    current_period_starts_at: datetime | None
    cancelled_at: datetime | None
    ended_at: datetime | None
    cancellation_reason: str | None
    usage: list[FeatureUsageOut]


class AdminPageMeta(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int
    trace_id: str


class AdminPlanListResponse(BaseModel):
    success: bool
    data: list[AdminPlanOut]
    message: str
    meta: AdminPageMeta


class AdminPlanResponse(BaseModel):
    success: bool
    data: AdminPlanOut
    message: str
    meta: dict


class AdminSubscriptionListResponse(BaseModel):
    success: bool
    data: list[AdminSubscriptionSummaryOut]
    message: str
    meta: AdminPageMeta


class AdminSubscriptionResponse(BaseModel):
    success: bool
    data: AdminSubscriptionDetailOut
    message: str
    meta: dict

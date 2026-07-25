from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class PlanFeatureOut(BaseModel):
    code: str
    name: str
    module: str
    value_kind: str
    unit: str | None
    enabled: bool
    unlimited: bool
    value: bool | int | Decimal | str | dict | list | None


class PlanOut(BaseModel):
    id: int
    code: str
    name: str
    description: str | None
    billing_period: str
    duration_days: int | None
    price_toman: Decimal
    currency: str
    version: int
    is_default_free: bool
    features: list[PlanFeatureOut]


class SubscriptionOut(BaseModel):
    id: int
    status: str
    plan: PlanOut
    starts_at: datetime | None
    current_period_starts_at: datetime | None
    current_period_ends_at: datetime | None
    grace_ends_at: datetime | None
    auto_renew: bool
    cancel_at_period_end: bool
    version: int


class SubscriptionCancelIn(BaseModel):
    expected_version: int = Field(ge=1)
    cancel_at_period_end: bool = True
    reason: str = Field(min_length=3, max_length=500)


class SubscriptionResumeIn(BaseModel):
    expected_version: int = Field(ge=1)


class EntitlementOut(BaseModel):
    code: str
    enabled: bool
    unlimited: bool
    limit_value: Decimal | None
    policy_value: dict | list | None
    source: str
    starts_at: datetime
    ends_at: datetime


class FeatureUsageOut(BaseModel):
    code: str
    used_value: Decimal
    reserved_value: Decimal
    limit_value: Decimal | None
    unlimited: bool
    remaining_value: Decimal | None
    period_ends_at: datetime


class QuotaEstimateIn(BaseModel):
    feature_code: str = Field(min_length=1, max_length=120)
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=4)


class QuotaEstimateOut(BaseModel):
    feature_code: str
    requested_value: Decimal
    used_value: Decimal
    reserved_value: Decimal
    limit_value: Decimal | None
    unlimited: bool
    remaining_before: Decimal | None
    remaining_after: Decimal | None
    allowed: bool


class QuotaReservationOut(BaseModel):
    id: int
    feature_code: str
    amount: Decimal
    status: str
    expires_at: datetime
    finalized_at: datetime | None
    released_at: datetime | None


class PlanListResponse(BaseModel):
    success: bool
    data: list[PlanOut]
    message: str
    meta: dict


class PlanDetailResponse(BaseModel):
    success: bool
    data: PlanOut
    message: str
    meta: dict


class OwnSubscriptionResponse(BaseModel):
    success: bool
    data: SubscriptionOut | None
    message: str
    meta: dict


class EntitlementListResponse(BaseModel):
    success: bool
    data: list[EntitlementOut]
    message: str
    meta: dict


class UsageListResponse(BaseModel):
    success: bool
    data: list[FeatureUsageOut]
    message: str
    meta: dict


class QuotaEstimateResponse(BaseModel):
    success: bool
    data: QuotaEstimateOut
    message: str
    meta: dict

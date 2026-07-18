from datetime import datetime
from decimal import Decimal

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


class RentalEquipmentMediaIn(BaseModel):
    media_file_id: int = Field(ge=1)
    sort_order: int = Field(default=0, ge=0)
    is_primary: bool = False
    alt_text: str | None = Field(default=None, max_length=255)

    _normalize = field_validator("alt_text", mode="before")(_strip)


class RentalEquipmentMediaOut(BaseModel):
    id: int
    media_file_id: int
    file_key: str | None = None
    public_url: str | None = None
    sort_order: int
    is_primary: bool
    alt_text: str | None


class RentalEquipmentInput(BaseModel):
    category_id: int | None = Field(default=None, ge=1)
    title: str = Field(min_length=2, max_length=220)
    slug: str = Field(min_length=3, max_length=180)
    description: str | None = Field(default=None, max_length=8000)
    manufacturer: str | None = Field(default=None, max_length=120)
    model_name: str | None = Field(default=None, max_length=120)
    production_year: int | None = Field(default=None, ge=1950, le=2200)
    operator_mode: str = "without_operator"
    province_id: int | None = Field(default=None, ge=1)
    city_id: int | None = Field(default=None, ge=1)
    address_text: str | None = Field(default=None, max_length=2000)
    delivery_available: bool = False
    delivery_terms: str | None = Field(default=None, max_length=3000)
    security_deposit_amount: float | None = Field(default=None, ge=0)
    currency: str = Field(default="TOMAN", min_length=3, max_length=10)
    is_active: bool = True
    media_items: list[RentalEquipmentMediaIn] = Field(default_factory=list, max_length=20)

    _normalize = field_validator(
        "title",
        "slug",
        "description",
        "manufacturer",
        "model_name",
        "address_text",
        "delivery_terms",
        mode="before",
    )(_strip)


class RentalEquipmentStatusIn(BaseModel):
    status: str
    admin_note: str | None = Field(default=None, max_length=2000)

    _normalize = field_validator("status", "admin_note", mode="before")(_strip)


class RentalEquipmentOut(BaseModel):
    id: int
    lessor_profile_id: int
    category_id: int | None
    title: str
    slug: str
    description: str | None
    manufacturer: str | None
    model_name: str | None
    production_year: int | None
    operator_mode: str
    status: str
    province_id: int | None
    city_id: int | None
    address_text: str | None
    delivery_available: bool
    delivery_terms: str | None
    security_deposit_amount: float | None
    currency: str
    is_active: bool
    media: list[RentalEquipmentMediaOut] = Field(default_factory=list)
    category: RentalCategoryOut | None = None
    lessor_display_name: str | None = None
    admin_note: str | None = None
    submitted_at: datetime | None
    approved_at: datetime | None
    approved_by: int | None
    created_at: datetime
    updated_at: datetime


class RentalEquipmentPublicOut(BaseModel):
    id: int
    lessor_profile_id: int
    category_id: int | None
    title: str
    slug: str
    description: str | None
    manufacturer: str | None
    model_name: str | None
    production_year: int | None
    operator_mode: str
    province_id: int | None
    city_id: int | None
    delivery_available: bool
    delivery_terms: str | None
    security_deposit_amount: float | None
    currency: str
    media: list[RentalEquipmentMediaOut]
    category: RentalCategoryOut | None
    lessor_display_name: str | None


class RentalPricingRuleIn(BaseModel):
    unit: str
    operator_included: bool = False
    price_amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    minimum_units: Decimal = Field(default=Decimal("1"), gt=0, max_digits=10, decimal_places=2)
    currency: str = Field(default="TOMAN", min_length=3, max_length=10)
    is_active: bool = True

    _normalize = field_validator("unit", "currency", mode="before")(_strip)


class RentalPricingRuleOut(BaseModel):
    id: int
    equipment_id: int
    unit: str
    operator_included: bool
    price_amount: Decimal
    minimum_units: Decimal
    currency: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RentalAvailabilityBlockIn(BaseModel):
    block_type: str
    starts_at: datetime
    ends_at: datetime
    note: str | None = Field(default=None, max_length=2000)

    _normalize = field_validator("block_type", "note", mode="before")(_strip)


class RentalAvailabilityBlockOut(BaseModel):
    id: int
    equipment_id: int
    block_type: str
    starts_at: datetime
    ends_at: datetime
    note: str | None
    created_at: datetime


class RentalAvailabilityCheckOut(BaseModel):
    equipment_id: int
    starts_at: datetime
    ends_at: datetime
    is_available: bool
    conflicting_blocks: list[RentalAvailabilityBlockOut] = Field(default_factory=list)


class RentalRequestCreateIn(BaseModel):
    equipment_id: int = Field(ge=1)
    pricing_rule_id: int = Field(ge=1)
    starts_at: datetime
    ends_at: datetime
    requested_units: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    operator_requested: bool = False
    delivery_address: str | None = Field(default=None, max_length=2000)
    requester_note: str | None = Field(default=None, max_length=3000)

    _normalize = field_validator("delivery_address", "requester_note", mode="before")(_strip)


class RentalRequestCancelIn(BaseModel):
    reason: str = Field(min_length=2, max_length=2000)

    _normalize = field_validator("reason", mode="before")(_strip)


class RentalRequestStatusIn(BaseModel):
    status: str
    note: str | None = Field(default=None, max_length=2000)

    _normalize = field_validator("status", "note", mode="before")(_strip)


class RentalRequestStatusLogOut(BaseModel):
    id: int
    changed_by: int | None
    from_status: str | None
    to_status: str
    note: str | None
    created_at: datetime


class RentalRequestListOut(BaseModel):
    id: int
    requester_user_id: int
    lessor_profile_id: int
    equipment_id: int
    pricing_rule_id: int
    equipment_title: str
    lessor_display_name: str | None
    starts_at: datetime
    ends_at: datetime
    requested_units: Decimal
    operator_requested: bool
    status: str
    price_per_unit_snapshot: Decimal | None
    rental_amount_snapshot: Decimal | None
    deposit_amount_snapshot: Decimal | None
    total_amount_snapshot: Decimal | None
    currency: str
    created_at: datetime
    updated_at: datetime


class RentalRequestDetailOut(RentalRequestListOut):
    delivery_address: str | None
    requester_note: str | None
    lessor_note: str | None
    cancel_reason: str | None
    accepted_at: datetime | None
    completed_at: datetime | None
    cancelled_at: datetime | None
    status_logs: list[RentalRequestStatusLogOut] = Field(default_factory=list)


class RentalRequestAdminDetailOut(RentalRequestDetailOut):
    admin_note: str | None

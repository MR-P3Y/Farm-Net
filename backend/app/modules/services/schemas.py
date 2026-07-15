from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class ServiceCategoryCreateIn(BaseModel):
    parent_id: int | None = Field(default=None, ge=1)
    code: str = Field(min_length=2, max_length=100)
    title: str = Field(min_length=2, max_length=180)
    description: str | None = Field(default=None, max_length=2000)
    sort_order: int = Field(default=100, ge=0)
    is_active: bool = True

    @field_validator("code", "title", "description", mode="before")
    @classmethod
    def normalize_strings(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class ServiceCategoryUpdateIn(BaseModel):
    parent_id: int | None = Field(default=None, ge=1)
    code: str | None = Field(default=None, min_length=2, max_length=100)
    title: str | None = Field(default=None, min_length=2, max_length=180)
    description: str | None = Field(default=None, max_length=2000)
    sort_order: int | None = Field(default=None, ge=0)
    is_active: bool | None = None

    @field_validator("code", "title", "description", mode="before")
    @classmethod
    def normalize_strings(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class ServiceCategoryOut(BaseModel):
    id: int
    parent_id: int | None = None
    code: str
    title: str
    description: str | None = None
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ServiceProviderProfileCreateIn(BaseModel):
    display_name: str | None = Field(default=None, max_length=150)
    title: str | None = Field(default=None, max_length=180)
    bio: str | None = Field(default=None, max_length=4000)
    experience_years: int | None = Field(default=None, ge=0, le=80)
    phone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=255)
    province_id: int | None = Field(default=None, ge=1)
    city_id: int | None = Field(default=None, ge=1)
    village_id: int | None = Field(default=None, ge=1)
    province_name: str | None = Field(default=None, max_length=120)
    city_name: str | None = Field(default=None, max_length=120)
    village_name: str | None = Field(default=None, max_length=120)
    service_area: str | None = Field(default=None, max_length=255)
    avatar_file_id: str | None = Field(default=None, max_length=255)
    avatar_media_file_id: int | None = Field(default=None, ge=1)
    category_ids: list[int] = Field(default_factory=list, max_length=20)

    @field_validator(
        "display_name",
        "title",
        "bio",
        "phone",
        "email",
        "province_name",
        "city_name",
        "village_name",
        "service_area",
        "avatar_file_id",
        mode="before",
    )
    @classmethod
    def normalize_strings(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class ServiceProviderProfileUpdateIn(ServiceProviderProfileCreateIn):
    pass


class ServiceProviderProfileStatusUpdateIn(BaseModel):
    status: str = Field(min_length=3, max_length=50)
    note: str | None = Field(default=None, max_length=2000)

    @field_validator("status", "note", mode="before")
    @classmethod
    def normalize_strings(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class ServiceProviderProfileOut(BaseModel):
    id: int
    user_id: int
    display_name: str | None = None
    name: str | None = None
    title: str | None = None
    bio: str | None = None
    experience_years: int | None = None
    phone: str | None = None
    email: str | None = None
    province_id: int | None = None
    city_id: int | None = None
    village_id: int | None = None
    province_name: str | None = None
    city_name: str | None = None
    village_name: str | None = None
    service_area: str | None = None
    avatar_file_id: str | None = None
    avatar_media_file_id: int | None = None
    avatar_url: str | None = None
    status: str
    is_verified: bool
    verification_status: str
    is_featured: bool
    rating_average: Decimal
    reviews_count: int
    requests_count: int
    completed_requests_count: int
    categories: list[ServiceCategoryOut] = Field(default_factory=list)
    admin_note: str | None = None
    submitted_at: datetime | None = None
    approved_at: datetime | None = None
    approved_by: int | None = None
    rejected_at: datetime | None = None
    rejected_by: int | None = None
    suspended_at: datetime | None = None
    suspended_by: int | None = None
    created_at: datetime
    updated_at: datetime


class ServiceProviderProfilePublicOut(BaseModel):
    id: int
    user_id: int
    display_name: str | None = None
    name: str | None = None
    title: str | None = None
    bio: str | None = None
    experience_years: int | None = None
    province_id: int | None = None
    city_id: int | None = None
    village_id: int | None = None
    province_name: str | None = None
    city_name: str | None = None
    village_name: str | None = None
    service_area: str | None = None
    avatar_file_id: str | None = None
    avatar_media_file_id: int | None = None
    avatar_url: str | None = None
    status: str
    is_verified: bool
    verification_status: str
    is_featured: bool
    rating_average: Decimal
    reviews_count: int
    requests_count: int
    completed_requests_count: int
    categories: list[ServiceCategoryOut] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class ServiceOfferMediaIn(BaseModel):
    file_id: str | None = Field(default=None, max_length=255)
    media_file_id: int | None = Field(default=None, ge=1)
    file_path: str | None = Field(default=None, min_length=3, max_length=1000)
    alt_text: str | None = Field(default=None, max_length=255)
    sort_order: int = Field(default=0, ge=0)
    is_primary: bool = False

    @field_validator("file_id", "file_path", "alt_text", mode="before")
    @classmethod
    def normalize_strings(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class ServiceOfferCreateIn(BaseModel):
    category_id: int | None = Field(default=None, ge=1)
    title: str = Field(min_length=2, max_length=220)
    slug: str = Field(min_length=3, max_length=160)
    short_description: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, max_length=10000)
    pricing_type: str = Field(default="negotiable", min_length=2, max_length=40)
    price_amount: Decimal | None = Field(default=None, ge=0)
    currency: str = Field(default="TOMAN", min_length=2, max_length=10)
    province_id: int | None = Field(default=None, ge=1)
    city_id: int | None = Field(default=None, ge=1)
    village_id: int | None = Field(default=None, ge=1)
    province_name: str | None = Field(default=None, max_length=120)
    city_name: str | None = Field(default=None, max_length=120)
    village_name: str | None = Field(default=None, max_length=120)
    service_area: str | None = Field(default=None, max_length=255)
    latitude: str | None = Field(default=None, max_length=40)
    longitude: str | None = Field(default=None, max_length=40)
    is_active: bool = True
    media_items: list[ServiceOfferMediaIn] = Field(default_factory=list, max_length=20)

    @field_validator(
        "title",
        "slug",
        "short_description",
        "description",
        "pricing_type",
        "currency",
        "province_name",
        "city_name",
        "village_name",
        "service_area",
        "latitude",
        "longitude",
        mode="before",
    )
    @classmethod
    def normalize_strings(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class ServiceOfferUpdateIn(BaseModel):
    category_id: int | None = Field(default=None, ge=1)
    title: str | None = Field(default=None, min_length=2, max_length=220)
    slug: str | None = Field(default=None, min_length=3, max_length=160)
    short_description: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, max_length=10000)
    pricing_type: str | None = Field(default=None, min_length=2, max_length=40)
    price_amount: Decimal | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, min_length=2, max_length=10)
    province_id: int | None = Field(default=None, ge=1)
    city_id: int | None = Field(default=None, ge=1)
    village_id: int | None = Field(default=None, ge=1)
    province_name: str | None = Field(default=None, max_length=120)
    city_name: str | None = Field(default=None, max_length=120)
    village_name: str | None = Field(default=None, max_length=120)
    service_area: str | None = Field(default=None, max_length=255)
    latitude: str | None = Field(default=None, max_length=40)
    longitude: str | None = Field(default=None, max_length=40)
    is_active: bool | None = None
    media_items: list[ServiceOfferMediaIn] | None = Field(default=None, max_length=20)

    @field_validator(
        "title",
        "slug",
        "short_description",
        "description",
        "pricing_type",
        "currency",
        "province_name",
        "city_name",
        "village_name",
        "service_area",
        "latitude",
        "longitude",
        mode="before",
    )
    @classmethod
    def normalize_strings(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class ServiceOfferStatusUpdateIn(BaseModel):
    status: str = Field(min_length=3, max_length=50)
    note: str | None = Field(default=None, max_length=2000)

    @field_validator("status", "note", mode="before")
    @classmethod
    def normalize_strings(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class ServiceOfferMediaOut(BaseModel):
    id: int
    offer_id: int
    file_id: str | None = None
    media_file_id: int | None = None
    file_key: str | None = None
    public_url: str | None = None
    file_path: str | None = None
    alt_text: str | None = None
    sort_order: int
    is_primary: bool
    created_at: datetime
    updated_at: datetime


class ServiceOfferOut(BaseModel):
    id: int
    provider_profile_id: int
    category_id: int | None = None
    title: str
    slug: str
    short_description: str | None = None
    description: str | None = None
    status: str
    pricing_type: str
    price_amount: Decimal | None = None
    currency: str
    province_id: int | None = None
    city_id: int | None = None
    village_id: int | None = None
    province_name: str | None = None
    city_name: str | None = None
    village_name: str | None = None
    service_area: str | None = None
    latitude: str | None = None
    longitude: str | None = None
    is_active: bool
    is_featured: bool
    views_count: int
    requests_count: int
    completed_requests_count: int
    media: list[ServiceOfferMediaOut] = Field(default_factory=list)
    primary_media: ServiceOfferMediaOut | None = None
    category: ServiceCategoryOut | None = None
    provider: ServiceProviderProfilePublicOut | None = None
    admin_note: str | None = None
    submitted_at: datetime | None = None
    approved_at: datetime | None = None
    approved_by: int | None = None
    rejected_at: datetime | None = None
    rejected_by: int | None = None
    suspended_at: datetime | None = None
    suspended_by: int | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class ServiceOfferPublicOut(BaseModel):
    id: int
    provider_profile_id: int
    category_id: int | None = None
    title: str
    slug: str
    short_description: str | None = None
    description: str | None = None
    status: str
    pricing_type: str
    price_amount: Decimal | None = None
    currency: str
    province_id: int | None = None
    city_id: int | None = None
    village_id: int | None = None
    province_name: str | None = None
    city_name: str | None = None
    village_name: str | None = None
    service_area: str | None = None
    latitude: str | None = None
    longitude: str | None = None
    is_active: bool
    is_featured: bool
    views_count: int
    requests_count: int
    completed_requests_count: int
    media: list[ServiceOfferMediaOut] = Field(default_factory=list)
    primary_media: ServiceOfferMediaOut | None = None
    category: ServiceCategoryOut | None = None
    provider: ServiceProviderProfilePublicOut | None = None
    created_at: datetime
    updated_at: datetime


class ServiceRequestCreateIn(BaseModel):
    offer_id: int = Field(ge=1)
    title: str = Field(min_length=2, max_length=255)
    description: str = Field(min_length=5, max_length=10000)
    contact_method: str = Field(default="in_app", min_length=2, max_length=40)
    budget_amount: Decimal | None = Field(default=None, ge=0)
    currency: str = Field(default="TOMAN", min_length=2, max_length=10)
    scheduled_at: datetime | None = None
    province_id: int | None = Field(default=None, ge=1)
    city_id: int | None = Field(default=None, ge=1)
    village_id: int | None = Field(default=None, ge=1)
    province_name: str | None = Field(default=None, max_length=120)
    city_name: str | None = Field(default=None, max_length=120)
    village_name: str | None = Field(default=None, max_length=120)
    address_text: str | None = Field(default=None, max_length=2000)
    latitude: str | None = Field(default=None, max_length=40)
    longitude: str | None = Field(default=None, max_length=40)

    model_config = {"extra": "forbid"}

    @field_validator(
        "title",
        "description",
        "contact_method",
        "currency",
        "province_name",
        "city_name",
        "village_name",
        "address_text",
        "latitude",
        "longitude",
        mode="before",
    )
    @classmethod
    def normalize_strings(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class ServiceRequestStatusUpdateIn(BaseModel):
    status: str = Field(min_length=3, max_length=50)
    note: str | None = Field(default=None, max_length=2000)

    model_config = {"extra": "forbid"}

    @field_validator("status", "note", mode="before")
    @classmethod
    def normalize_strings(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class ServiceRequestCancelIn(BaseModel):
    reason: str | None = Field(default=None, max_length=2000)

    model_config = {"extra": "forbid"}

    @field_validator("reason", mode="before")
    @classmethod
    def normalize_reason(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class ServiceRequestStatusLogOut(BaseModel):
    id: int
    request_id: int
    changed_by: int | None = None
    from_status: str | None = None
    to_status: str
    note: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ServiceRequestOut(BaseModel):
    id: int
    requester_user_id: int
    provider_profile_id: int | None = None
    offer_id: int | None = None
    category_id: int | None = None
    title: str
    description: str
    contact_method: str
    status: str
    budget_amount: Decimal | None = None
    currency: str
    scheduled_at: datetime | None = None
    province_id: int | None = None
    city_id: int | None = None
    village_id: int | None = None
    province_name: str | None = None
    city_name: str | None = None
    village_name: str | None = None
    accepted_at: datetime | None = None
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ServiceRequestDetailOut(ServiceRequestOut):
    address_text: str | None = None
    latitude: str | None = None
    longitude: str | None = None
    provider_note: str | None = None
    admin_note: str | None = None
    cancel_reason: str | None = None
    status_logs: list[ServiceRequestStatusLogOut] = Field(default_factory=list)

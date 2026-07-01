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

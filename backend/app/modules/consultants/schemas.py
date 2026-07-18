from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class ConsultSpecialtyCreateIn(BaseModel):
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


class ConsultSpecialtyUpdateIn(BaseModel):
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


class ConsultSpecialtyOut(BaseModel):
    id: int
    code: str
    title: str
    description: str | None = None
    sort_order: int
    is_active: bool
    profiles_count: int = 0
    requests_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConsultProfileCreateIn(BaseModel):
    display_name: str | None = Field(default=None, max_length=150)
    title: str | None = Field(default=None, max_length=180)
    bio: str | None = Field(default=None, max_length=4000)
    experience_years: int | None = Field(default=None, ge=0, le=80)
    phone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=255)
    province_id: int | None = Field(default=None, ge=1)
    city_id: int | None = Field(default=None, ge=1)
    province_name: str | None = Field(default=None, max_length=120)
    city_name: str | None = Field(default=None, max_length=120)
    avatar_file_id: str | None = Field(default=None, max_length=255)
    avatar_media_file_id: int | None = Field(default=None, ge=1)
    specialty_ids: list[int] = Field(default_factory=list, max_length=20)

    @field_validator(
        "display_name",
        "title",
        "bio",
        "phone",
        "email",
        "province_name",
        "city_name",
        "avatar_file_id",
        mode="before",
    )
    @classmethod
    def normalize_strings(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class ConsultProfileUpdateIn(ConsultProfileCreateIn):
    pass


class ConsultProfileStatusUpdateIn(BaseModel):
    status: str = Field(min_length=3, max_length=50)
    note: str | None = Field(default=None, max_length=2000)

    @field_validator("status", "note", mode="before")
    @classmethod
    def normalize_strings(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class ConsultProfileOut(BaseModel):
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
    province_name: str | None = None
    city_name: str | None = None
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
    specialties: list[ConsultSpecialtyOut] = Field(default_factory=list)
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


class ConsultProfilePublicOut(BaseModel):
    id: int
    user_id: int
    display_name: str | None = None
    name: str | None = None
    title: str | None = None
    bio: str | None = None
    experience_years: int | None = None
    province_id: int | None = None
    city_id: int | None = None
    province_name: str | None = None
    city_name: str | None = None
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
    specialties: list[ConsultSpecialtyOut] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class ConsultRequestCreateIn(BaseModel):
    consultant_profile_id: int | None = Field(default=None, ge=1)
    specialty_id: int | None = Field(default=None, ge=1)
    title: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=10, max_length=8000)
    contact_method: str = Field(default="in_app", min_length=2, max_length=40)
    budget_amount: Decimal | None = Field(default=None, ge=0)
    currency: str = Field(default="IRR", min_length=2, max_length=10)
    scheduled_at: datetime | None = None

    @field_validator("title", "description", "contact_method", "currency", mode="before")
    @classmethod
    def normalize_strings(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class ConsultRequestStatusUpdateIn(BaseModel):
    status: str = Field(min_length=3, max_length=50)
    note: str | None = Field(default=None, max_length=2000)

    @field_validator("status", "note", mode="before")
    @classmethod
    def normalize_strings(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class ConsultRequestStatusLogOut(BaseModel):
    id: int
    request_id: int
    changed_by: int | None = None
    from_status: str | None = None
    to_status: str
    note: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConsultRequestOut(BaseModel):
    id: int
    requester_user_id: int
    consultant_profile_id: int | None = None
    specialty_id: int | None = None
    title: str
    description: str
    contact_method: str
    status: str
    budget_amount: Decimal | None = None
    currency: str
    scheduled_at: datetime | None = None
    admin_note: str | None = None
    consultant_note: str | None = None
    cancel_reason: str | None = None
    accepted_at: datetime | None = None
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    consultant: ConsultProfileOut | None = None
    specialty: ConsultSpecialtyOut | None = None
    status_logs: list[ConsultRequestStatusLogOut] = Field(default_factory=list)

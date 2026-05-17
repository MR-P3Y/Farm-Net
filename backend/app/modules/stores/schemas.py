from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class StoreCreateIn(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    slug: str = Field(min_length=3, max_length=120)
    description: str | None = Field(default=None, max_length=5000)

    store_type: str = Field(default="other", max_length=80)

    phone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=255)

    province_id: int | None = Field(default=None, ge=1)
    county_id: int | None = Field(default=None, ge=1)
    district_id: int | None = Field(default=None, ge=1)
    city_id: int | None = Field(default=None, ge=1)
    village_id: int | None = Field(default=None, ge=1)

    address: str | None = Field(default=None, max_length=3000)
    postal_code: str | None = Field(default=None, max_length=20)

    latitude: Decimal | None = None
    longitude: Decimal | None = None

    logo_file_id: str | None = Field(default=None, max_length=255)
    banner_file_id: str | None = Field(default=None, max_length=255)

    @field_validator(
        "name",
        "slug",
        "description",
        "store_type",
        "phone",
        "email",
        "address",
        "postal_code",
        "logo_file_id",
        "banner_file_id",
        mode="before",
    )
    @classmethod
    def normalize_strings(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class StoreUpdateIn(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=180)
    slug: str | None = Field(default=None, min_length=3, max_length=120)
    description: str | None = Field(default=None, max_length=5000)

    store_type: str | None = Field(default=None, max_length=80)

    phone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=255)

    province_id: int | None = Field(default=None, ge=1)
    county_id: int | None = Field(default=None, ge=1)
    district_id: int | None = Field(default=None, ge=1)
    city_id: int | None = Field(default=None, ge=1)
    village_id: int | None = Field(default=None, ge=1)

    address: str | None = Field(default=None, max_length=3000)
    postal_code: str | None = Field(default=None, max_length=20)

    latitude: Decimal | None = None
    longitude: Decimal | None = None

    logo_file_id: str | None = Field(default=None, max_length=255)
    banner_file_id: str | None = Field(default=None, max_length=255)

    @field_validator(
        "name",
        "slug",
        "description",
        "store_type",
        "phone",
        "email",
        "address",
        "postal_code",
        "logo_file_id",
        "banner_file_id",
        mode="before",
    )
    @classmethod
    def normalize_strings(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class StoreOut(BaseModel):
    id: int
    owner_user_id: int

    name: str
    slug: str
    description: str | None = None

    status: str
    store_type: str

    phone: str | None = None
    email: str | None = None

    province_id: int | None = None
    county_id: int | None = None
    district_id: int | None = None
    city_id: int | None = None
    village_id: int | None = None

    address: str | None = None
    postal_code: str | None = None

    latitude: Decimal | None = None
    longitude: Decimal | None = None

    logo_file_id: str | None = None
    banner_file_id: str | None = None

    admin_note: str | None = None

    approved_at: str | None = None
    approved_by: int | None = None
    rejected_at: str | None = None
    rejected_by: int | None = None

    created_at: str
    updated_at: str


class StoreStatusHistoryOut(BaseModel):
    id: int
    store_id: int
    changed_by: int | None = None
    from_status: str | None = None
    to_status: str
    note: str | None = None
    created_at: str

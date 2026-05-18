from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class ProductCreateIn(BaseModel):
    category_id: int | None = Field(default=None, ge=1)

    name: str = Field(min_length=2, max_length=220)
    slug: str = Field(min_length=3, max_length=160)

    short_description: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, max_length=10000)

    sku: str | None = Field(default=None, max_length=120)

    price: Decimal = Field(gt=0)
    compare_at_price: Decimal | None = Field(default=None, gt=0)
    currency: str = Field(default="TOMAN", max_length=10)

    stock_quantity: int = Field(default=0, ge=0)
    unit: str = Field(default="piece", max_length=30)

    min_order_quantity: int = Field(default=1, ge=1)
    max_order_quantity: int | None = Field(default=None, ge=1)

    is_active: bool = True
    is_featured: bool = False

    @field_validator(
        "name",
        "slug",
        "short_description",
        "description",
        "sku",
        "currency",
        "unit",
        mode="before",
    )
    @classmethod
    def normalize_strings(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class ProductUpdateIn(BaseModel):
    category_id: int | None = Field(default=None, ge=1)

    name: str | None = Field(default=None, min_length=2, max_length=220)
    slug: str | None = Field(default=None, min_length=3, max_length=160)

    short_description: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, max_length=10000)

    sku: str | None = Field(default=None, max_length=120)

    price: Decimal | None = Field(default=None, gt=0)
    compare_at_price: Decimal | None = Field(default=None, gt=0)
    currency: str | None = Field(default=None, max_length=10)

    stock_quantity: int | None = Field(default=None, ge=0)
    unit: str | None = Field(default=None, max_length=30)

    min_order_quantity: int | None = Field(default=None, ge=1)
    max_order_quantity: int | None = Field(default=None, ge=1)

    is_active: bool | None = None
    is_featured: bool | None = None

    @field_validator(
        "name",
        "slug",
        "short_description",
        "description",
        "sku",
        "currency",
        "unit",
        mode="before",
    )
    @classmethod
    def normalize_strings(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class ProductOut(BaseModel):
    id: int
    store_id: int
    category_id: int | None = None

    name: str
    slug: str

    short_description: str | None = None
    description: str | None = None

    sku: str | None = None

    status: str

    price: Decimal
    compare_at_price: Decimal | None = None
    currency: str

    stock_quantity: int
    unit: str

    min_order_quantity: int
    max_order_quantity: int | None = None

    is_active: bool
    is_featured: bool

    admin_note: str | None = None

    suspended_at: str | None = None
    suspended_by: int | None = None

    created_at: str
    updated_at: str


class ProductStatusHistoryOut(BaseModel):
    id: int
    product_id: int
    changed_by: int | None = None
    from_status: str | None = None
    to_status: str
    note: str | None = None
    created_at: str


class ProductImageCreateIn(BaseModel):
    file_id: str | None = Field(default=None, max_length=255)
    file_path: str = Field(min_length=3, max_length=1000)
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


class ProductImageUpdateIn(BaseModel):
    file_id: str | None = Field(default=None, max_length=255)
    file_path: str | None = Field(default=None, min_length=3, max_length=1000)
    alt_text: str | None = Field(default=None, max_length=255)

    sort_order: int | None = Field(default=None, ge=0)
    is_primary: bool | None = None

    @field_validator("file_id", "file_path", "alt_text", mode="before")
    @classmethod
    def normalize_strings(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class ProductImageOut(BaseModel):
    id: int
    product_id: int

    file_id: str | None = None
    file_path: str
    alt_text: str | None = None

    sort_order: int
    is_primary: bool

    created_at: str
    updated_at: str

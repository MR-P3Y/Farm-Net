from decimal import Decimal

from pydantic import BaseModel, Field


class CartItemAddIn(BaseModel):
    product_id: int = Field(ge=1)
    quantity: int = Field(default=1, ge=1)


class CartItemUpdateIn(BaseModel):
    quantity: int = Field(ge=1)


class CartItemOut(BaseModel):
    id: int
    cart_id: int

    product_id: int
    store_id: int

    quantity: int
    unit_price: Decimal
    line_total: Decimal

    product_name_snapshot: str
    product_slug_snapshot: str
    product_sku_snapshot: str | None = None
    unit_snapshot: str

    created_at: str
    updated_at: str


class CartOut(BaseModel):
    id: int
    user_id: int
    status: str
    currency: str

    items: list[CartItemOut]

    items_count: int
    subtotal_amount: Decimal

    created_at: str
    updated_at: str
    checked_out_at: str | None = None

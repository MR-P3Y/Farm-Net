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


class CheckoutIn(BaseModel):
    buyer_note: str | None = Field(default=None, max_length=2000)

    shipping_province_id: int | None = Field(default=None, ge=1)
    shipping_county_id: int | None = Field(default=None, ge=1)
    shipping_city_id: int | None = Field(default=None, ge=1)

    shipping_address: str | None = Field(default=None, max_length=5000)
    shipping_postal_code: str | None = Field(default=None, max_length=20)
    shipping_phone: str | None = Field(default=None, max_length=30)


class OrderItemOut(BaseModel):
    id: int
    order_id: int

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


class PaymentOut(BaseModel):
    id: int
    order_id: int
    user_id: int

    method: str
    status: str

    amount: Decimal
    currency: str

    provider: str | None = None
    provider_payment_id: str | None = None
    provider_reference: str | None = None

    paid_at: str | None = None
    failed_at: str | None = None
    cancelled_at: str | None = None

    created_at: str
    updated_at: str


class OrderStatusHistoryOut(BaseModel):
    id: int
    order_id: int
    changed_by: int | None = None
    from_status: str | None = None
    to_status: str
    note: str | None = None
    created_at: str


class OrderOut(BaseModel):
    id: int
    order_number: str

    buyer_user_id: int
    store_id: int

    status: str
    payment_status: str
    currency: str

    subtotal_amount: Decimal
    discount_amount: Decimal
    shipping_amount: Decimal
    total_amount: Decimal

    commission_percent: Decimal
    commission_amount: Decimal
    seller_amount: Decimal

    buyer_note: str | None = None
    seller_note: str | None = None
    admin_note: str | None = None

    shipping_province_id: int | None = None
    shipping_county_id: int | None = None
    shipping_city_id: int | None = None
    shipping_address: str | None = None
    shipping_postal_code: str | None = None
    shipping_phone: str | None = None

    paid_at: str | None = None
    confirmed_at: str | None = None
    cancelled_at: str | None = None
    delivered_at: str | None = None

    created_at: str
    updated_at: str

    items: list[OrderItemOut] = []
    payments: list[PaymentOut] = []
    status_history: list[OrderStatusHistoryOut] = []


class CheckoutOut(BaseModel):
    orders: list[OrderOut]
    orders_count: int
    total_amount: Decimal


class MockPaymentFailIn(BaseModel):
    reason: str | None = Field(default="Mock payment failed", max_length=2000)


class SellerOrderStatusUpdateIn(BaseModel):
    status: str = Field(min_length=3, max_length=50)
    seller_note: str | None = Field(default=None, max_length=2000)


class AdminOrderStatusUpdateIn(BaseModel):
    status: str = Field(min_length=3, max_length=50)
    admin_note: str | None = Field(default=None, max_length=2000)


class CommissionSettingOut(BaseModel):
    id: int
    title: str
    percent: Decimal
    status: str
    is_default: bool
    description: str | None = None
    created_by: int | None = None
    updated_by: int | None = None
    created_at: str
    updated_at: str


class CommissionSettingUpdateIn(BaseModel):
    percent: Decimal = Field(ge=0, le=100)
    description: str | None = Field(default=None, max_length=2000)


class PaymentCheckoutIn(BaseModel):
    invoice_id: int = Field(ge=1)
    provider: str = Field(min_length=2, max_length=80)
    idempotency_key: str = Field(min_length=8, max_length=160)


class PaymentVerifyIn(BaseModel):
    payment_attempt_id: int = Field(ge=1)
    provider_payment_id: str = Field(min_length=1, max_length=255)


class RefundCreateIn(BaseModel):
    invoice_id: int = Field(ge=1)
    amount: Decimal = Field(gt=0)
    reason: str = Field(min_length=3, max_length=2000)
    idempotency_key: str = Field(min_length=8, max_length=160)


class FinancialInvoiceOut(BaseModel):
    id: int
    invoice_number: str
    order_id: int
    buyer_user_id: int
    store_id: int
    status: str
    currency: str
    subtotal_amount: Decimal
    discount_amount: Decimal
    shipping_amount: Decimal
    total_amount: Decimal
    platform_amount: Decimal
    provider_amount: Decimal
    issued_at: str
    paid_at: str | None = None
    cancelled_at: str | None = None
    refunded_at: str | None = None
    created_at: str
    updated_at: str


class PaymentAttemptOut(BaseModel):
    id: int
    invoice_id: int
    order_id: int
    user_id: int
    provider: str
    status: str
    amount: Decimal
    currency: str
    idempotency_key: str
    provider_payment_id: str | None = None
    provider_reference: str | None = None
    redirect_url: str | None = None
    failure_code: str | None = None
    failure_message: str | None = None
    expires_at: str | None = None
    verified_at: str | None = None
    created_at: str
    updated_at: str


class FinancialTransactionOut(BaseModel):
    id: int
    invoice_id: int
    order_id: int
    payment_attempt_id: int | None = None
    transaction_type: str
    status: str
    amount: Decimal
    currency: str
    provider: str | None = None
    provider_reference: str | None = None
    description: str | None = None
    occurred_at: str
    created_at: str


class FinancialRefundOut(BaseModel):
    id: int
    invoice_id: int
    order_id: int
    payment_attempt_id: int | None = None
    transaction_id: int | None = None
    status: str
    amount: Decimal
    currency: str
    reason: str
    provider_reference: str | None = None
    requested_by_user_id: int | None = None
    processed_by_user_id: int | None = None
    failure_message: str | None = None
    requested_at: str
    processed_at: str | None = None
    created_at: str
    updated_at: str

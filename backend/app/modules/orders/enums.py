from enum import StrEnum


class CartStatus(StrEnum):
    ACTIVE = "active"
    CHECKED_OUT = "checked_out"
    ABANDONED = "abandoned"


class OrderStatus(StrEnum):
    PENDING_PAYMENT = "pending_payment"
    PAID = "paid"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethod(StrEnum):
    MOCK = "mock"
    CARD_TO_CARD = "card_to_card"
    ONLINE_GATEWAY = "online_gateway"


class CommissionSettingStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class InvoiceStatus(StrEnum):
    ISSUED = "issued"
    PAYMENT_PENDING = "payment_pending"
    PAID = "paid"
    CANCELLED = "cancelled"
    REFUND_PENDING = "refund_pending"
    REFUNDED = "refunded"


class PaymentAttemptStatus(StrEnum):
    CREATED = "created"
    REDIRECTED = "redirected"
    VERIFYING = "verifying"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class FinancialTransactionType(StrEnum):
    PAYMENT = "payment"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"


class FinancialTransactionStatus(StrEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REVERSED = "reversed"


class RefundStatus(StrEnum):
    REQUESTED = "requested"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class InventoryReservationStatus(StrEnum):
    RESERVED = "reserved"
    CONSUMED = "consumed"
    RELEASED = "released"
    EXPIRED = "expired"

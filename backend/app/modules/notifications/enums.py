from enum import Enum


class NotificationEventType(str, Enum):
    ORDER_CREATED = "order.created"
    ORDER_STATUS_CHANGED = "order.status_changed"

    PAYMENT_CREATED = "payment.created"
    PAYMENT_SUCCEEDED = "payment.succeeded"
    PAYMENT_FAILED = "payment.failed"
    PAYMENT_RECEIPT_UPLOADED = "payment.receipt_uploaded"

    VERIFICATION_SUBMITTED = "verification.submitted"
    VERIFICATION_APPROVED = "verification.approved"
    VERIFICATION_REJECTED = "verification.rejected"

    MEDIA_QUARANTINED = "media.quarantined"
    MEDIA_DELETED = "media.deleted"

    STORE_APPROVED = "store.approved"
    STORE_REJECTED = "store.rejected"

    PRODUCT_APPROVED = "product.approved"
    PRODUCT_REJECTED = "product.rejected"

    WEATHER_ALERT_CREATED = "weather.alert_created"
    WEATHER_ALERT_RESOLVED = "weather.alert_resolved"

    SYSTEM_MESSAGE = "system.message"


class NotificationChannel(str, Enum):
    IN_APP = "in_app"
    SMS = "sms"
    EMAIL = "email"
    PUSH = "push"
    TELEGRAM = "telegram"


class NotificationStatus(str, Enum):
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"
    DELETED = "deleted"


class NotificationPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationDeliveryStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    SKIPPED = "skipped"

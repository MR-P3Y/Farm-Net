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

    SOCIAL_COMMENT_CREATED = "social.comment_created"
    SOCIAL_REPLY_CREATED = "social.reply_created"
    SOCIAL_POST_REPORTED = "social.post_reported"
    SOCIAL_COMMENT_REPORTED = "social.comment_reported"
    SOCIAL_POST_HIDDEN = "social.post_hidden"
    SOCIAL_COMMENT_HIDDEN = "social.comment_hidden"

    EXPERT_ANSWER_CREATED = "expert_answer_created"

    CONSULTANT_REQUEST_SUBMITTED = "consultant.request_submitted"
    CONSULTANT_APPROVED = "consultant.approved"
    CONSULTANT_REJECTED = "consultant.rejected"
    CONSULT_REQUEST_CREATED = "consult.request_created"
    CONSULT_REQUEST_ACCEPTED = "consult.request_accepted"
    CONSULT_REQUEST_COMPLETED = "consult.request_completed"
    CONSULT_REQUEST_CANCELLED = "consult.request_cancelled"

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

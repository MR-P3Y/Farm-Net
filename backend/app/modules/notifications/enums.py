from enum import Enum


class NotificationEventType(str, Enum):
    ORDER_CREATED = "order.created"
    ORDER_STATUS_CHANGED = "order.status_changed"

    PAYMENT_CREATED = "payment.created"
    PAYMENT_SUCCEEDED = "payment.succeeded"
    PAYMENT_FAILED = "payment.failed"
    PAYMENT_RECEIPT_UPLOADED = "payment.receipt_uploaded"
    REFUND_REQUESTED = "finance.refund_requested"
    REFUND_COMPLETED = "finance.refund_completed"
    SETTLEMENT_REQUESTED = "finance.settlement_requested"
    SETTLEMENT_APPROVED = "finance.settlement_approved"
    SETTLEMENT_REJECTED = "finance.settlement_rejected"
    SETTLEMENT_SIMULATED = "finance.settlement_simulated"
    WALLET_ADJUSTED = "finance.wallet_adjusted"

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

    SERVICE_PROVIDER_SUBMITTED = "service_provider.submitted"
    SERVICE_PROVIDER_APPROVED = "service_provider.approved"
    SERVICE_PROVIDER_REJECTED = "service_provider.rejected"
    SERVICE_OFFER_SUBMITTED = "service_offer.submitted"
    SERVICE_OFFER_APPROVED = "service_offer.approved"
    SERVICE_OFFER_REJECTED = "service_offer.rejected"
    SERVICE_REQUEST_CREATED = "service_request.created"
    SERVICE_REQUEST_ACCEPTED = "service_request.accepted"
    SERVICE_REQUEST_REJECTED = "service_request.rejected"
    SERVICE_REQUEST_IN_PROGRESS = "service_request.in_progress"
    SERVICE_REQUEST_COMPLETED = "service_request.completed"
    SERVICE_REQUEST_CANCELLED = "service_request.cancelled"

    RENTAL_REQUEST_CREATED = "rental_request.created"
    RENTAL_REQUEST_ACCEPTED = "rental_request.accepted"
    RENTAL_REQUEST_REJECTED = "rental_request.rejected"
    RENTAL_REQUEST_IN_PROGRESS = "rental_request.in_progress"
    RENTAL_REQUEST_COMPLETED = "rental_request.completed"
    RENTAL_REQUEST_CANCELLED = "rental_request.cancelled"

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
    PROCESSING = "processing"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    SKIPPED = "skipped"

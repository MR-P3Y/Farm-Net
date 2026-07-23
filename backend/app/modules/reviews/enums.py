from enum import StrEnum


class ReviewSourceType(StrEnum):
    ORDER = "order"
    SERVICE_REQUEST = "service_request"
    RENTAL_REQUEST = "rental_request"
    CONSULT_REQUEST = "consult_request"


class ReviewSubjectType(StrEnum):
    PRODUCT = "product"
    STORE = "store"
    SERVICE_OFFER = "service_offer"
    SERVICE_PROVIDER = "service_provider"
    RENTAL_EQUIPMENT = "rental_equipment"
    RENTAL_LESSOR = "rental_lessor"
    CONSULTANT = "consultant"


class ReviewStatus(StrEnum):
    ACTIVE = "active"
    HIDDEN = "hidden"
    DELETED = "deleted"


class ReviewReportReason(StrEnum):
    SPAM = "spam"
    ABUSE = "abuse"
    HARASSMENT = "harassment"
    PRIVACY = "privacy"
    FRAUD = "fraud"
    OTHER = "other"


class ReviewReportStatus(StrEnum):
    OPEN = "open"
    REVIEWED = "reviewed"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class ReviewModerationAction(StrEnum):
    HIDDEN = "hidden"
    RESTORED = "restored"
    DELETED = "deleted"
    REPORT_REVIEWED = "report_reviewed"
    REPORT_RESOLVED = "report_resolved"
    REPORT_DISMISSED = "report_dismissed"

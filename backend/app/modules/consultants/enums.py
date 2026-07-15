from enum import StrEnum


class ConsultProfileStatus(StrEnum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class ConsultRequestStatus(StrEnum):
    OPEN = "open"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class ConsultContactMethod(StrEnum):
    IN_APP = "in_app"
    PHONE = "phone"
    VIDEO = "video"
    VISIT = "visit"

from enum import StrEnum


class LessorStatus(StrEnum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class RentalEquipmentStatus(StrEnum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class RentalOperatorMode(StrEnum):
    WITHOUT_OPERATOR = "without_operator"
    WITH_OPERATOR = "with_operator"
    EITHER = "either"


class RentalPricingUnit(StrEnum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    HECTARE = "hectare"
    PROJECT = "project"


class RentalDiscoverySort(StrEnum):
    RELEVANCE = "relevance"
    NEWEST = "newest"
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"


class RentalAvailabilityBlockType(StrEnum):
    UNAVAILABLE = "unavailable"
    MAINTENANCE = "maintenance"
    OWNER_RESERVED = "owner_reserved"


class RentalRequestStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

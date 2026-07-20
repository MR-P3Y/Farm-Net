from enum import StrEnum


class ServiceProviderStatus(StrEnum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class ServiceOfferStatus(StrEnum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class ServicePricingType(StrEnum):
    FIXED = "fixed"
    HOURLY = "hourly"
    DAILY = "daily"
    HECTARE = "hectare"
    PROJECT = "project"
    NEGOTIABLE = "negotiable"


class ServiceDiscoverySort(StrEnum):
    RELEVANCE = "relevance"
    NEWEST = "newest"
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    RATING = "rating"


class ServiceRequestStatus(StrEnum):
    OPEN = "open"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class ServiceContactMethod(StrEnum):
    IN_APP = "in_app"
    PHONE = "phone"
    VIDEO = "video"
    VISIT = "visit"

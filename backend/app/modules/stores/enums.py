from enum import StrEnum


class StoreStatus(StrEnum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"
    CLOSED = "closed"


class StoreType(StrEnum):
    AGRICULTURE_INPUTS = "agriculture_inputs"
    EQUIPMENT = "equipment"
    SEEDS = "seeds"
    FERTILIZER = "fertilizer"
    PESTICIDE = "pesticide"
    MIXED = "mixed"
    OTHER = "other"


class StoreDiscoverySort(StrEnum):
    RELEVANCE = "relevance"
    NEWEST = "newest"


class StoreMemberRole(StrEnum):
    OWNER = "owner"
    MANAGER = "manager"
    STAFF = "staff"
    VIEWER = "viewer"


class StoreMemberStatus(StrEnum):
    ACTIVE = "active"
    INVITED = "invited"
    SUSPENDED = "suspended"
    REMOVED = "removed"

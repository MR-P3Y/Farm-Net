from enum import StrEnum


class PlanStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    RETIRED = "retired"


class BillingPeriod(StrEnum):
    FREE = "free"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class FeatureValueKind(StrEnum):
    BOOLEAN = "boolean"
    INTEGER = "integer"
    DECIMAL = "decimal"
    STRING = "string"
    JSON = "json"


class FeatureStatus(StrEnum):
    ACTIVE = "active"
    RETIRED = "retired"


class SubscriptionStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    GRACE = "grace"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class SubscriptionPeriodStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    CLOSED = "closed"
    VOID = "void"


class EntitlementSource(StrEnum):
    PLAN = "plan"
    ADDON = "addon"
    ADMIN = "admin"


class UsageReservationStatus(StrEnum):
    RESERVED = "reserved"
    FINALIZED = "finalized"
    RELEASED = "released"
    EXPIRED = "expired"

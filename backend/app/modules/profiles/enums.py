from enum import StrEnum


class Gender(StrEnum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class DocumentType(StrEnum):
    NATIONAL_CARD = "national_card"
    BUSINESS_LICENSE = "business_license"
    AGRICULTURE_CERTIFICATE = "agriculture_certificate"
    CONSULTANT_CERTIFICATE = "consultant_certificate"
    EQUIPMENT_OWNERSHIP = "equipment_ownership"
    DRIVER_LICENSE = "driver_license"
    CONTRACT_SIGNED_PDF = "contract_signed_pdf"
    OTHER = "other"


class DocumentStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class VerificationTargetRole(StrEnum):
    SHOP_OWNER = "shop_owner"
    LESSOR = "lessor"
    CONSULTANT = "consultant"
    SERVICE_PROVIDER = "service_provider"
    DATA_CLIENT = "data_client"


class VerificationStatus(StrEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    NEEDS_REVISION = "needs_revision"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class VerificationReviewAction(StrEnum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    NEEDS_REVISION = "needs_revision"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

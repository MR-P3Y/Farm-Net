from enum import StrEnum


class MediaVisibility(StrEnum):
    PUBLIC = "public"
    PRIVATE = "private"


class MediaStatus(StrEnum):
    ACTIVE = "active"
    DELETED = "deleted"
    QUARANTINED = "quarantined"


class MediaPurpose(StrEnum):
    PRODUCT_IMAGE = "product_image"
    SOCIAL_POST_IMAGE = "social_post_image"
    STORE_LOGO = "store_logo"
    STORE_BANNER = "store_banner"
    PROFILE_DOCUMENT = "profile_document"
    VERIFICATION_DOCUMENT = "verification_document"
    GENERAL = "general"


class MediaStorageDisk(StrEnum):
    LOCAL = "local"

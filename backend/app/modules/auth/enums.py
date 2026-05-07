from enum import StrEnum


class UserStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class TokenStatus(StrEnum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class OtpPurpose(StrEnum):
    LOGIN = "login"
    REGISTER = "register"
    VERIFY_PHONE = "verify_phone"
    RESET_PASSWORD = "reset_password"


class OtpStatus(StrEnum):
    PENDING = "pending"
    USED = "used"
    EXPIRED = "expired"
    FAILED = "failed"


class SessionStatus(StrEnum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"
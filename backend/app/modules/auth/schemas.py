from datetime import datetime

from email_validator import EmailNotValidError, validate_email
from pydantic import BaseModel, Field, field_validator


def normalize_email(value: str) -> str:
    try:
        validation = validate_email(
            value,
            check_deliverability=False,
            test_environment=True,
        )
    except EmailNotValidError as exc:
        raise ValueError(str(exc)) from exc

    return validation.normalized.lower()


class AuthUserOut(BaseModel):
    id: int
    email: str | None = None
    phone: str | None = None
    status: str
    is_email_verified: bool
    is_phone_verified: bool


class TokenPairOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: AuthUserOut


class EmailRegisterIn(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=128)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    display_name: str | None = Field(default=None, max_length=150)
    national_id: str = Field(min_length=10, max_length=10, pattern=r"^\d{10}$")
    province_id: int = Field(ge=1)
    county_id: int = Field(ge=1)
    city_id: int | None = Field(default=None, ge=1)
    address: str = Field(min_length=1, max_length=2000)
    postal_code: str | None = Field(
        default=None,
        min_length=10,
        max_length=10,
        pattern=r"^\d{10}$",
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return normalize_email(value)

    @field_validator(
        "first_name",
        "last_name",
        "display_name",
        "address",
        mode="before",
    )
    @classmethod
    def normalize_profile_text(cls, value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value

    @field_validator("national_id", "postal_code", mode="before")
    @classmethod
    def normalize_profile_digits(cls, value):
        if value is None:
            return None
        translation_table = str.maketrans(
            "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
            "01234567890123456789",
        )
        return str(value).strip().translate(translation_table)


class EmailLoginIn(BaseModel):
    email: str
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return normalize_email(value)


class OtpRequestIn(BaseModel):
    phone: str
    purpose: str = "login"


class OtpRequestOut(BaseModel):
    phone: str
    expires_in_seconds: int
    dev_code: str | None = None


class OtpVerifyIn(BaseModel):
    phone: str
    code: str = Field(min_length=4, max_length=10)
    purpose: str = "login"


class RefreshTokenIn(BaseModel):
    refresh_token: str = Field(min_length=20)


class LogoutIn(BaseModel):
    refresh_token: str | None = None


class ChangePasswordIn(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class PasswordResetRequestIn(BaseModel):
    identifier: str = Field(min_length=3, max_length=255)

    @field_validator("identifier")
    @classmethod
    def normalize_identifier(cls, value: str) -> str:
        return value.strip()


class PasswordResetRequestOut(BaseModel):
    expires_in_seconds: int
    dev_code: str | None = None


class PasswordResetConfirmIn(BaseModel):
    identifier: str = Field(min_length=3, max_length=255)
    code: str = Field(min_length=4, max_length=10)
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("identifier", "code")
    @classmethod
    def normalize_reset_text(cls, value: str) -> str:
        return value.strip()


class AuthSessionOut(BaseModel):
    id: int
    status: str
    ip_address: str | None = None
    user_agent: str | None = None
    is_current: bool
    created_at: datetime
    last_seen_at: datetime | None = None
    expires_at: datetime | None = None


class CurrentUserOut(BaseModel):
    id: int
    email: str | None = None
    phone: str | None = None
    status: str
    is_email_verified: bool
    is_phone_verified: bool
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)

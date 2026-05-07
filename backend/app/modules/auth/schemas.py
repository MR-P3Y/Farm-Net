from pydantic import BaseModel, EmailStr, Field


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
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class EmailLoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


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
    refresh_token: str
from datetime import datetime

from pydantic import BaseModel, Field


class AdminUserListItemOut(BaseModel):
    id: int
    email: str | None = None
    phone: str | None = None
    status: str
    is_email_verified: bool
    is_phone_verified: bool
    roles: list[str] = Field(default_factory=list)


class AdminUserDetailOut(BaseModel):
    id: int
    email: str | None = None
    phone: str | None = None
    status: str
    is_email_verified: bool
    is_phone_verified: bool
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)


class AdminUpdateUserStatusIn(BaseModel):
    status: str = Field(min_length=3, max_length=50)


class AdminRoleOut(BaseModel):
    id: int
    code: str
    name: str
    description: str | None = None
    is_system: bool
    is_active: bool


class AdminPermissionOut(BaseModel):
    id: int
    code: str
    name: str
    module: str
    description: str | None = None
    is_system: bool
    is_active: bool


class AdminVerificationDocumentOut(BaseModel):
    id: int
    document_id: int
    document_type: str
    file_name: str
    status: str


class AdminVerificationReviewOut(BaseModel):
    id: int
    reviewer_id: int | None = None
    action: str
    note: str | None = None
    created_at: datetime


class AdminVerificationRequestOut(BaseModel):
    id: int
    user_id: int
    user_email: str | None = None
    user_phone: str | None = None
    target_role: str
    status: str
    request_note: str | None = None
    admin_note: str | None = None
    submitted_at: datetime | None = None
    reviewed_at: datetime | None = None
    reviewed_by: int | None = None
    created_at: datetime
    updated_at: datetime
    documents: list[AdminVerificationDocumentOut] = Field(default_factory=list)
    reviews: list[AdminVerificationReviewOut] = Field(default_factory=list)


class AdminUpdateVerificationStatusIn(BaseModel):
    status: str = Field(min_length=3, max_length=50)
    note: str | None = Field(default=None, max_length=2000)

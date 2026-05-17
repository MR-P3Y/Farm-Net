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


class AdminStoreMemberOut(BaseModel):
    id: int
    store_id: int
    user_id: int
    role: str
    status: str
    invited_by: int | None = None
    joined_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class AdminStoreStatusHistoryOut(BaseModel):
    id: int
    store_id: int
    changed_by: int | None = None
    from_status: str | None = None
    to_status: str
    note: str | None = None
    created_at: datetime


class AdminStoreOut(BaseModel):
    id: int
    owner_user_id: int
    owner_email: str | None = None
    owner_phone: str | None = None

    name: str
    slug: str
    description: str | None = None

    status: str
    store_type: str

    phone: str | None = None
    email: str | None = None

    province_id: int | None = None
    county_id: int | None = None
    district_id: int | None = None
    city_id: int | None = None
    village_id: int | None = None

    address: str | None = None
    postal_code: str | None = None

    latitude: str | None = None
    longitude: str | None = None

    logo_file_id: str | None = None
    banner_file_id: str | None = None

    admin_note: str | None = None

    approved_at: datetime | None = None
    approved_by: int | None = None
    rejected_at: datetime | None = None
    rejected_by: int | None = None

    created_at: datetime
    updated_at: datetime

    members: list[AdminStoreMemberOut] = Field(default_factory=list)
    status_history: list[AdminStoreStatusHistoryOut] = Field(default_factory=list)


class AdminUpdateStoreStatusIn(BaseModel):
    status: str = Field(min_length=3, max_length=50)
    note: str | None = Field(default=None, max_length=2000)

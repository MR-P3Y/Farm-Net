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

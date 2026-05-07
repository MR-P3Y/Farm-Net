from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import all models here so Alembic can detect them.
from app.modules.auth.models import (  # noqa: E402,F401
    AuthOtpCode,
    AuthPermission,
    AuthRefreshToken,
    AuthRole,
    AuthRolePermission,
    AuthSession,
    AuthUser,
    AuthUserRole,
)
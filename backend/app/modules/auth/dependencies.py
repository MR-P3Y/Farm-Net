from collections.abc import Callable
from datetime import datetime

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token, ensure_token_type
from app.db.session import get_db
from app.modules.auth.enums import UserStatus
from app.modules.auth.exceptions import PermissionDeniedError, TokenInvalidError, UserNotFoundError
from app.modules.auth.models import AuthUser
from app.modules.auth.repository import AuthRepository


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> AuthUser:
    if credentials is None or not credentials.credentials:
        raise TokenInvalidError()

    token = credentials.credentials

    try:
        payload = decode_token(token)
        ensure_token_type(payload, "access")
        user_id = int(payload["sub"])
        session_id = int(payload["sid"])
    except (KeyError, TypeError, ValueError) as exc:
        raise TokenInvalidError() from exc

    repo = AuthRepository(db)
    session = repo.get_session_by_id(session_id)
    if (
        session is None
        or session.user_id != user_id
        or session.status != "active"
        or session.expires_at is None
        or session.expires_at < datetime.utcnow()
    ):
        raise TokenInvalidError()

    user = repo.get_user_by_id(user_id)

    if user is None:
        raise UserNotFoundError()

    return user


def get_current_active_user(
    user: AuthUser = Depends(get_current_user),
) -> AuthUser:
    if user.status in {UserStatus.SUSPENDED.value, UserStatus.DELETED.value}:
        raise TokenInvalidError()

    return user


def require_permission(permission: str) -> Callable:
    def dependency(
        user: AuthUser = Depends(get_current_active_user),
        db: Session = Depends(get_db),
    ) -> AuthUser:
        repo = AuthRepository(db)
        permissions = set(repo.get_user_permission_codes(user.id))

        if permission not in permissions:
            raise PermissionDeniedError()

        return user

    return dependency

from datetime import datetime

from sqlalchemy.orm import Session

from app.modules.auth.models import (
    AuthOtpCode,
    AuthPermission,
    AuthRefreshToken,
    AuthRole,
    AuthRolePermission,
    AuthSession,
    AuthUser,
    AuthUserRole,
)


class AuthRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_user_by_id(self, user_id: int) -> AuthUser | None:
        return self.db.query(AuthUser).filter(AuthUser.id == user_id).one_or_none()

    def get_user_by_email(self, email: str) -> AuthUser | None:
        return (
            self.db.query(AuthUser)
            .filter(AuthUser.email == email.lower())
            .one_or_none()
        )

    def get_user_by_phone(self, phone: str) -> AuthUser | None:
        return self.db.query(AuthUser).filter(AuthUser.phone == phone).one_or_none()

    def create_user(
        self,
        *,
        email: str | None,
        phone: str | None,
        password_hash: str | None,
        status: str,
        is_email_verified: bool = False,
        is_phone_verified: bool = False,
    ) -> AuthUser:
        user = AuthUser(
            email=email.lower() if email else None,
            phone=phone,
            password_hash=password_hash,
            status=status,
            is_email_verified=is_email_verified,
            is_phone_verified=is_phone_verified,
        )
        self.db.add(user)
        self.db.flush()
        return user

    def get_role_by_code(self, code: str) -> AuthRole | None:
        return self.db.query(AuthRole).filter(AuthRole.code == code).one_or_none()

    def get_user_role_codes(self, user_id: int) -> list[str]:
        rows = (
            self.db.query(AuthRole.code)
            .join(AuthUserRole, AuthUserRole.role_id == AuthRole.id)
            .filter(AuthUserRole.user_id == user_id)
            .all()
        )
        return [row[0] for row in rows]

    def get_user_permission_codes(self, user_id: int) -> list[str]:
        rows = (
            self.db.query(AuthPermission.code)
            .join(AuthRolePermission, AuthRolePermission.permission_id == AuthPermission.id)
            .join(AuthRole, AuthRole.id == AuthRolePermission.role_id)
            .join(AuthUserRole, AuthUserRole.role_id == AuthRole.id)
            .filter(
                AuthUserRole.user_id == user_id,
                AuthPermission.is_active.is_(True),
                AuthRole.is_active.is_(True),
            )
            .distinct()
            .all()
        )
        return [row[0] for row in rows]

    def assign_role_to_user(
        self,
        *,
        user_id: int,
        role_id: int,
        assigned_by: int | None = None,
    ) -> AuthUserRole:
        existing = (
            self.db.query(AuthUserRole)
            .filter(
                AuthUserRole.user_id == user_id,
                AuthUserRole.role_id == role_id,
            )
            .one_or_none()
        )

        if existing:
            return existing

        user_role = AuthUserRole(
            user_id=user_id,
            role_id=role_id,
            assigned_by=assigned_by,
        )
        self.db.add(user_role)
        self.db.flush()
        return user_role

    def create_session(
        self,
        *,
        user_id: int,
        status: str,
        ip_address: str | None,
        user_agent: str | None,
        expires_at: datetime | None,
    ) -> AuthSession:
        session = AuthSession(
            user_id=user_id,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at,
            last_seen_at=datetime.utcnow(),
        )
        self.db.add(session)
        self.db.flush()
        return session

    def create_refresh_token(
        self,
        *,
        user_id: int,
        session_id: int | None,
        token_hash: str,
        status: str,
        expires_at: datetime,
    ) -> AuthRefreshToken:
        token = AuthRefreshToken(
            user_id=user_id,
            session_id=session_id,
            token_hash=token_hash,
            status=status,
            expires_at=expires_at,
        )
        self.db.add(token)
        self.db.flush()
        return token

    def get_refresh_token_by_hash(self, token_hash: str) -> AuthRefreshToken | None:
        return (
            self.db.query(AuthRefreshToken)
            .filter(AuthRefreshToken.token_hash == token_hash)
            .one_or_none()
        )

    def revoke_refresh_token(self, token: AuthRefreshToken, revoked_at: datetime) -> None:
        token.status = "revoked"
        token.revoked_at = revoked_at

    def revoke_session(self, session_id: int | None, revoked_at: datetime) -> None:
        if session_id is None:
            return

        session = (
            self.db.query(AuthSession)
            .filter(AuthSession.id == session_id)
            .one_or_none()
        )

        if session is None:
            return

        session.status = "revoked"
        session.revoked_at = revoked_at

    def create_otp_code(
        self,
        *,
        user_id: int | None,
        phone: str,
        code_hash: str,
        purpose: str,
        status: str,
        max_attempts: int,
        expires_at: datetime,
        ip_address: str | None,
        user_agent: str | None,
    ) -> AuthOtpCode:
        otp = AuthOtpCode(
            user_id=user_id,
            phone=phone,
            code_hash=code_hash,
            purpose=purpose,
            status=status,
            max_attempts=max_attempts,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(otp)
        self.db.flush()
        return otp

    def get_latest_pending_otp(
        self,
        *,
        phone: str,
        purpose: str,
    ) -> AuthOtpCode | None:
        return (
            self.db.query(AuthOtpCode)
            .filter(
                AuthOtpCode.phone == phone,
                AuthOtpCode.purpose == purpose,
                AuthOtpCode.status == "pending",
            )
            .order_by(AuthOtpCode.created_at.desc())
            .first()
        )

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

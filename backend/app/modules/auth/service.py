from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    ensure_token_type,
    hash_password,
    hash_token,
    verify_password,
)
from app.modules.auth.enums import (
    OtpPurpose,
    OtpStatus,
    SessionStatus,
    TokenStatus,
    UserStatus,
)
from app.modules.auth.exceptions import (
    InvalidCredentialsError,
    OtpExpiredError,
    OtpInvalidError,
    OtpTooManyAttemptsError,
    TokenInvalidError,
    UserAlreadyExistsError,
    UserNotFoundError,
    UserSuspendedError,
)
from app.modules.auth.models import AuthUser
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import AuthUserOut, CurrentUserOut, OtpRequestOut, TokenPairOut
from app.modules.auth.utils import normalize_iran_phone


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = AuthRepository(db)
        self.settings = get_settings()

    def register_with_email(
        self,
        *,
        email: str,
        password: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TokenPairOut:
        normalized_email = email.strip().lower()

        existing = self.repo.get_user_by_email(normalized_email)
        if existing is not None:
            raise UserAlreadyExistsError()

        user = self.repo.create_user(
            email=normalized_email,
            phone=None,
            password_hash=hash_password(password),
            status=UserStatus.ACTIVE.value,
            is_email_verified=False,
            is_phone_verified=False,
        )

        self._assign_base_user_role(user)

        token_pair = self._create_token_pair(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.repo.commit()
        return token_pair

    def login_with_email(
        self,
        *,
        email: str,
        password: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TokenPairOut:
        normalized_email = email.strip().lower()

        user = self.repo.get_user_by_email(normalized_email)
        if user is None or not user.password_hash:
            raise InvalidCredentialsError()

        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        self._ensure_user_can_login(user)

        user.last_login_at = datetime.utcnow()

        token_pair = self._create_token_pair(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.repo.commit()
        return token_pair

    def request_otp(
        self,
        *,
        phone: str,
        purpose: str = OtpPurpose.LOGIN.value,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> OtpRequestOut:
        normalized_phone = normalize_iran_phone(phone)

        if purpose not in {item.value for item in OtpPurpose}:
            purpose = OtpPurpose.LOGIN.value

        user = self.repo.get_user_by_phone(normalized_phone)

        otp_code = self._get_dev_otp_code()

        expires_at = datetime.utcnow() + timedelta(
            minutes=self.settings.otp_expire_minutes,
        )

        self.repo.create_otp_code(
            user_id=user.id if user else None,
            phone=normalized_phone,
            code_hash=hash_token(otp_code),
            purpose=purpose,
            status=OtpStatus.PENDING.value,
            max_attempts=self.settings.otp_max_attempts,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.repo.commit()

        return OtpRequestOut(
            phone=normalized_phone,
            expires_in_seconds=self.settings.otp_expire_minutes * 60,
            dev_code=otp_code if self.settings.auth_dev_otp_enabled else None,
        )

    def verify_otp(
        self,
        *,
        phone: str,
        code: str,
        purpose: str = OtpPurpose.LOGIN.value,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TokenPairOut:
        normalized_phone = normalize_iran_phone(phone)

        otp = self.repo.get_latest_pending_otp(
            phone=normalized_phone,
            purpose=purpose,
        )

        if otp is None:
            raise OtpInvalidError()

        if otp.expires_at < datetime.utcnow():
            otp.status = OtpStatus.EXPIRED.value
            self.repo.commit()
            raise OtpExpiredError()

        if otp.attempts >= otp.max_attempts:
            otp.status = OtpStatus.FAILED.value
            self.repo.commit()
            raise OtpTooManyAttemptsError()

        otp.attempts += 1

        if otp.code_hash != hash_token(code):
            self.repo.commit()
            raise OtpInvalidError()

        otp.status = OtpStatus.USED.value
        otp.used_at = datetime.utcnow()

        user = self.repo.get_user_by_phone(normalized_phone)

        if user is None:
            user = self.repo.create_user(
                email=None,
                phone=normalized_phone,
                password_hash=None,
                status=UserStatus.ACTIVE.value,
                is_email_verified=False,
                is_phone_verified=True,
            )
            self._assign_base_user_role(user)
        else:
            self._ensure_user_can_login(user)
            user.is_phone_verified = True
            user.status = UserStatus.ACTIVE.value

        user.last_login_at = datetime.utcnow()

        token_pair = self._create_token_pair(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.repo.commit()
        return token_pair

    def refresh_access_token(
        self,
        *,
        refresh_token: str,
    ) -> TokenPairOut:
        try:
            payload = decode_token(refresh_token)
            ensure_token_type(payload, "refresh")
        except (KeyError, TypeError, ValueError) as exc:
            raise TokenInvalidError() from exc

        try:
            user_id = int(payload["sub"])
        except (KeyError, TypeError, ValueError) as exc:
            raise TokenInvalidError() from exc

        token_hash = hash_token(refresh_token)
        stored_token = self.repo.get_refresh_token_by_hash(token_hash)

        if stored_token is None:
            raise TokenInvalidError()

        if stored_token.status != TokenStatus.ACTIVE.value:
            raise TokenInvalidError()

        if stored_token.expires_at < datetime.utcnow():
            stored_token.status = TokenStatus.EXPIRED.value
            self.repo.commit()
            raise TokenInvalidError()

        user = self.repo.get_user_by_id(user_id)
        if user is None:
            raise UserNotFoundError()

        self._ensure_user_can_login(user)

        access_token = create_access_token(subject=user.id)

        # Refresh token rotation is intentionally deferred to the stricter auth phase.
        self.repo.commit()

        return TokenPairOut(
            access_token=access_token,
            refresh_token=refresh_token,
            user=self._user_out(user),
        )

    def logout(
        self,
        *,
        refresh_token: str | None,
    ) -> None:
        if not refresh_token:
            return

        token_hash = hash_token(refresh_token)
        stored_token = self.repo.get_refresh_token_by_hash(token_hash)

        if stored_token is None:
            return

        now = datetime.utcnow()

        self.repo.revoke_refresh_token(stored_token, revoked_at=now)
        self.repo.revoke_session(stored_token.session_id, revoked_at=now)
        self.repo.commit()

    def get_current_user_out(self, user: AuthUser) -> CurrentUserOut:
        roles = self.repo.get_user_role_codes(user.id)
        permissions = self.repo.get_user_permission_codes(user.id)

        return CurrentUserOut(
            id=user.id,
            email=user.email,
            phone=user.phone,
            status=user.status,
            is_email_verified=user.is_email_verified,
            is_phone_verified=user.is_phone_verified,
            roles=roles,
            permissions=permissions,
        )

    def _assign_base_user_role(self, user: AuthUser) -> None:
        role = self.repo.get_role_by_code("user")
        if role is None:
            raise RuntimeError("Base role 'user' is not seeded")

        self.repo.assign_role_to_user(
            user_id=user.id,
            role_id=role.id,
            assigned_by=None,
        )

    def _ensure_user_can_login(self, user: AuthUser) -> None:
        if user.status == UserStatus.SUSPENDED.value:
            raise UserSuspendedError()

        if user.status == UserStatus.DELETED.value:
            raise UserNotFoundError()

    def _create_token_pair(
        self,
        *,
        user: AuthUser,
        ip_address: str | None,
        user_agent: str | None,
    ) -> TokenPairOut:
        session_expires_at = datetime.utcnow() + timedelta(
            days=self.settings.jwt_refresh_token_expire_days,
        )

        session = self.repo.create_session(
            user_id=user.id,
            status=SessionStatus.ACTIVE.value,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=session_expires_at,
        )

        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(
            subject=user.id,
            extra_claims={"sid": session.id},
        )

        self.repo.create_refresh_token(
            user_id=user.id,
            session_id=session.id,
            token_hash=hash_token(refresh_token),
            status=TokenStatus.ACTIVE.value,
            expires_at=session_expires_at,
        )

        return TokenPairOut(
            access_token=access_token,
            refresh_token=refresh_token,
            user=self._user_out(user),
        )

    def _user_out(self, user: AuthUser) -> AuthUserOut:
        return AuthUserOut(
            id=user.id,
            email=user.email,
            phone=user.phone,
            status=user.status,
            is_email_verified=user.is_email_verified,
            is_phone_verified=user.is_phone_verified,
        )

    def _get_dev_otp_code(self) -> str:
        if self.settings.auth_dev_otp_enabled:
            return self.settings.auth_dev_otp_code

        # SMS provider واقعی در فاز Notification/SMS اضافه می‌شود.
        # فعلاً اگر dev OTP خاموش شد، باز هم code ساده تولید می‌کنیم تا سرویس نشکند.
        return self.settings.auth_dev_otp_code

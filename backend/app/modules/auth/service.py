from datetime import datetime, timedelta
import logging
import secrets
from urllib.parse import urlparse

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

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
    CurrentPasswordInvalidError,
    InvalidCredentialsError,
    OtpExpiredError,
    OtpInvalidError,
    OtpTooManyAttemptsError,
    PasswordResetExpiredError,
    PasswordResetInvalidError,
    PasswordResetTooManyAttemptsError,
    TokenInvalidError,
    UserAlreadyExistsError,
    UserNotFoundError,
    UserSuspendedError,
    ValidationAuthError,
)
from app.modules.auth.models import AuthUser
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import (
    AuthSessionOut,
    AuthUserOut,
    CurrentUserOut,
    OtpRequestOut,
    PasswordResetRequestOut,
    TokenPairOut,
    normalize_email,
)
from app.modules.auth.utils import normalize_iran_phone
from app.modules.notifications.email_provider import (
    EmailProviderError,
    SmtpEmailTransport,
    build_email_envelope,
)
from app.modules.notifications.sms_provider import (
    HttpJsonSmsTransport,
    SmsProviderError,
    build_sms_message,
)
from app.modules.profiles.repository import ProfileRepository
from app.modules.profiles.schemas import ProfileUpdateIn
from app.modules.profiles.service import ProfileService
from app.core.exceptions import AppException


logger = logging.getLogger(__name__)


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
        profile: ProfileUpdateIn,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TokenPairOut:
        normalized_email = email.strip().lower()

        existing = self.repo.get_user_by_email(normalized_email)
        if existing is not None:
            raise UserAlreadyExistsError()

        try:
            user = self.repo.create_user(
                email=normalized_email,
                phone=None,
                password_hash=hash_password(password),
                status=UserStatus.ACTIVE.value,
                is_email_verified=False,
                is_phone_verified=False,
            )

            ProfileService(self.db).prepare_registration_profile(
                user=user,
                payload=profile,
            )

            self._assign_base_user_role(user)

            token_pair = self._create_token_pair(
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            self.repo.commit()
        except IntegrityError as exc:
            self.repo.rollback()
            if self.repo.get_user_by_email(normalized_email) is not None:
                raise UserAlreadyExistsError() from exc
            if (
                profile.national_id
                and ProfileRepository(self.db).get_profile_by_national_id(
                    profile.national_id,
                )
                is not None
            ):
                raise AppException(
                    code="PROFILE_NATIONAL_ID_CONFLICT",
                    message="National ID is already linked to another account",
                    status_code=409,
                    details={"field": "national_id"},
                ) from exc
            raise AppException(
                code="AUTH_REGISTRATION_CONFLICT",
                message="Registration data conflicts with an existing account",
                status_code=409,
            ) from exc
        except Exception:
            self.repo.rollback()
            raise
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
            session_id = int(payload["sid"])
        except (KeyError, TypeError, ValueError) as exc:
            raise TokenInvalidError() from exc

        token_hash = hash_token(refresh_token)
        stored_token = self.repo.get_refresh_token_by_hash_for_update(token_hash)

        if stored_token is None:
            raise TokenInvalidError()

        if stored_token.status != TokenStatus.ACTIVE.value:
            if stored_token.session_id is not None:
                now = datetime.utcnow()
                self.repo.revoke_session(stored_token.session_id, revoked_at=now)
                self.repo.revoke_active_refresh_tokens_for_session(
                    stored_token.session_id,
                    revoked_at=now,
                )
                self.repo.commit()
            raise TokenInvalidError()

        if stored_token.user_id != user_id or stored_token.session_id != session_id:
            raise TokenInvalidError()

        now = datetime.utcnow()
        if stored_token.expires_at < now:
            stored_token.status = TokenStatus.EXPIRED.value
            self.repo.commit()
            raise TokenInvalidError()

        session = self.repo.get_session_by_id(session_id)
        if (
            session is None
            or session.user_id != user_id
            or session.status != SessionStatus.ACTIVE.value
            or session.expires_at is None
            or session.expires_at < now
        ):
            raise TokenInvalidError()

        user = self.repo.get_user_by_id(user_id)
        if user is None:
            raise UserNotFoundError()

        self._ensure_user_can_login(user)

        remaining_lifetime = session.expires_at - now
        access_token = create_access_token(
            subject=user.id,
            extra_claims={"sid": session.id},
            expires_delta=min(
                remaining_lifetime,
                timedelta(minutes=self.settings.jwt_access_token_expire_minutes),
            ),
        )
        rotated_refresh_token = create_refresh_token(
            subject=user.id,
            extra_claims={"sid": session.id},
            expires_delta=remaining_lifetime,
        )
        self.repo.revoke_refresh_token(stored_token, revoked_at=now)
        self.repo.create_refresh_token(
            user_id=user.id,
            session_id=session.id,
            token_hash=hash_token(rotated_refresh_token),
            status=TokenStatus.ACTIVE.value,
            expires_at=session.expires_at,
        )
        self.repo.commit()

        return TokenPairOut(
            access_token=access_token,
            refresh_token=rotated_refresh_token,
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

    def list_my_sessions(
        self,
        *,
        user: AuthUser,
        current_session_id: int,
    ) -> list[AuthSessionOut]:
        sessions = self.repo.list_active_sessions_for_user(
            user_id=user.id,
            now=datetime.utcnow(),
        )
        return [
            AuthSessionOut(
                id=session.id,
                status=session.status,
                ip_address=session.ip_address,
                user_agent=session.user_agent,
                is_current=session.id == current_session_id,
                created_at=session.created_at,
                last_seen_at=session.last_seen_at,
                expires_at=session.expires_at,
            )
            for session in sessions
        ]

    def revoke_my_session(
        self,
        *,
        user: AuthUser,
        session_id: int,
        current_session_id: int,
    ) -> None:
        if session_id == current_session_id:
            raise ValidationAuthError(
                message="Current session must be closed by logging out",
                details={"session_id": session_id},
            )

        session = self.repo.get_session_by_id_for_user(
            session_id=session_id,
            user_id=user.id,
        )
        if session is None or session.status != SessionStatus.ACTIVE.value:
            raise ValidationAuthError(
                message="Active session not found",
                details={"session_id": session_id},
            )

        now = datetime.utcnow()
        self.repo.revoke_active_refresh_tokens_for_session(session.id, revoked_at=now)
        self.repo.revoke_session(session.id, revoked_at=now)
        self.repo.commit()

    def revoke_my_other_sessions(
        self,
        *,
        user: AuthUser,
        current_session_id: int,
    ) -> int:
        sessions = self.repo.list_active_sessions_for_user(
            user_id=user.id,
            now=datetime.utcnow(),
        )
        other_sessions = [
            session for session in sessions if session.id != current_session_id
        ]
        now = datetime.utcnow()
        for session in other_sessions:
            self.repo.revoke_active_refresh_tokens_for_session(
                session.id,
                revoked_at=now,
            )
            self.repo.revoke_session(session.id, revoked_at=now)

        self.repo.commit()
        return len(other_sessions)

    def change_my_password(
        self,
        *,
        user: AuthUser,
        current_password: str,
        new_password: str,
        current_session_id: int,
    ) -> int:
        if user.password_hash is None or not verify_password(
            current_password,
            user.password_hash,
        ):
            raise CurrentPasswordInvalidError()

        if verify_password(new_password, user.password_hash):
            raise ValidationAuthError(
                message="New password must be different from current password",
                details={"field": "new_password"},
            )

        user.password_hash = hash_password(new_password)
        return self.revoke_my_other_sessions(
            user=user,
            current_session_id=current_session_id,
        )

    def request_password_reset(
        self,
        *,
        identifier: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> PasswordResetRequestOut:
        channel, normalized_identifier, user = self._resolve_reset_identifier(
            identifier
        )
        code = self._get_dev_otp_code()
        code_hash = hash_token(code)
        expires_at = datetime.utcnow() + timedelta(
            minutes=self.settings.otp_expire_minutes,
        )
        dev_code = None

        if user is not None and user.status == UserStatus.ACTIVE.value:
            identifier_hash = hash_token(normalized_identifier)
            self.repo.expire_pending_password_resets(
                identifier_hash=identifier_hash,
            )
            self.repo.create_password_reset_challenge(
                user_id=user.id,
                identifier_hash=identifier_hash,
                channel=channel,
                code_hash=code_hash,
                max_attempts=self.settings.otp_max_attempts,
                expires_at=expires_at,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            self.repo.commit()
            self._deliver_password_reset_code(
                channel=channel,
                destination=normalized_identifier,
                code=code,
            )
            if self.settings.auth_dev_otp_enabled:
                dev_code = code

        return PasswordResetRequestOut(
            expires_in_seconds=self.settings.otp_expire_minutes * 60,
            dev_code=dev_code,
        )

    def confirm_password_reset(
        self,
        *,
        identifier: str,
        code: str,
        new_password: str,
    ) -> int:
        _channel, normalized_identifier, user = self._resolve_reset_identifier(
            identifier
        )
        challenge = self.repo.get_latest_pending_password_reset_for_update(
            identifier_hash=hash_token(normalized_identifier),
        )
        if challenge is None:
            raise PasswordResetInvalidError()

        now = datetime.utcnow()
        if challenge.expires_at < now:
            challenge.status = OtpStatus.EXPIRED.value
            self.repo.commit()
            raise PasswordResetExpiredError()

        if challenge.attempts >= challenge.max_attempts:
            challenge.status = OtpStatus.FAILED.value
            self.repo.commit()
            raise PasswordResetTooManyAttemptsError()

        challenge.attempts += 1
        if challenge.code_hash != hash_token(code):
            self.repo.commit()
            raise PasswordResetInvalidError()

        if (
            user is None
            or challenge.user_id != user.id
            or user.status != UserStatus.ACTIVE.value
        ):
            challenge.status = OtpStatus.FAILED.value
            self.repo.commit()
            raise PasswordResetInvalidError()

        if user.password_hash and verify_password(new_password, user.password_hash):
            self.repo.commit()
            raise ValidationAuthError(
                message="New password must be different from current password",
                details={"field": "new_password"},
            )

        user.password_hash = hash_password(new_password)
        self.repo.expire_pending_password_resets(
            identifier_hash=challenge.identifier_hash,
            exclude_id=challenge.id,
        )
        challenge.status = OtpStatus.USED.value
        challenge.used_at = now

        sessions = self.repo.list_active_sessions_for_user(
            user_id=user.id,
            now=now,
        )
        for session in sessions:
            self.repo.revoke_active_refresh_tokens_for_session(
                session.id,
                revoked_at=now,
            )
            self.repo.revoke_session(session.id, revoked_at=now)

        self.repo.commit()
        return len(sessions)

    def _resolve_reset_identifier(
        self,
        identifier: str,
    ) -> tuple[str, str, AuthUser | None]:
        raw_identifier = identifier.strip()
        try:
            if "@" in raw_identifier:
                normalized = normalize_email(raw_identifier)
                return "email", normalized, self.repo.get_user_by_email(normalized)

            normalized_phone = normalize_iran_phone(raw_identifier)
            if normalized_phone is None:
                raise ValueError("Invalid phone number")
            return (
                "sms",
                normalized_phone,
                self.repo.get_user_by_phone(normalized_phone),
            )
        except ValueError as exc:
            raise ValidationAuthError(
                message="Enter a valid email address or Iranian phone number",
                details={"field": "identifier"},
            ) from exc

    def _deliver_password_reset_code(
        self,
        *,
        channel: str,
        destination: str,
        code: str,
    ) -> None:
        if self.settings.auth_dev_otp_enabled:
            return

        try:
            if channel == "email" and self._email_delivery_is_configured():
                envelope = build_email_envelope(
                    to=destination,
                    title="Farm Net password reset",
                    body=f"Your Farm Net password reset code is: {code}",
                    action_url=None,
                )
                SmtpEmailTransport(self.settings).send(envelope)
                return

            if channel == "sms" and self._sms_delivery_is_configured():
                message = build_sms_message(
                    to=destination,
                    title="Farm Net",
                    body=f"Password reset code: {code}",
                    action_url=None,
                )
                HttpJsonSmsTransport(self.settings).send(message)
        except (EmailProviderError, SmsProviderError) as exc:
            logger.warning(
                "Password reset delivery failed: %s",
                exc.code,
            )

    def _email_delivery_is_configured(self) -> bool:
        return bool(
            self.settings.email_enabled
            and self.settings.email_provider == "smtp"
            and self.settings.email_host.strip()
            and self.settings.email_from.strip()
            and not (
                self.settings.email_starttls and self.settings.email_use_ssl
            )
        )

    def _sms_delivery_is_configured(self) -> bool:
        parsed = urlparse(self.settings.sms_api_url)
        return bool(
            self.settings.sms_enabled
            and self.settings.sms_provider == "http_json"
            and parsed.scheme == "https"
            and parsed.netloc
            and self.settings.sms_api_key.strip()
            and self.settings.sms_sender.strip()
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

        access_token = create_access_token(
            subject=user.id,
            extra_claims={"sid": session.id},
        )
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

        return f"{secrets.randbelow(1_000_000):06d}"

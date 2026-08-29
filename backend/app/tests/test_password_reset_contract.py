from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

from app.main import app
from app.modules.auth.exceptions import PasswordResetInvalidError
from app.modules.auth.service import AuthService


class _PasswordResetRepository:
    def __init__(self) -> None:
        self.user = SimpleNamespace(
            id=7,
            email="farmer@example.com",
            phone="989121234567",
            password_hash="old-hash",
            status="active",
        )
        self.challenge = None
        self.sessions = [SimpleNamespace(id=11), SimpleNamespace(id=12)]
        self.revoked_sessions: list[int] = []
        self.revoked_token_families: list[int] = []
        self.commits = 0

    def get_user_by_email(self, email: str):
        return self.user if email == self.user.email else None

    def get_user_by_phone(self, phone: str):
        return self.user if phone == self.user.phone else None

    def expire_pending_password_resets(
        self,
        *,
        identifier_hash: str,
        exclude_id: int | None = None,
    ) -> int:
        return 0

    def create_password_reset_challenge(self, **kwargs):
        self.challenge = SimpleNamespace(
            id=1,
            status="pending",
            attempts=0,
            created_at=datetime.utcnow(),
            used_at=None,
            **kwargs,
        )
        return self.challenge

    def get_latest_pending_password_reset_for_update(
        self,
        *,
        identifier_hash: str,
    ):
        if self.challenge is None:
            return None
        if self.challenge.identifier_hash != identifier_hash:
            return None
        if self.challenge.status != "pending":
            return None
        return self.challenge

    def list_active_sessions_for_user(self, *, user_id: int, now: datetime):
        assert user_id == self.user.id
        return self.sessions

    def revoke_active_refresh_tokens_for_session(
        self,
        session_id: int,
        revoked_at: datetime,
    ) -> None:
        self.revoked_token_families.append(session_id)

    def revoke_session(self, session_id: int, revoked_at: datetime) -> None:
        self.revoked_sessions.append(session_id)

    def commit(self) -> None:
        self.commits += 1


def _service() -> tuple[AuthService, _PasswordResetRepository]:
    service = AuthService.__new__(AuthService)
    repository = _PasswordResetRepository()
    service.repo = repository
    service.settings = SimpleNamespace(
        auth_dev_otp_enabled=True,
        auth_dev_otp_code="111111",
        otp_expire_minutes=2,
        otp_max_attempts=5,
    )
    return service, repository


def test_password_reset_routes_are_publicly_exposed_and_rate_limited() -> None:
    paths = app.openapi()["paths"]
    assert "post" in paths["/api/v1/auth/password/reset/request"]
    assert "post" in paths["/api/v1/auth/password/reset/confirm"]


def test_password_reset_request_is_generic_for_an_unknown_account() -> None:
    service, repository = _service()

    result = service.request_password_reset(identifier="unknown@example.com")

    assert result.dev_code is None
    assert result.expires_in_seconds == 120
    assert repository.challenge is None


def test_password_reset_hashes_the_code_and_never_stores_it_plainly(
    monkeypatch,
) -> None:
    service, repository = _service()
    deliveries = []
    monkeypatch.setattr(
        service,
        "_deliver_password_reset_code",
        lambda **kwargs: deliveries.append(kwargs),
    )

    result = service.request_password_reset(identifier="Farmer@Example.com")

    assert result.dev_code == "111111"
    assert repository.challenge.code_hash != "111111"
    assert repository.challenge.channel == "email"
    assert deliveries == [
        {
            "channel": "email",
            "destination": "farmer@example.com",
            "code": "111111",
        }
    ]


def test_password_reset_rejects_an_invalid_code(monkeypatch) -> None:
    service, repository = _service()
    monkeypatch.setattr(service, "_deliver_password_reset_code", lambda **_: None)
    service.request_password_reset(identifier="farmer@example.com")

    with pytest.raises(PasswordResetInvalidError):
        service.confirm_password_reset(
            identifier="farmer@example.com",
            code="000000",
            new_password="new-password-123",
        )

    assert repository.challenge.attempts == 1
    assert repository.user.password_hash == "old-hash"


def test_password_reset_changes_password_and_revokes_every_session(
    monkeypatch,
) -> None:
    service, repository = _service()
    monkeypatch.setattr(service, "_deliver_password_reset_code", lambda **_: None)
    monkeypatch.setattr(
        "app.modules.auth.service.verify_password",
        lambda *_: False,
    )
    monkeypatch.setattr(
        "app.modules.auth.service.hash_password",
        lambda value: f"hashed:{value}",
    )
    service.request_password_reset(identifier="farmer@example.com")
    repository.challenge.expires_at = datetime.utcnow() + timedelta(minutes=2)

    revoked = service.confirm_password_reset(
        identifier="farmer@example.com",
        code="111111",
        new_password="new-password-123",
    )

    assert revoked == 2
    assert repository.user.password_hash == "hashed:new-password-123"
    assert repository.challenge.status == "used"
    assert repository.revoked_sessions == [11, 12]
    assert repository.revoked_token_families == [11, 12]

from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest
from fastapi.security import HTTPAuthorizationCredentials

from app.modules.auth.exceptions import TokenInvalidError
from app.modules.auth.service import AuthService


def active_user(user_id: int = 7):
    return SimpleNamespace(
        id=user_id,
        email="user@example.com",
        phone=None,
        status="active",
        is_email_verified=True,
        is_phone_verified=False,
    )


class RefreshRepository:
    def __init__(self, *, token_status: str = "active"):
        expires_at = datetime.utcnow() + timedelta(days=2)
        self.token = SimpleNamespace(
            user_id=7,
            session_id=11,
            status=token_status,
            expires_at=expires_at,
            revoked_at=None,
        )
        self.session = SimpleNamespace(
            id=11,
            user_id=7,
            status="active",
            expires_at=expires_at,
        )
        self.user = active_user()
        self.created = []
        self.revoked_sessions = []
        self.revoked_families = []
        self.commits = 0

    def get_refresh_token_by_hash_for_update(self, _token_hash):
        return self.token

    def get_session_by_id(self, _session_id):
        return self.session

    def get_user_by_id(self, _user_id):
        return self.user

    def revoke_refresh_token(self, token, revoked_at):
        token.status = "revoked"
        token.revoked_at = revoked_at

    def create_refresh_token(self, **kwargs):
        self.created.append(kwargs)

    def revoke_session(self, session_id, revoked_at):
        self.revoked_sessions.append((session_id, revoked_at))

    def revoke_active_refresh_tokens_for_session(self, session_id, revoked_at):
        self.revoked_families.append((session_id, revoked_at))

    def commit(self):
        self.commits += 1


def make_service(repo):
    service = AuthService.__new__(AuthService)
    service.repo = repo
    service.settings = SimpleNamespace(jwt_access_token_expire_minutes=30)
    return service


def test_refresh_rotates_token_and_binds_new_access_to_session(monkeypatch):
    repo = RefreshRepository()
    service = make_service(repo)
    access_calls = []
    refresh_calls = []
    monkeypatch.setattr(
        "app.modules.auth.service.decode_token",
        lambda _token: {"sub": "7", "sid": 11, "type": "refresh"},
    )
    monkeypatch.setattr(
        "app.modules.auth.service.create_access_token",
        lambda **kwargs: access_calls.append(kwargs) or "new-access",
    )
    monkeypatch.setattr(
        "app.modules.auth.service.create_refresh_token",
        lambda **kwargs: refresh_calls.append(kwargs) or "new-refresh",
    )

    result = service.refresh_access_token(refresh_token="old-refresh-token-value")

    assert result.access_token == "new-access"
    assert result.refresh_token == "new-refresh"
    assert repo.token.status == "revoked"
    assert repo.created[0]["session_id"] == 11
    assert access_calls[0]["extra_claims"] == {"sid": 11}
    assert refresh_calls[0]["extra_claims"] == {"sid": 11}
    assert repo.commits == 1


def test_refresh_replay_revokes_the_whole_session_family(monkeypatch):
    repo = RefreshRepository(token_status="revoked")
    service = make_service(repo)
    monkeypatch.setattr(
        "app.modules.auth.service.decode_token",
        lambda _token: {"sub": "7", "sid": 11, "type": "refresh"},
    )

    with pytest.raises(TokenInvalidError):
        service.refresh_access_token(refresh_token="replayed-refresh-token")

    assert repo.revoked_sessions[0][0] == 11
    assert repo.revoked_families[0][0] == 11
    assert repo.commits == 1


def test_refresh_rejects_claim_and_database_session_mismatch(monkeypatch):
    repo = RefreshRepository()
    service = make_service(repo)
    monkeypatch.setattr(
        "app.modules.auth.service.decode_token",
        lambda _token: {"sub": "7", "sid": 99, "type": "refresh"},
    )

    with pytest.raises(TokenInvalidError):
        service.refresh_access_token(refresh_token="mismatched-refresh-token")

    assert repo.created == []
    assert repo.commits == 0


def test_access_token_requires_an_active_matching_session(monkeypatch):
    from app.modules.auth import dependencies

    repository = SimpleNamespace(
        get_session_by_id=lambda _sid: SimpleNamespace(
            user_id=7,
            status="active",
            expires_at=datetime.utcnow() + timedelta(minutes=10),
        ),
        get_user_by_id=lambda _user_id: active_user(),
    )
    monkeypatch.setattr(
        dependencies,
        "decode_token",
        lambda _token: {"sub": "7", "sid": 11, "type": "access"},
    )
    monkeypatch.setattr(dependencies, "AuthRepository", lambda _db: repository)

    user = dependencies.get_current_user(
        credentials=HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="access-token",
        ),
        db=object(),
    )

    assert user.id == 7


@pytest.mark.parametrize("status", ["revoked", "expired"])
def test_access_token_is_rejected_after_session_closes(monkeypatch, status):
    from app.modules.auth import dependencies

    repository = SimpleNamespace(
        get_session_by_id=lambda _sid: SimpleNamespace(
            user_id=7,
            status=status,
            expires_at=datetime.utcnow() + timedelta(minutes=10),
        )
    )
    monkeypatch.setattr(
        dependencies,
        "decode_token",
        lambda _token: {"sub": "7", "sid": 11, "type": "access"},
    )
    monkeypatch.setattr(dependencies, "AuthRepository", lambda _db: repository)

    with pytest.raises(TokenInvalidError):
        dependencies.get_current_user(
            credentials=HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials="access-token",
            ),
            db=object(),
        )

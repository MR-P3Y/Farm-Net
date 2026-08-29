from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

from app.main import app
from app.modules.auth.exceptions import CurrentPasswordInvalidError, ValidationAuthError
from app.modules.auth.service import AuthService


def _session(session_id: int, *, user_id: int = 7):
    now = datetime.utcnow()
    return SimpleNamespace(
        id=session_id,
        user_id=user_id,
        status="active",
        ip_address="127.0.0.1",
        user_agent="FarmNet test client",
        created_at=now - timedelta(days=1),
        last_seen_at=now,
        expires_at=now + timedelta(days=5),
    )


class _SecurityRepository:
    def __init__(self) -> None:
        self.sessions = [_session(11), _session(12), _session(13)]
        self.revoked_sessions: list[int] = []
        self.revoked_token_families: list[int] = []
        self.commits = 0

    def list_active_sessions_for_user(self, *, user_id: int, now: datetime):
        assert user_id == 7
        assert now <= datetime.utcnow()
        return [
            session
            for session in self.sessions
            if session.id not in self.revoked_sessions
        ]

    def get_session_by_id_for_user(self, *, session_id: int, user_id: int):
        return next(
            (
                session
                for session in self.sessions
                if session.id == session_id and session.user_id == user_id
            ),
            None,
        )

    def revoke_active_refresh_tokens_for_session(
        self,
        session_id: int,
        revoked_at: datetime,
    ) -> None:
        assert revoked_at <= datetime.utcnow()
        self.revoked_token_families.append(session_id)

    def revoke_session(self, session_id: int, revoked_at: datetime) -> None:
        assert revoked_at <= datetime.utcnow()
        self.revoked_sessions.append(session_id)

    def commit(self) -> None:
        self.commits += 1


def _service() -> tuple[AuthService, _SecurityRepository]:
    service = AuthService.__new__(AuthService)
    repository = _SecurityRepository()
    service.repo = repository
    return service, repository


def _user():
    return SimpleNamespace(id=7, password_hash="old-hash")


def test_account_security_routes_are_exposed() -> None:
    paths = app.openapi()["paths"]
    assert "get" in paths["/api/v1/auth/sessions"]
    assert "delete" in paths["/api/v1/auth/sessions/{session_id}"]
    assert "post" in paths["/api/v1/auth/sessions/revoke-others"]
    assert "post" in paths["/api/v1/auth/password/change"]


def test_session_list_marks_only_the_access_token_session_as_current() -> None:
    service, _repository = _service()

    result = service.list_my_sessions(user=_user(), current_session_id=12)

    assert [item.id for item in result if item.is_current] == [12]


def test_current_session_cannot_be_revoked_through_remote_revoke() -> None:
    service, repository = _service()

    with pytest.raises(ValidationAuthError):
        service.revoke_my_session(
            user=_user(),
            session_id=11,
            current_session_id=11,
        )

    assert repository.revoked_sessions == []


def test_revoke_others_preserves_current_session_and_revokes_token_families() -> None:
    service, repository = _service()

    count = service.revoke_my_other_sessions(user=_user(), current_session_id=12)

    assert count == 2
    assert repository.revoked_sessions == [11, 13]
    assert repository.revoked_token_families == [11, 13]
    assert repository.commits == 1


def test_password_change_requires_the_current_password(monkeypatch) -> None:
    service, repository = _service()
    monkeypatch.setattr("app.modules.auth.service.verify_password", lambda *_: False)

    with pytest.raises(CurrentPasswordInvalidError):
        service.change_my_password(
            user=_user(),
            current_password="wrong-password",
            new_password="new-password-123",
            current_session_id=11,
        )

    assert repository.commits == 0


def test_password_change_hashes_new_value_and_revokes_other_sessions(monkeypatch) -> None:
    service, repository = _service()
    checks = iter([True, False])
    monkeypatch.setattr(
        "app.modules.auth.service.verify_password",
        lambda *_: next(checks),
    )
    monkeypatch.setattr(
        "app.modules.auth.service.hash_password",
        lambda value: f"hashed:{value}",
    )
    user = _user()

    count = service.change_my_password(
        user=user,
        current_password="old-password",
        new_password="new-password-123",
        current_session_id=11,
    )

    assert count == 2
    assert user.password_hash == "hashed:new-password-123"
    assert repository.revoked_sessions == [12, 13]
    assert repository.commits == 1

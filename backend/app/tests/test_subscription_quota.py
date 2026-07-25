from datetime import UTC, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.core.exceptions import AppException
from app.modules.subscriptions.quota_service import QuotaService


class _QuotaRepo:
    def __init__(self, *, limit: Decimal | None = Decimal("5")) -> None:
        self.entitlement = SimpleNamespace(
            is_enabled=True,
            is_unlimited=limit is None,
            limit_value=limit,
            feature_code_snapshot="ai.text_chat",
        )
        self.usage = SimpleNamespace(
            id=7,
            entitlement=self.entitlement,
            used_value=Decimal("0"),
            reserved_value=Decimal("0"),
            version=1,
        )
        self.rows: list[object] = []
        self.commits = 0

    def current_usage(self, user_id, feature_code, now, *, lock):
        if user_id == 3 and feature_code == "ai.text_chat":
            return self.usage
        return None

    def reservation_by_key(self, key, *, lock):
        return next((row for row in self.rows if row.idempotency_key == key), None)

    def reservation_by_id(self, reservation_id, *, lock):
        return next((row for row in self.rows if row.id == reservation_id), None)

    def expired_for_usage(self, usage_id, now):
        return [
            row
            for row in self.rows
            if row.usage_id == usage_id and row.status == "reserved" and row.expires_at <= now
        ]

    def due_reservations(self, now, limit):
        return [
            row for row in self.rows if row.status == "reserved" and row.expires_at <= now
        ][:limit]

    def usage_by_id(self, usage_id, *, lock):
        return self.usage if usage_id == self.usage.id else None

    def add(self, row):
        row.id = len(self.rows) + 1
        self.rows.append(row)

    def flush(self):
        return None

    def commit(self):
        self.commits += 1

    def rollback(self):
        return None


def _service(repo: _QuotaRepo) -> QuotaService:
    return QuotaService(SimpleNamespace(), repo=repo)  # type: ignore[arg-type]


def test_estimate_does_not_mutate_usage() -> None:
    repo = _QuotaRepo(limit=Decimal("5"))
    result = _service(repo).estimate(3, "ai.text_chat", Decimal("2"))

    assert result.allowed is True
    assert result.remaining_before == Decimal("5")
    assert result.remaining_after == Decimal("3")
    assert repo.usage.reserved_value == Decimal("0")
    assert repo.commits == 0


def test_reserve_replay_is_idempotent_and_finalize_is_exact_once() -> None:
    repo = _QuotaRepo(limit=Decimal("5"))
    service = _service(repo)

    first = service.reserve(3, "ai.text_chat", Decimal("2"), "request-0001")
    replay = service.reserve(3, "ai.text_chat", Decimal("2"), "request-0001")
    finalized = service.finalize(3, first.id)
    finalized_replay = service.finalize(3, first.id)

    assert replay.id == first.id
    assert finalized.status == finalized_replay.status == "finalized"
    assert repo.usage.reserved_value == Decimal("0")
    assert repo.usage.used_value == Decimal("2.0000")
    assert len(repo.rows) == 1


def test_idempotency_key_rejects_different_payload() -> None:
    repo = _QuotaRepo()
    service = _service(repo)
    service.reserve(3, "ai.text_chat", Decimal("1"), "request-0002")

    with pytest.raises(AppException) as caught:
        service.reserve(3, "ai.text_chat", Decimal("2"), "request-0002")

    assert caught.value.code == "BILLING_IDEMPOTENCY_CONFLICT"
    assert caught.value.status_code == 409


def test_limit_includes_reserved_usage_and_release_is_idempotent() -> None:
    repo = _QuotaRepo(limit=Decimal("2"))
    service = _service(repo)
    reservation = service.reserve(3, "ai.text_chat", Decimal("2"), "request-0003")

    with pytest.raises(AppException) as caught:
        service.reserve(3, "ai.text_chat", Decimal("1"), "request-0004")
    assert caught.value.code == "BILLING_QUOTA_EXCEEDED"

    released = service.release(3, reservation.id, "upstream_failed")
    replay = service.release(3, reservation.id, "ignored_on_replay")
    assert released.status == replay.status == "released"
    assert repo.usage.reserved_value == Decimal("0")
    assert repo.usage.used_value == Decimal("0")


def test_expired_reservation_is_reclaimed_before_new_reserve() -> None:
    repo = _QuotaRepo(limit=Decimal("2"))
    service = _service(repo)
    expired = service.reserve(3, "ai.text_chat", Decimal("2"), "request-0005")
    repo.rows[0].expires_at = datetime.now(UTC).replace(tzinfo=None) - timedelta(seconds=1)

    current = service.reserve(3, "ai.text_chat", Decimal("2"), "request-0006")

    assert expired.id != current.id
    assert repo.rows[0].status == "expired"
    assert repo.usage.reserved_value == Decimal("2.0000")


def test_owner_boundary_hides_foreign_reservation() -> None:
    repo = _QuotaRepo()
    service = _service(repo)
    reservation = service.reserve(3, "ai.text_chat", Decimal("1"), "request-0007")

    with pytest.raises(AppException) as caught:
        service.finalize(4, reservation.id)

    assert caught.value.code == "BILLING_QUOTA_RESERVATION_NOT_FOUND"
    assert caught.value.status_code == 404

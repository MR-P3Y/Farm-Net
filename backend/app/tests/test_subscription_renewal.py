from datetime import datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock

from app.modules.notifications.enums import NotificationEventType
from app.modules.subscriptions.renewal_service import (
    PAID_GRACE_DAYS,
    SubscriptionRenewalService,
)


class _Query:
    def __init__(self) -> None:
        self.updated: dict = {}

    def filter(self, *args):
        return self

    def update(self, values, synchronize_session=False):
        self.updated = values
        return 1


class _Db:
    def __init__(self) -> None:
        self.added: list[object] = []
        self.query_result = _Query()

    def add(self, row) -> None:
        if getattr(row, "id", None) is None:
            row.id = len(self.added) + 100
        self.added.append(row)

    def flush(self) -> None:
        return None

    def query(self, *args):
        return self.query_result


def _subscription(*, period: str, status: str = "active"):
    plan = SimpleNamespace(
        code="free" if period == "free" else "farmer_plus",
        version=1,
        billing_period=period,
        price_toman=Decimal("0" if period == "free" else "250000"),
        currency="TOMAN",
        features=[],
    )
    return SimpleNamespace(
        id=10,
        user_id=7,
        plan=plan,
        status=status,
        current_period_starts_at=None,
        current_period_ends_at=None,
        grace_ends_at=None,
        cancel_at_period_end=False,
        cancelled_at=None,
        ended_at=None,
        auto_renew=True,
        version=1,
    )


def _period(now: datetime):
    return SimpleNamespace(
        id=20,
        sequence=1,
        status="active",
        starts_at=now - timedelta(days=30),
        ends_at=now,
    )


def _service():
    db = _Db()
    notifier = Mock()
    service = SubscriptionRenewalService(db, notifier=notifier)  # type: ignore[arg-type]
    return service, db, notifier


def test_free_renewal_creates_next_period_and_exact_event_key() -> None:
    service, db, notifier = _service()
    now = datetime(2026, 7, 26, 3, 0, 0)
    subscription = _subscription(period="free")
    period = _period(now)

    service._renew_free(subscription, period, now)

    next_period = db.added[0]
    assert period.status == "closed"
    assert next_period.sequence == 2
    assert next_period.status == "active"
    assert subscription.current_period_starts_at == now
    assert subscription.current_period_ends_at == now + timedelta(days=30)
    call = notifier.create_event_and_notify_user.call_args.kwargs
    assert call["event_type"] == NotificationEventType.SUBSCRIPTION_RENEWED.value
    assert call["event_key"] == "subscription:10:period:2:subscription.renewed"
    assert call["commit"] is False


def test_paid_period_enters_three_day_grace_and_extends_entitlement_access() -> None:
    service, db, notifier = _service()
    now = datetime(2026, 7, 26, 3, 0, 0)
    subscription = _subscription(period="monthly")
    period = _period(now)

    service._enter_grace(subscription, period, now)

    assert subscription.status == "grace"
    assert subscription.grace_ends_at == now + timedelta(days=PAID_GRACE_DAYS)
    assert period.status == "closed"
    assert db.query_result.updated
    call = notifier.create_event_and_notify_user.call_args.kwargs
    assert call["event_type"] == NotificationEventType.SUBSCRIPTION_GRACE_STARTED.value
    assert call["event_key"] == "subscription:10:period:1:subscription.grace_started"


def test_cancel_at_period_end_is_terminal_without_grace() -> None:
    service, _, notifier = _service()
    now = datetime(2026, 7, 26, 3, 0, 0)
    subscription = _subscription(period="monthly")
    subscription.cancel_at_period_end = True
    period = _period(now)

    service._cancel(subscription, period, now)

    assert subscription.status == "cancelled"
    assert subscription.ended_at == now
    assert subscription.auto_renew is False
    assert notifier.create_event_and_notify_user.call_args.kwargs[
        "event_type"
    ] == NotificationEventType.SUBSCRIPTION_CANCELLED.value


def test_grace_expiry_terminates_access_and_notifies_once_key() -> None:
    service, db, notifier = _service()
    now = datetime(2026, 7, 29, 3, 0, 0)
    subscription = _subscription(period="monthly", status="grace")
    subscription.grace_ends_at = now
    period = _period(now - timedelta(days=3))

    service._expire(subscription, period, now)

    assert subscription.status == "expired"
    assert subscription.ended_at == now
    assert subscription.auto_renew is False
    assert db.query_result.updated
    call = notifier.create_event_and_notify_user.call_args.kwargs
    assert call["event_type"] == NotificationEventType.SUBSCRIPTION_EXPIRED.value
    assert call["event_key"] == "subscription:10:period:1:subscription.expired"


def test_subscription_lifecycle_event_types_are_registered() -> None:
    values = {item.value for item in NotificationEventType}
    assert {
        "subscription.activated",
        "subscription.renewed",
        "subscription.grace_started",
        "subscription.cancelled",
        "subscription.expired",
    }.issubset(values)

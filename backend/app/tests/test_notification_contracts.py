from types import SimpleNamespace
from unittest.mock import Mock

from sqlalchemy import UniqueConstraint

from app.modules.notifications.enums import NotificationDeliveryStatus
from app.modules.notifications.models import (
    Notification,
    NotificationDeliveryLog,
    NotificationPreference,
)
from app.modules.notifications.service import NotificationService


def test_notification_exact_once_constraints_are_registered() -> None:
    notification_unique = {
        tuple(constraint.columns.keys())
        for constraint in Notification.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    delivery_unique = {
        tuple(constraint.columns.keys())
        for constraint in NotificationDeliveryLog.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }

    assert ("event_id", "recipient_user_id", "channel") in notification_unique
    assert ("notification_id", "channel") in delivery_unique


def test_notification_preference_scope_is_unique() -> None:
    preference_unique = {
        tuple(constraint.columns.keys())
        for constraint in NotificationPreference.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }

    assert ("user_id", "event_type", "channel") in preference_unique


def test_delivery_retry_contract_defaults_are_explicit() -> None:
    assert NotificationDeliveryLog.__table__.c.attempt_count.default.arg == 0
    assert NotificationDeliveryLog.__table__.c.max_attempts.default.arg == 5
    assert NotificationDeliveryStatus.PROCESSING.value == "processing"
    assert "next_attempt_at" in NotificationDeliveryLog.__table__.columns
    assert "last_attempt_at" in NotificationDeliveryLog.__table__.columns
    assert "locked_at" in NotificationDeliveryLog.__table__.columns


def test_source_event_key_is_deterministic_and_payload_sensitive() -> None:
    service = NotificationService.__new__(NotificationService)

    first = service._generate_event_key(
        event_type="social.comment_created",
        source_type="social_post",
        source_id="7",
        payload_json={"comment_id": 11, "post_id": 7},
    )
    retry = service._generate_event_key(
        event_type="social.comment_created",
        source_type="social_post",
        source_id="7",
        payload_json={"post_id": 7, "comment_id": 11},
    )
    another_comment = service._generate_event_key(
        event_type="social.comment_created",
        source_type="social_post",
        source_id="7",
        payload_json={"comment_id": 12, "post_id": 7},
    )

    assert first == retry
    assert first != another_comment
    assert len(first) <= 80


def test_source_less_event_key_remains_unique() -> None:
    service = NotificationService.__new__(NotificationService)

    first = service._generate_event_key(
        event_type="system.message",
        source_type=None,
        source_id=None,
        payload_json=None,
    )
    second = service._generate_event_key(
        event_type="system.message",
        source_type=None,
        source_id=None,
        payload_json=None,
    )

    assert first != second


def test_self_notification_is_suppressed_before_database_work() -> None:
    service = NotificationService.__new__(NotificationService)

    result = service.create_event_and_notify_user(
        event_type="order.created",
        recipient_user_id=42,
        actor_user_id=42,
        title="Created",
        body="Created",
    )

    assert result is None


def routing_service(
    *, recipient: SimpleNamespace, preferences: list[SimpleNamespace]
) -> NotificationService:
    service = NotificationService.__new__(NotificationService)
    service.repo = Mock()
    service.repo.get_recipient.return_value = recipient
    service.repo.list_routing_preferences.return_value = preferences
    return service


def test_routing_defaults_to_in_app_only() -> None:
    service = routing_service(
        recipient=SimpleNamespace(
            email="user@example.com",
            phone="09120000000",
            is_email_verified=True,
            is_phone_verified=True,
        ),
        preferences=[],
    )

    assert service.resolve_channels(user_id=1, event_type="order.created") == [
        "in_app"
    ]


def test_event_preference_overrides_global_and_requires_verified_destination() -> None:
    service = routing_service(
        recipient=SimpleNamespace(
            email="user@example.com",
            phone="09120000000",
            is_email_verified=True,
            is_phone_verified=False,
        ),
        preferences=[
            SimpleNamespace(event_type="*", channel="email", is_enabled=True),
            SimpleNamespace(event_type="*", channel="sms", is_enabled=True),
            SimpleNamespace(event_type="*", channel="push", is_enabled=True),
            SimpleNamespace(
                event_type="payment.failed", channel="email", is_enabled=False
            ),
        ],
    )

    assert service.resolve_channels(user_id=1, event_type="order.created") == [
        "in_app",
        "email",
    ]
    assert service.resolve_channels(user_id=1, event_type="payment.failed") == [
        "in_app"
    ]

from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import Mock

from sqlalchemy import UniqueConstraint

from app.core.config import Settings
from app.modules.notifications.email_dispatcher import EmailDeliveryDispatcher
from app.modules.notifications.email_provider import build_email_envelope
from app.modules.notifications.sms_dispatcher import SmsDeliveryDispatcher
from app.modules.notifications.sms_provider import build_sms_message
from app.modules.notifications.enums import NotificationDeliveryStatus
from app.modules.notifications.delivery_service import NotificationDeliveryService
from app.modules.notifications.models import (
    Notification,
    NotificationDeliveryLog,
    NotificationDeliveryAttempt,
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


def test_delivery_attempt_number_is_unique_per_delivery() -> None:
    attempt_unique = {
        tuple(constraint.columns.keys())
        for constraint in NotificationDeliveryAttempt.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }

    assert ("delivery_log_id", "attempt_number") in attempt_unique


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


def delivery_row(**overrides):
    values = {
        "id": 9,
        "notification_id": 7,
        "channel": "email",
        "provider": None,
        "provider_message_id": None,
        "status": "pending",
        "error_code": None,
        "error_message": None,
        "attempt_count": 0,
        "max_attempts": 3,
        "next_attempt_at": None,
        "last_attempt_at": None,
        "locked_at": None,
        "sent_at": None,
        "delivered_at": None,
        "created_at": datetime.now(UTC),
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_claim_creates_monotonic_processing_attempt() -> None:
    service = NotificationDeliveryService.__new__(NotificationDeliveryService)
    service.repo = Mock()
    row = delivery_row()
    service.repo.claim_ready_deliveries.return_value = [row]

    claimed = service.claim_ready(limit=1)

    assert len(claimed) == 1
    assert row.status == "processing"
    assert row.attempt_count == 1
    attempt = service.repo.add_delivery_attempt.call_args.args[0]
    assert attempt.delivery_log_id == 9
    assert attempt.attempt_number == 1
    assert attempt.status == "processing"
    service.repo.commit.assert_called_once()


def test_failure_uses_exponential_backoff_and_terminal_limit() -> None:
    service = NotificationDeliveryService.__new__(NotificationDeliveryService)
    service.repo = Mock()
    service.get_detail = Mock(return_value="detail")
    attempt = SimpleNamespace(
        finished_at=None,
        status="processing",
        provider=None,
        error_code=None,
        error_message=None,
    )
    service.repo.get_delivery_attempt.return_value = attempt

    retryable = delivery_row(status="processing", attempt_count=2, max_attempts=3)
    service.repo.get_delivery_log.return_value = retryable
    before_failure = datetime.now(UTC)
    service.record_failure(
        delivery_log_id=9,
        error_code="timeout",
        error_message="Timed out",
        base_delay_seconds=10,
    )
    assert retryable.status == "pending"
    assert retryable.next_attempt_at is not None
    retry_delay = (retryable.next_attempt_at - before_failure).total_seconds()
    assert 19 <= retry_delay <= 21

    terminal = delivery_row(status="processing", attempt_count=3, max_attempts=3)
    service.repo.get_delivery_log.return_value = terminal
    attempt.finished_at = None
    service.record_failure(
        delivery_log_id=9,
        error_code="rejected",
        error_message="Rejected",
    )
    assert terminal.status == "failed"
    assert terminal.next_attempt_at is None


def test_stale_worker_lease_closes_attempt_before_reclaim() -> None:
    service = NotificationDeliveryService.__new__(NotificationDeliveryService)
    service.repo = Mock()
    row = delivery_row(status="processing", attempt_count=1, max_attempts=3)
    stale_attempt = SimpleNamespace(
        finished_at=None,
        status="processing",
        error_code=None,
        error_message=None,
    )
    service.repo.claim_ready_deliveries.return_value = [row]
    service.repo.get_delivery_attempt.return_value = stale_attempt

    claimed = service.claim_ready(limit=1)

    assert len(claimed) == 1
    assert stale_attempt.status == "failed"
    assert stale_attempt.error_code == "lease_expired"
    assert stale_attempt.finished_at is not None
    assert row.status == "processing"
    assert row.attempt_count == 2


def email_settings(**overrides) -> Settings:
    values = {
        "database_url": "mysql+pymysql://unused",
        "email_enabled": True,
        "email_provider": "smtp",
        "email_host": "smtp.example.com",
        "email_from": "no-reply@example.com",
    }
    values.update(overrides)
    return Settings(**values)


def test_email_dispatcher_is_fail_closed_when_disabled() -> None:
    dispatcher = EmailDeliveryDispatcher(
        None,
        settings=email_settings(email_enabled=False),
        transport=Mock(),
    )
    dispatcher.delivery = Mock()

    result = dispatcher.run_once()

    assert result.disabled is True
    dispatcher.delivery.claim_ready.assert_not_called()


def test_email_dispatcher_sends_only_verified_target_through_transport() -> None:
    transport = Mock()
    transport.send.return_value = "message-1"
    dispatcher = EmailDeliveryDispatcher(
        None,
        settings=email_settings(),
        transport=transport,
    )
    dispatcher.delivery = Mock()
    dispatcher.repo = Mock()
    dispatcher.delivery.claim_ready.return_value = [SimpleNamespace(id=5)]
    dispatcher.repo.get_delivery_target.return_value = (
        SimpleNamespace(id=5),
        SimpleNamespace(title="Alert", body="Body", action_url="/orders/1"),
        SimpleNamespace(email="verified@example.com", is_email_verified=True),
    )

    result = dispatcher.run_once(limit=1)

    assert result.sent == 1
    envelope = transport.send.call_args.args[0]
    assert envelope.to == "verified@example.com"
    dispatcher.delivery.record_success.assert_called_once_with(
        delivery_log_id=5,
        provider="smtp",
        provider_message_id="message-1",
    )


def test_email_envelope_escapes_html_content() -> None:
    envelope = build_email_envelope(
        to="user@example.com",
        title="Title",
        body="<script>alert(1)</script>",
        action_url='https://example.com/?q="unsafe"',
    )

    assert "<script>" not in envelope.html_body
    assert "&lt;script&gt;" in envelope.html_body
    assert "&quot;unsafe&quot;" in envelope.html_body


def sms_settings(**overrides) -> Settings:
    values = {
        "database_url": "mysql+pymysql://unused",
        "sms_enabled": True,
        "sms_provider": "http_json",
        "sms_api_url": "https://sms.example.com/send",
        "sms_api_key": "test-key",
        "sms_sender": "FarmNet",
    }
    values.update(overrides)
    return Settings(**values)


def test_sms_dispatcher_is_fail_closed_when_disabled() -> None:
    dispatcher = SmsDeliveryDispatcher(
        None, settings=sms_settings(sms_enabled=False), transport=Mock()
    )
    dispatcher.delivery = Mock()

    result = dispatcher.run_once()

    assert result.disabled is True
    dispatcher.delivery.claim_ready.assert_not_called()


def test_sms_dispatcher_uses_verified_phone_and_fake_transport() -> None:
    transport = Mock()
    transport.send.return_value = "sms-1"
    dispatcher = SmsDeliveryDispatcher(None, settings=sms_settings(), transport=transport)
    dispatcher.delivery = Mock()
    dispatcher.repo = Mock()
    dispatcher.delivery.claim_ready.return_value = [SimpleNamespace(id=6)]
    dispatcher.repo.get_delivery_target.return_value = (
        SimpleNamespace(id=6),
        SimpleNamespace(title="Alert", body="Body", action_url="/orders/1"),
        SimpleNamespace(phone="09120000000", is_phone_verified=True),
    )

    result = dispatcher.run_once(limit=1)

    assert result.sent == 1
    assert transport.send.call_args.args[0].to == "09120000000"
    dispatcher.delivery.record_success.assert_called_once_with(
        delivery_log_id=6,
        provider="http_json",
        provider_message_id="sms-1",
    )


def test_sms_message_drops_unsafe_url_and_enforces_length() -> None:
    message = build_sms_message(
        to="09120000000",
        title="Title",
        body="x" * 600,
        action_url="javascript:alert(1)",
    )

    assert len(message.body) == 480
    assert "javascript:" not in message.body

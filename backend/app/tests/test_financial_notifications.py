from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.modules.auth.exceptions import ValidationAuthError
from app.modules.finance.settlement_service import SettlementService
from app.modules.notifications.enums import NotificationEventType
from app.modules.notifications.schemas import NotificationEventCreateIn
from app.modules.notifications.service import NotificationService


def test_financial_event_vocabulary_is_explicit() -> None:
    values = {item.value for item in NotificationEventType}
    assert {
        "finance.refund_requested", "finance.refund_completed",
        "finance.settlement_requested", "finance.settlement_approved",
        "finance.settlement_rejected", "finance.settlement_simulated",
        "finance.wallet_adjusted",
    } <= values


@pytest.mark.parametrize(
    "field", ["merchant_id", "authority", "card_pan", "card_hash",
              "idempotency_key", "provider_reference", "admin_note"]
)
def test_financial_notification_rejects_sensitive_payload_fields(field: str) -> None:
    service = NotificationService(MagicMock())
    service.repo = MagicMock()
    with pytest.raises(ValidationAuthError) as error:
        service.create_event(
            payload=NotificationEventCreateIn(
                event_type="finance.refund_completed",
                source_type="finance_refund", source_id="1",
                payload_json={"nested": {field: "secret-value"}},
            )
        )
    assert error.value.details["error_code"] == "FINANCIAL_NOTIFICATION_PRIVACY"


def test_settlement_notification_contains_only_safe_owner_fields(monkeypatch) -> None:
    notifier = MagicMock()
    monkeypatch.setattr(
        "app.modules.finance.settlement_service.NotificationService",
        lambda _db: notifier,
    )
    row = SimpleNamespace(
        id=4, requester_user_id=30, status="approved", currency="TOMAN",
        amount=1000, note="private", admin_note="private",
    )
    service = SettlementService(MagicMock())
    service._notify(
        row=row,
        event_type=NotificationEventType.SETTLEMENT_APPROVED.value,
        title="Approved", body="Approved", actor_user_id=9,
    )
    call = notifier.create_event_and_notify_user.call_args.kwargs
    assert call["recipient_user_id"] == 30
    assert call["payload_json"] == {
        "settlement_id": 4, "status": "approved", "currency": "TOMAN"
    }
    assert "amount" not in call["payload_json"]
    assert "admin_note" not in call["payload_json"]

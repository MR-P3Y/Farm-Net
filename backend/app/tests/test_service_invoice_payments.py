from datetime import UTC, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError
from sqlalchemy import CheckConstraint, Index

from app.core.exceptions import AppException
from app.main import app
from app.modules.finance.enums import BillingPaymentAttemptStatus
from app.modules.finance.final_price_service import (
    FinalPriceContractError,
    FinalPriceService,
)
from app.modules.finance.models import BillingPaymentAttempt
from app.modules.finance.payment_service import BillingInvoicePaymentService
from app.modules.finance.schemas import (
    InvoicePaymentCheckoutIn,
    InvoicePaymentVerifyIn,
)
from app.modules.finance.settlement_service import LedgerMovementService


def _constraint_names(model, kind) -> set[str]:
    return {
        item.name for item in model.__table__.constraints if isinstance(item, kind) and item.name
    }


def test_billing_payment_attempt_has_bounded_financial_contract() -> None:
    assert BillingPaymentAttempt.__tablename__ == "finance_billing_payment_attempts"
    checks = _constraint_names(BillingPaymentAttempt, CheckConstraint)
    assert {
        "ck_billing_payment_attempt_provider",
        "ck_billing_payment_attempt_status",
        "ck_billing_payment_attempt_amount",
        "ck_billing_payment_attempt_currency",
    } <= checks
    indexes = {
        item.name for item in BillingPaymentAttempt.__table__.indexes if isinstance(item, Index)
    }
    assert {
        "ix_billing_payment_attempt_user_status",
        "ix_billing_payment_attempt_invoice_status",
    } <= indexes


def test_service_invoice_payment_routes_are_explicit() -> None:
    paths = app.openapi()["paths"]
    assert "post" in paths["/api/v1/finance/invoices/{invoice_id}/checkout"]
    assert "post" in paths["/api/v1/finance/payments/verify"]
    assert "get" in paths["/api/v1/finance/payments/callback/zarinpal"]


def test_payment_inputs_reject_unknown_provider_and_short_keys() -> None:
    valid = InvoicePaymentCheckoutIn(
        provider="mock",
        idempotency_key="service-payment-1",
    )
    assert valid.provider == "mock"
    assert (
        InvoicePaymentVerifyIn(
            payment_attempt_id=1,
            provider_token="approved",
        ).payment_attempt_id
        == 1
    )

    with pytest.raises(ValidationError):
        InvoicePaymentCheckoutIn(provider="unknown", idempotency_key="short")
    with pytest.raises(ValidationError):
        InvoicePaymentVerifyIn(payment_attempt_id=0, provider_token="")


def test_checkout_idempotency_replay_is_owner_and_provider_scoped() -> None:
    existing = SimpleNamespace(invoice_id=8, user_id=20, provider="mock")
    service = BillingInvoicePaymentService(MagicMock())
    service._attempt_by_key = MagicMock(return_value=existing)
    service.output = MagicMock(return_value="replayed")

    assert (
        service.checkout(
            invoice_id=8,
            user_id=20,
            provider="mock",
            idempotency_key="service-payment-1",
        )
        == "replayed"
    )
    with pytest.raises(AppException, match="conflicts with another request"):
        service.checkout(
            invoice_id=8,
            user_id=21,
            provider="mock",
            idempotency_key="service-payment-1",
        )


def test_successful_payment_verification_is_idempotent() -> None:
    attempt = SimpleNamespace(status=BillingPaymentAttemptStatus.SUCCEEDED.value)
    service = BillingInvoicePaymentService(MagicMock())
    service._attempt_for_user = MagicMock(return_value=attempt)
    service.output = MagicMock(return_value="already-paid")

    assert (
        service.verify(attempt_id=4, user_id=20, provider_token="same-reference") == "already-paid"
    )
    service.output.assert_called_once_with(attempt)


def test_final_price_requires_paid_invoice_before_work_starts() -> None:
    db = MagicMock()
    service = FinalPriceService(db)
    service.require_accepted = MagicMock(return_value=SimpleNamespace(id=1))
    invoice = SimpleNamespace(status="payment_pending")
    query = MagicMock()
    query.filter.return_value.with_for_update.return_value.one_or_none.return_value = invoice
    db.query.return_value = query

    with pytest.raises(FinalPriceContractError, match="Paid invoice"):
        service.require_paid(source_type="service_request", source_id=9)

    invoice.status = "paid"
    assert service.require_paid(source_type="service_request", source_id=9) is invoice


def test_verified_service_payment_posts_pending_provider_ledger(monkeypatch) -> None:
    now = datetime.now(UTC).replace(tzinfo=None)
    attempt = SimpleNamespace(
        id=4,
        invoice_id=8,
        user_id=20,
        provider="mock",
        status=BillingPaymentAttemptStatus.REDIRECTED.value,
        amount_toman=Decimal("1000"),
        currency="TOMAN",
        expires_at=now + timedelta(minutes=10),
        provider_authority=None,
        provider_reference=None,
        verified_at=None,
        failure_code=None,
        failure_message=None,
    )
    invoice = SimpleNamespace(
        id=8,
        source_type="service_request",
        source_id=12,
        payer_user_id=20,
        provider_user_id=30,
        status="payment_pending",
        currency="TOMAN",
        total_amount=Decimal("1000"),
        provider_amount=Decimal("900"),
        platform_amount=Decimal("100"),
        paid_at=None,
    )
    db = MagicMock()
    service = BillingInvoicePaymentService(db)
    service._attempt_for_user = MagicMock(return_value=attempt)
    service._invoice_for_attempt = MagicMock(return_value=invoice)
    service._notify_paid = MagicMock()
    service.output = MagicMock(return_value="paid-output")
    ledger = MagicMock()
    monkeypatch.setattr(
        "app.modules.finance.payment_service.get_settings",
        lambda: SimpleNamespace(app_env="test"),
    )
    monkeypatch.setattr(
        "app.modules.finance.payment_service.LedgerMovementService",
        lambda _db: ledger,
    )

    assert (
        service.verify(attempt_id=attempt.id, user_id=20, provider_token="approved")
        == "paid-output"
    )
    assert attempt.status == "succeeded"
    assert invoice.status == "paid"
    ledger.post_billable_invoice_payment.assert_called_once_with(
        invoice=invoice,
        actor_user_id=20,
        trace_id="billing-payment:4",
    )
    service._notify_paid.assert_called_once_with(invoice=invoice, actor_user_id=20)
    db.commit.assert_called_once()


@pytest.mark.parametrize(
    ("source_type", "requester_url", "provider_url"),
    [
        (
            "service_request",
            "/services/requests/12",
            "/services/workbench/requests/12",
        ),
        (
            "consultation_request",
            "/consultants/requests/12",
            "/consultants/workbench/requests/12",
        ),
    ],
)
def test_paid_notifications_use_role_specific_private_details(
    monkeypatch,
    source_type: str,
    requester_url: str,
    provider_url: str,
) -> None:
    notifier = MagicMock()
    monkeypatch.setattr(
        "app.modules.finance.payment_service.NotificationService",
        lambda _db: notifier,
    )
    invoice = SimpleNamespace(
        id=8,
        source_type=source_type,
        source_id=12,
        payer_user_id=20,
        provider_user_id=30,
        status="paid",
        currency="TOMAN",
    )

    BillingInvoicePaymentService(MagicMock())._notify_paid(
        invoice=invoice,
        actor_user_id=20,
    )

    calls = notifier.create_event_and_notify_user.call_args_list
    assert len(calls) == 2
    assert calls[0].kwargs["recipient_user_id"] == 20
    assert calls[0].kwargs["action_url"] == requester_url
    assert calls[0].kwargs["allow_self_notification"] is True
    assert calls[1].kwargs["recipient_user_id"] == 30
    assert calls[1].kwargs["action_url"] == provider_url
    assert calls[0].kwargs["event_key"] == calls[1].kwargs["event_key"]


def test_billable_payment_ledger_is_exact_once_and_balanced() -> None:
    invoice = SimpleNamespace(
        id=6,
        source_type="service_request",
        source_id=14,
        status="paid",
        provider_user_id=30,
        total_amount=Decimal("1000"),
        provider_amount=Decimal("900"),
        platform_amount=Decimal("100"),
    )
    service = LedgerMovementService(MagicMock())
    service._post = MagicMock(return_value="journal")

    assert (
        service.post_billable_invoice_payment(
            invoice=invoice,
            actor_user_id=20,
            trace_id="payment-test",
        )
        == "journal"
    )
    call = service._post.call_args.kwargs
    assert call["idempotency_key"] == "payment:billing_invoice:6"
    assert call["source_type"] == "service_request"
    assert sum(line[-1] for line in call["lines"][:1]) == Decimal("1000")
    assert sum(line[-1] for line in call["lines"][1:]) == Decimal("1000")

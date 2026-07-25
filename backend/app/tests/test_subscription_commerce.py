from datetime import datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest
from sqlalchemy import CheckConstraint, UniqueConstraint

from app.core.exceptions import AppException
from app.modules.finance.models import BillingInvoice
from app.modules.subscriptions.commerce_service import SubscriptionCommerceService
from app.modules.subscriptions.models import BillingSubscriptionPaymentAttempt


def test_platform_invoice_extension_is_explicit_and_provider_optional() -> None:
    checks = {
        constraint.name
        for constraint in BillingInvoice.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }

    assert BillingInvoice.__table__.c.provider_user_id.nullable is True
    assert "ck_billing_invoice_platform_owner" in checks


def test_subscription_payment_has_exact_once_and_toman_contracts() -> None:
    uniques = {
        tuple(column.name for column in constraint.columns)
        for constraint in BillingSubscriptionPaymentAttempt.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    checks = {
        constraint.name
        for constraint in BillingSubscriptionPaymentAttempt.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }

    assert ("idempotency_key",) in uniques
    assert ("provider_authority",) in uniques
    assert ("provider_reference",) in uniques
    assert {
        "ck_subscription_payment_provider",
        "ck_subscription_payment_status",
        "ck_subscription_payment_amount",
        "ck_subscription_payment_currency",
    }.issubset(checks)


def test_checkout_output_does_not_expose_gateway_or_idempotency_secrets() -> None:
    now = datetime.now()
    output = SubscriptionCommerceService._output(
        SimpleNamespace(
            id=11,
            subscription_id=12,
            invoice_id=13,
            provider="zarinpal",
            status="redirected",
            amount_toman=Decimal("250000"),
            currency="TOMAN",
            redirect_url="https://gateway.example/start",
            expires_at=now + timedelta(minutes=30),
            verified_at=None,
            provider_authority="private-authority",
            provider_reference=None,
            idempotency_key="private-key",
        )
    )

    data = output.model_dump()
    assert data["amount_toman"] == Decimal("250000")
    assert data["currency"] == "TOMAN"
    assert "provider_authority" not in data
    assert "provider_reference" not in data
    assert "idempotency_key" not in data


@pytest.mark.parametrize(
    ("period", "duration", "expected"),
    [("monthly", None, 30), ("yearly", None, 365), ("custom", 45, 45)],
)
def test_paid_plan_duration_contract(period: str, duration: int | None, expected: int) -> None:
    plan = SimpleNamespace(billing_period=period, duration_days=duration)
    assert SubscriptionCommerceService._duration_days(plan) == expected


def test_free_plan_cannot_enter_paid_checkout_duration() -> None:
    with pytest.raises(AppException) as caught:
        SubscriptionCommerceService._duration_days(
            SimpleNamespace(billing_period="free", duration_days=None)
        )
    assert caught.value.code == "BILLING_PLAN_PERIOD_INVALID"


def test_mock_checkout_is_blocked_in_production(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.modules.subscriptions.commerce_service.get_settings",
        lambda: SimpleNamespace(app_env="production"),
    )
    service = SubscriptionCommerceService(SimpleNamespace())  # type: ignore[arg-type]

    with pytest.raises(AppException) as caught:
        service.checkout(
            user_id=1,
            plan_code="farmer_plus",
            provider="mock",
            idempotency_key="checkout-production-1",
        )

    assert caught.value.code == "BILLING_PAYMENT_PROVIDER_UNAVAILABLE"
    assert caught.value.status_code == 403

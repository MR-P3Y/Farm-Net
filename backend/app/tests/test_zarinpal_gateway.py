from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.main import app
from app.modules.orders.payment_gateway import PaymentGatewayError, ZarinpalGateway
from app.modules.orders.schemas import PaymentCheckoutIn
from app.modules.orders.service import PaymentService


def _settings(**overrides):
    values = {
        "payment_gateway_enabled": True,
        "payment_gateway": "zarinpal",
        "payment_merchant_id": "00000000-0000-0000-0000-000000000000",
        "payment_callback_base_url": "https://farmnet.example/api/v1/payments/callback/zarinpal",
        "payment_zarinpal_sandbox": True,
        "payment_gateway_timeout_seconds": 15,
        "app_env": "test",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_gateway_is_disabled_by_default_contract() -> None:
    gateway = ZarinpalGateway(_settings(payment_gateway_enabled=False))
    with pytest.raises(PaymentGatewayError, match="disabled"):
        gateway.ensure_configured()


def test_gateway_request_uses_irt_and_fixed_sandbox_host() -> None:
    gateway = ZarinpalGateway(_settings())
    gateway._post = MagicMock(return_value={
        "data": {"code": 100, "authority": "S000000000000000000000000000000000001"},
        "errors": [],
    })
    result = gateway.request_payment(
        amount=Decimal("10000"), invoice_id=12, description="Invoice 12"
    )
    payload = gateway._post.call_args.args[1]
    assert payload["currency"] == "IRT"
    assert payload["amount"] == 10000
    assert payload["metadata"]["auto_verify"] is False
    assert result.redirect_url.startswith("https://sandbox.zarinpal.com/pg/StartPay/")


def test_gateway_verify_accepts_provider_exact_once_code_101() -> None:
    gateway = ZarinpalGateway(_settings())
    gateway._post = MagicMock(return_value={
        "data": {"code": 101, "ref_id": 987654}, "errors": [],
    })
    result = gateway.verify_payment(
        amount=Decimal("10000"), authority="S-authority"
    )
    assert result.code == 101
    assert result.reference_id == "987654"


def test_zarinpal_initiate_stores_authority_not_merchant(monkeypatch) -> None:
    invoice = SimpleNamespace(
        id=12, order_id=9, buyer_user_id=7, status="payment_pending",
        total_amount=Decimal("10000"), currency="TOMAN",
    )
    payment = SimpleNamespace(id=4)
    attempt = SimpleNamespace(
        id=15, amount=Decimal("10000"), provider="mock", status="created",
        provider_reference=None, redirect_url=None, callback_payload=None,
    )
    service = PaymentService(MagicMock())
    service.repo = MagicMock()
    service.repo.get_payment_attempt_by_key.return_value = None
    service.repo.get_invoice_for_buyer.return_value = invoice
    service.repo.get_payment_by_order.return_value = payment
    service.repo.create_payment_attempt.return_value = attempt
    service._attempt_out = lambda value: value
    gateway = MagicMock()
    gateway.request_payment.return_value = SimpleNamespace(
        authority="S-authority", redirect_url="https://sandbox.zarinpal.com/pg/StartPay/S-authority",
        raw_response={"data": {"code": 100}},
    )
    monkeypatch.setattr("app.modules.orders.service.ZarinpalGateway", lambda: gateway)

    result = service.initiate(
        user=SimpleNamespace(id=7),
        payload=PaymentCheckoutIn(
            invoice_id=12, provider="zarinpal", idempotency_key="zarinpal-invoice-12"
        ),
    )
    assert result.provider_reference == "S-authority"
    assert "00000000" not in result.callback_payload
    service.repo.commit.assert_called_once_with()


def test_callback_nok_cancels_without_verify() -> None:
    attempt = SimpleNamespace(
        id=15, user_id=7, status="redirected", callback_payload=None,
        failure_code=None, failure_message=None,
    )
    service = PaymentService(MagicMock())
    service.repo = MagicMock()
    service.repo.get_payment_attempt_by_provider_reference_for_update.return_value = attempt
    service._attempt_out = lambda value: value
    service.verify = MagicMock()
    result = service.handle_zarinpal_callback(authority="S-authority", status="NOK")
    assert result.status == "cancelled"
    service.verify.assert_not_called()
    service.repo.commit.assert_called_once_with()


def test_callback_route_is_public_and_registered() -> None:
    operation = app.openapi()["paths"]["/api/v1/payments/callback/zarinpal"]["get"]
    assert operation.get("security") in (None, [])

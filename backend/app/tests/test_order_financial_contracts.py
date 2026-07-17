from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from sqlalchemy import UniqueConstraint

from app.modules.auth.exceptions import ValidationAuthError

from app.modules.orders.enums import (
    FinancialTransactionStatus,
    FinancialTransactionType,
    InventoryReservationStatus,
    InvoiceStatus,
    PaymentAttemptStatus,
    RefundStatus,
)
from app.modules.orders.models import (
    CommissionSnapshot,
    FinancialInvoice,
    FinancialInvoiceItem,
    FinancialRefund,
    FinancialTransaction,
    InventoryReservation,
    PaymentAttempt,
)
from app.modules.orders.schemas import (
    AdminOrderStatusUpdateIn,
    CheckoutIn,
    OrderOut,
    PaymentCheckoutIn,
    PaymentVerifyIn,
    RefundCreateIn,
)
from app.modules.orders.service import AdminOrderService, CheckoutService, PaymentService


def test_financial_contract_tables_are_registered() -> None:
    assert FinancialInvoice.__tablename__ == "finance_invoices"
    assert FinancialInvoiceItem.__tablename__ == "finance_invoice_items"
    assert CommissionSnapshot.__tablename__ == "commission_snapshots"
    assert PaymentAttempt.__tablename__ == "payment_attempts"
    assert FinancialTransaction.__tablename__ == "finance_transactions"
    assert FinancialRefund.__tablename__ == "finance_refunds"
    assert InventoryReservation.__tablename__ == "inventory_reservations"


def test_idempotency_and_single_snapshot_constraints_exist() -> None:
    payment_unique = {
        tuple(constraint.columns.keys())
        for constraint in PaymentAttempt.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    refund_unique = {
        tuple(constraint.columns.keys())
        for constraint in FinancialRefund.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    snapshot_unique = {
        tuple(constraint.columns.keys())
        for constraint in CommissionSnapshot.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }

    assert ("idempotency_key",) in payment_unique
    assert ("provider_reference",) in payment_unique
    assert ("idempotency_key",) in refund_unique
    assert ("order_id",) in snapshot_unique
    assert ("invoice_id",) in snapshot_unique


def test_financial_enums_are_explicit() -> None:
    assert InvoiceStatus.PAYMENT_PENDING.value == "payment_pending"
    assert PaymentAttemptStatus.VERIFYING.value == "verifying"
    assert FinancialTransactionType.REFUND.value == "refund"
    assert FinancialTransactionStatus.REVERSED.value == "reversed"
    assert RefundStatus.PROCESSING.value == "processing"
    assert InventoryReservationStatus.RELEASED.value == "released"


def test_checkout_and_refund_inputs_require_idempotency() -> None:
    checkout = PaymentCheckoutIn(
        invoice_id=10,
        provider="mock",
        idempotency_key="checkout-order-10",
    )
    refund = RefundCreateIn(
        invoice_id=10,
        amount="1000",
        reason="Customer cancellation",
        idempotency_key="refund-order-10",
    )

    assert checkout.idempotency_key == "checkout-order-10"
    assert refund.amount > 0


def test_checkout_rolls_back_when_atomic_validation_fails() -> None:
    service = CheckoutService(MagicMock())
    service.repo = MagicMock()
    service.repo.release_expired_reservations.return_value = 0
    service.repo.get_active_cart_for_checkout.return_value = None

    with pytest.raises(ValidationAuthError):
        service.checkout(
            user=SimpleNamespace(id=7), payload=CheckoutIn(idempotency_key="checkout-test-7")
        )

    service.repo.rollback.assert_called_once_with()


def test_checkout_locks_stock_and_builds_financial_contracts(monkeypatch) -> None:
    now = datetime.utcnow()
    cart = SimpleNamespace(
        id=1,
        user_id=7,
        status="active",
        currency="TOMAN",
        checked_out_at=None,
    )
    item = SimpleNamespace(
        id=2,
        product_id=3,
        store_id=4,
        quantity=2,
        unit_price=100,
        line_total=200,
        product_name_snapshot="old",
        product_slug_snapshot="old",
        product_sku_snapshot=None,
        unit_snapshot="piece",
    )
    product = SimpleNamespace(
        id=3,
        store_id=4,
        price=150,
        stock_quantity=5,
        min_order_quantity=1,
        max_order_quantity=10,
        name="Product",
        slug="product",
        sku="SKU",
        unit="piece",
    )
    commission = SimpleNamespace(id=5, percent=5)
    order = SimpleNamespace(
        id=6,
        order_number="FN-1",
        buyer_user_id=7,
        store_id=4,
        currency="TOMAN",
        subtotal_amount=300,
        discount_amount=0,
        shipping_amount=0,
        total_amount=300,
        commission_percent=5,
        commission_amount=15,
        seller_amount=285,
    )
    invoice = SimpleNamespace(id=8)
    order_item = SimpleNamespace(id=9, order_id=6, product_id=3, quantity=2)
    payment = SimpleNamespace(id=10)
    service = CheckoutService(MagicMock())
    service.repo = MagicMock()
    service.repo.release_expired_reservations.return_value = 0
    service.repo.get_checkout_request.return_value = None
    service.repo.get_active_cart_for_checkout.return_value = cart
    service.repo.list_cart_items.return_value = [item]
    service.repo.lock_products_for_checkout.return_value = {3: product}
    service.repo.get_active_default_commission.return_value = commission
    service.repo.create_order.return_value = order
    service.repo.create_financial_invoice.return_value = invoice
    service.repo.create_order_item.return_value = order_item
    service.repo.create_payment.return_value = payment
    service._order_out = lambda _: OrderOut(
        id=6,
        order_number="FN-1",
        buyer_user_id=7,
        store_id=4,
        status="pending_payment",
        payment_status="pending",
        currency="TOMAN",
        subtotal_amount=300,
        discount_amount=0,
        shipping_amount=0,
        total_amount=300,
        commission_percent=5,
        commission_amount=15,
        seller_amount=285,
        created_at=now.isoformat(),
        updated_at=now.isoformat(),
    )
    monkeypatch.setattr("app.modules.orders.service._notify_order_created", lambda **_: None)
    monkeypatch.setattr("app.modules.orders.service._notify_payment_created", lambda **_: None)

    result = service.checkout(
        user=SimpleNamespace(id=7), payload=CheckoutIn(idempotency_key="checkout-test-7")
    )

    assert result.orders_count == 1
    assert product.stock_quantity == 3
    assert item.unit_price == 150
    service.repo.create_financial_invoice.assert_called_once()
    service.repo.create_financial_invoice_item.assert_called_once()
    service.repo.create_commission_snapshot.assert_called_once()
    service.repo.create_inventory_reservation.assert_called_once()
    service.repo.create_payment_attempt.assert_called_once()
    service.repo.commit.assert_called_once_with()


def test_mock_payment_consumes_reservation_and_creates_transaction(monkeypatch) -> None:
    now = datetime.utcnow()
    payment = SimpleNamespace(
        id=4,
        order_id=9,
        user_id=2,
        method="mock",
        status="pending",
        amount=1000,
        currency="TOMAN",
        provider="mock",
        provider_payment_id=None,
        provider_reference=None,
        paid_at=None,
        failed_at=None,
        cancelled_at=None,
        created_at=now,
        updated_at=now,
    )
    order = SimpleNamespace(id=9, status="pending_payment", payment_status="pending", paid_at=None)
    attempt = SimpleNamespace(
        id=12,
        status="created",
        expires_at=None,
        provider_reference=None,
        verified_at=None,
    )
    invoice = SimpleNamespace(id=14, status="payment_pending", paid_at=None)
    service = PaymentService(MagicMock())
    service.repo = MagicMock()
    service.repo.get_my_payment_by_id.return_value = payment
    service.repo.get_order_by_id.return_value = order
    service.repo.get_payment_attempt_by_legacy_payment.return_value = attempt
    service.repo.get_invoice_by_order.return_value = invoice
    monkeypatch.setattr(
        "app.modules.orders.service._notify_payment_status_changed", lambda **_: None
    )
    monkeypatch.setattr("app.modules.orders.service._notify_order_status_changed", lambda **_: None)

    service.mock_pay(user=SimpleNamespace(id=2), payment_id=4)

    assert attempt.status == "succeeded"
    assert invoice.status == "paid"
    service.repo.consume_order_reservations.assert_called_once_with(order_id=9, now=payment.paid_at)
    service.repo.create_payment_transaction.assert_called_once()


def test_mock_payment_rejects_expired_inventory_reservation() -> None:
    now = datetime.utcnow()
    payment = SimpleNamespace(id=4, order_id=9, status="pending")
    order = SimpleNamespace(id=9, status="pending_payment", payment_status="pending")
    attempt = SimpleNamespace(id=12, expires_at=now - timedelta(seconds=1))
    service = PaymentService(MagicMock())
    service.repo = MagicMock()
    service.repo.get_my_payment_by_id.return_value = payment
    service.repo.get_order_by_id.return_value = order
    service.repo.get_payment_attempt_by_legacy_payment.return_value = attempt

    with pytest.raises(ValidationAuthError) as error:
        service.mock_pay(user=SimpleNamespace(id=2), payment_id=4)

    assert error.value.details["error_code"] == "PAYMENT_RESERVATION_EXPIRED"
    service.repo.consume_order_reservations.assert_not_called()


def test_payment_initiate_replays_same_idempotency_key() -> None:
    attempt = SimpleNamespace(
        user_id=7, invoice_id=11, provider="mock", idempotency_key="payment-replay-7"
    )
    service = PaymentService(MagicMock())
    service.repo = MagicMock()
    service.repo.get_payment_attempt_by_key.return_value = attempt
    service._attempt_out = lambda value: value

    result = service.initiate(
        user=SimpleNamespace(id=7),
        payload=PaymentCheckoutIn(
            invoice_id=11, provider="mock", idempotency_key="payment-replay-7"
        ),
    )

    assert result is attempt
    service.repo.create_payment_attempt.assert_not_called()


def test_payment_initiate_rejects_idempotency_conflict() -> None:
    attempt = SimpleNamespace(user_id=8, invoice_id=11, provider="mock")
    service = PaymentService(MagicMock())
    service.repo = MagicMock()
    service.repo.get_payment_attempt_by_key.return_value = attempt

    with pytest.raises(ValidationAuthError) as error:
        service.initiate(
            user=SimpleNamespace(id=7),
            payload=PaymentCheckoutIn(
                invoice_id=11, provider="mock", idempotency_key="payment-conflict-7"
            ),
        )

    assert error.value.details["error_code"] == "PAYMENT_IDEMPOTENCY_CONFLICT"


def test_payment_verify_is_exact_once_after_success() -> None:
    attempt = SimpleNamespace(status="succeeded")
    service = PaymentService(MagicMock())
    service.repo = MagicMock()
    service.repo.get_payment_attempt_for_buyer.return_value = attempt
    service._attempt_out = lambda value: value

    result = service.verify(
        user=SimpleNamespace(id=7),
        payload=PaymentVerifyIn(payment_attempt_id=12, provider_payment_id="MOCK-12"),
    )

    assert result is attempt
    service.repo.create_payment_transaction.assert_not_called()
    service.repo.commit.assert_not_called()


def test_admin_cancel_releases_reserved_or_consumed_inventory(monkeypatch) -> None:
    order = SimpleNamespace(
        id=9,
        status="paid",
        payment_status="paid",
        cancelled_at=None,
        admin_note=None,
    )
    invoice = SimpleNamespace(status="paid", cancelled_at=None)
    service = AdminOrderService(MagicMock())
    service.repo = MagicMock()
    service.repo.get_admin_order_by_id.return_value = order
    service.repo.get_invoice_by_order.return_value = invoice
    service._order_out = lambda value: value
    monkeypatch.setattr("app.modules.orders.service._notify_order_status_changed", lambda **_: None)

    service.update_admin_order_status(
        user=SimpleNamespace(id=1),
        order_id=9,
        payload=AdminOrderStatusUpdateIn(status="cancelled", admin_note="cancel"),
    )

    assert invoice.status == "refund_pending"
    service.repo.release_order_inventory.assert_called_once()
    assert service.repo.release_order_inventory.call_args.kwargs["include_consumed"] is True

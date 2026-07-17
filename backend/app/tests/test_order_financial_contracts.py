from sqlalchemy import UniqueConstraint

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
from app.modules.orders.schemas import PaymentCheckoutIn, RefundCreateIn


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

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError
from sqlalchemy import CheckConstraint, Index

from app.main import app
from app.modules.finance.enums import BillingRefundStatus
from app.modules.finance.models import BillingRefund
from app.modules.finance.refund_service import BillingRefundService
from app.modules.finance.schemas import (
    BillingRefundCreateIn,
    CommissionPolicyUpdateIn,
)
from app.modules.finance.seed import seed_finance_policies
from app.modules.finance.settlement_service import LedgerMovementService


def _names(model, kind) -> set[str]:
    return {
        item.name
        for item in (*model.__table__.constraints, *model.__table__.indexes)
        if isinstance(item, kind) and item.name
    }


def test_billing_refund_has_bounded_exact_once_contract() -> None:
    assert BillingRefund.__tablename__ == "finance_billing_refunds"
    assert {
        "ck_billing_refund_source_type",
        "ck_billing_refund_status",
        "ck_billing_refund_amount",
        "ck_billing_refund_currency",
    } <= _names(BillingRefund, CheckConstraint)
    assert {
        "ix_billing_refund_source",
        "ix_billing_refund_status_requested",
    } <= _names(BillingRefund, Index)
    assert BillingRefund.__table__.c.invoice_id.unique is True
    assert BillingRefund.__table__.c.idempotency_key.unique is True


def test_service_refund_release_routes_are_explicit() -> None:
    paths = app.openapi()["paths"]
    assert "post" in paths["/api/v1/services/requests/{request_id}/refund"]
    assert "post" in paths[
        "/api/v1/services/requests/{request_id}/confirm-completion"
    ]
    assert "post" in paths[
        "/api/v1/admin/services/requests/{request_id}/confirm-completion"
    ]
    assert "get" in paths["/api/v1/admin/finance/billing-refunds"]
    assert "patch" in paths[
        "/api/v1/admin/finance/billing-refunds/{refund_id}/decision"
    ]
    assert "post" in paths[
        "/api/v1/admin/finance/billing-refunds/{refund_id}/complete-mock"
    ]


def test_refund_and_commission_inputs_are_bounded() -> None:
    assert BillingRefundCreateIn(
        reason="work cancelled",
        idempotency_key="refund-service-1",
    ).reason == "work cancelled"
    assert CommissionPolicyUpdateIn(percent=Decimal("10")).percent == Decimal("10")
    with pytest.raises(ValidationError):
        BillingRefundCreateIn(reason="x", idempotency_key="short")
    with pytest.raises(ValidationError):
        CommissionPolicyUpdateIn(percent=Decimal("100"))


def test_finance_seed_preserves_admin_managed_service_percent() -> None:
    row = SimpleNamespace(
        id=7,
        code="service-request-default",
        title="Default service request commission",
        source_type="service_request",
        default_scope="service_request",
        percent=Decimal("12.50"),
        status="active",
        is_default=True,
    )
    db = MagicMock()
    db.query.return_value.filter.return_value.one_or_none.return_value = row

    result = seed_finance_policies(db)

    assert row.percent == Decimal("12.50")
    assert result["service_percent"] == "12.50"
    db.commit.assert_called_once()


@pytest.mark.parametrize(
    ("review_required", "expected_status"),
    [(False, BillingRefundStatus.APPROVED.value), (True, BillingRefundStatus.REQUESTED.value)],
)
def test_refund_is_full_and_review_depends_on_work_start(
    review_required: bool,
    expected_status: str,
) -> None:
    invoice = SimpleNamespace(
        id=8,
        source_type="service_request",
        source_id=12,
        payer_user_id=20,
        provider_user_id=30,
        status="paid",
        total_amount=Decimal("1000"),
    )
    attempt = SimpleNamespace(id=4)
    empty_key = MagicMock()
    empty_key.filter.return_value.one_or_none.return_value = None
    empty_invoice = MagicMock()
    empty_invoice.filter.return_value.with_for_update.return_value.one_or_none.return_value = None
    successful_attempt = MagicMock()
    successful_attempt.filter.return_value.order_by.return_value.with_for_update.return_value.first.return_value = attempt
    db = MagicMock()
    db.query.side_effect = [empty_key, empty_invoice, successful_attempt]
    service = BillingRefundService(db)
    service._invoice = MagicMock(return_value=invoice)
    service._notify = MagicMock()

    row = service.create(
        invoice_id=invoice.id,
        requester_user_id=invoice.payer_user_id,
        reason="Full cancellation",
        idempotency_key=f"service-refund-{review_required}",
        review_required=review_required,
    )

    assert row.amount_toman == invoice.total_amount
    assert row.status == expected_status
    assert row.review_required is review_required
    assert invoice.status == "refund_pending"


def test_completion_release_moves_pending_to_available() -> None:
    invoice = SimpleNamespace(
        id=8,
        source_type="service_request",
        source_id=12,
        status="paid",
        provider_user_id=30,
        provider_amount=Decimal("900"),
    )
    service = LedgerMovementService(MagicMock())
    service._post = MagicMock(return_value="journal")

    assert service.release_completed_billable_invoice(
        invoice=invoice,
        actor_user_id=20,
        trace_id="completion-test",
    ) == "journal"
    call = service._post.call_args.kwargs
    assert call["idempotency_key"] == "release:billing_invoice:8"
    assert call["lines"][0][-1] == call["lines"][1][-1] == Decimal("900")


def test_service_refund_reverses_release_and_payment_economics() -> None:
    invoice = SimpleNamespace(
        id=8,
        source_type="service_request",
        source_id=12,
        status="refund_pending",
        provider_user_id=30,
        total_amount=Decimal("1000"),
        provider_amount=Decimal("900"),
        platform_amount=Decimal("100"),
    )
    service = LedgerMovementService(MagicMock())
    service.reverse_billable_release_for_refund = MagicMock()
    service._post = MagicMock(return_value="refund-journal")

    assert service.post_billable_invoice_refund(
        invoice=invoice,
        actor_user_id=1,
        trace_id="refund-test",
    ) == "refund-journal"
    service.reverse_billable_release_for_refund.assert_called_once()
    call = service._post.call_args.kwargs
    assert call["idempotency_key"] == "refund:billing_invoice:8"
    assert sum(line[-1] for line in call["lines"][:2]) == Decimal("1000")
    assert call["lines"][2][-1] == Decimal("1000")

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock

from sqlalchemy import CheckConstraint, event

from app.main import app
from app.modules.auth.seed import BASE_PERMISSIONS
from app.modules.finance.enums import AccountPurpose, EntrySide, SettlementStatus
from app.modules.finance.models import (
    SettlementRequest,
    _protect_settlement_delete,
    _protect_settlement_update,
)
from app.modules.finance.settlement_service import LedgerMovementService


def test_settlement_database_and_permissions_are_explicit() -> None:
    assert SettlementRequest.__tablename__ == "finance_settlement_requests"
    checks = {
        item.name
        for item in SettlementRequest.__table__.constraints
        if isinstance(item, CheckConstraint)
    }
    assert {
        "ck_settlement_amount_positive",
        "ck_settlement_currency_toman",
        "ck_settlement_status",
    } <= checks
    assert event.contains(SettlementRequest, "before_update", _protect_settlement_update)
    assert event.contains(SettlementRequest, "before_delete", _protect_settlement_delete)
    codes = {item.code for item in BASE_PERMISSIONS}
    assert {"settlements.read_own", "settlements.create_own"} <= codes


def test_wallet_and_settlement_routes_are_registered() -> None:
    paths = app.openapi()["paths"]
    assert "get" in paths["/api/v1/finance/wallet/me"]
    assert "get" in paths["/api/v1/finance/settlements/me"]
    assert "post" in paths["/api/v1/finance/settlements"]
    assert "get" in paths["/api/v1/admin/finance/settlements"]
    assert "patch" in paths["/api/v1/admin/finance/settlements/{settlement_id}/decision"]
    assert "post" in paths[
        "/api/v1/admin/finance/settlements/{settlement_id}/simulate-payout"
    ]


def test_release_moves_provider_pending_to_available_without_new_money() -> None:
    db = Mock()
    db.query.return_value.filter.return_value.one_or_none.return_value = SimpleNamespace(
        status="paid", provider_user_id=30, provider_amount=Decimal("950")
    )
    service = LedgerMovementService(db)
    service._post = Mock(return_value=SimpleNamespace(id=8))
    order = SimpleNamespace(id=7, status="delivered", payment_status="paid")

    service.release_delivered_order(order=order, actor_user_id=30, trace_id="trace")

    lines = service._post.call_args.kwargs["lines"]
    assert lines == (
        (AccountPurpose.PROVIDER_PENDING, 30, EntrySide.DEBIT, Decimal("950")),
        (AccountPurpose.PROVIDER_AVAILABLE, 30, EntrySide.CREDIT, Decimal("950")),
    )
    assert service._post.call_args.kwargs["idempotency_key"] == "release:product_order:7"


def test_reserve_reject_and_simulated_payout_journals_have_correct_sides() -> None:
    service = LedgerMovementService.__new__(LedgerMovementService)
    service.db = Mock()
    service._post = Mock(return_value=SimpleNamespace(id=1))
    service.balance = Mock(return_value=SimpleNamespace(available_amount=Decimal("500")))
    row = SimpleNamespace(id=4, requester_user_id=30, amount=Decimal("400"))

    service.post_settlement_reserve(user_id=30, amount=Decimal("400"), key="key", trace_id="t")
    reserve = service._post.call_args.kwargs["lines"]
    assert reserve[0][:3] == (AccountPurpose.PROVIDER_AVAILABLE, 30, EntrySide.DEBIT)
    assert reserve[1][:3] == (AccountPurpose.PROVIDER_RESERVED, 30, EntrySide.CREDIT)

    service.post_settlement_reject(row=row, actor_user_id=9, trace_id="t")
    rejected = service._post.call_args.kwargs["lines"]
    assert rejected[0][:3] == (AccountPurpose.PROVIDER_RESERVED, 30, EntrySide.DEBIT)
    assert rejected[1][:3] == (AccountPurpose.PROVIDER_AVAILABLE, 30, EntrySide.CREDIT)

    service.post_simulated_payout(row=row, actor_user_id=9, trace_id="t")
    payout = service._post.call_args.kwargs["lines"]
    assert payout[0][:3] == (AccountPurpose.PROVIDER_RESERVED, 30, EntrySide.DEBIT)
    assert payout[1][:3] == (AccountPurpose.PAYOUT_CLEARING, None, EntrySide.CREDIT)


def test_status_vocabulary_does_not_claim_real_bank_payout() -> None:
    assert {item.value for item in SettlementStatus} == {
        "requested",
        "approved",
        "rejected",
        "simulated_completed",
    }
    assert not hasattr(SettlementStatus, "PAID")

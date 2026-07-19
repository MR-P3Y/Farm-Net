from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.modules.finance.enums import AccountPurpose, EntrySide
from app.modules.finance.service import OrderLedgerBridge


def _invoice(*, platform: str = "100", provider: str = "900"):
    return SimpleNamespace(
        id=1,
        order_id=2,
        store_id=3,
        currency="TOMAN",
        total_amount=Decimal("1000"),
        platform_amount=Decimal(platform),
        provider_amount=Decimal(provider),
    )


def test_payment_bridge_builds_balanced_cash_revenue_and_pending_lines() -> None:
    bridge = OrderLedgerBridge(MagicMock())
    bridge._provider_id = MagicMock(return_value=44)
    bridge._post = MagicMock(return_value="journal")

    result = bridge.post_payment(
        invoice=_invoice(),
        transaction=SimpleNamespace(id=9),
        actor_user_id=7,
        trace_id="trace-payment",
    )

    assert result == "journal"
    lines = bridge._post.call_args.kwargs["lines"]
    assert lines[0][0] == AccountPurpose.PLATFORM_CASH
    assert lines[0][3] == EntrySide.DEBIT
    assert sum(x[4] for x in lines if x[3] == EntrySide.DEBIT) == Decimal("1000")
    assert sum(x[4] for x in lines if x[3] == EntrySide.CREDIT) == Decimal("1000")


def test_refund_bridge_exactly_reverses_payment_economics() -> None:
    bridge = OrderLedgerBridge(MagicMock())
    bridge._provider_id = MagicMock(return_value=44)
    bridge._post = MagicMock(return_value="refund-journal")

    result = bridge.post_refund(
        invoice=_invoice(),
        transaction=SimpleNamespace(id=10),
        actor_user_id=8,
        trace_id="trace-refund",
    )

    assert result == "refund-journal"
    lines = bridge._post.call_args.kwargs["lines"]
    assert lines[-1][0] == AccountPurpose.PLATFORM_CASH
    assert lines[-1][3] == EntrySide.CREDIT
    assert sum(x[4] for x in lines if x[3] == EntrySide.DEBIT) == Decimal("1000")
    assert sum(x[4] for x in lines if x[3] == EntrySide.CREDIT) == Decimal("1000")

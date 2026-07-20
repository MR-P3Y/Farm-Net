from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

import pytest
from sqlalchemy import CheckConstraint, event

from app.modules.finance.enums import RentalFinancialTermsStatus
from app.modules.finance.models import (
    RentalFinancialTerms,
    _protect_rental_terms_delete,
    _protect_rental_terms_update,
)
from app.modules.finance.rental_service import (
    RentalFinancialContractError,
    RentalFinancialService,
)


def _check_names():
    return {
        item.name
        for item in RentalFinancialTerms.__table__.constraints
        if isinstance(item, CheckConstraint)
    }


def test_rental_financial_terms_enforce_revenue_deposit_boundary() -> None:
    assert RentalFinancialTerms.__tablename__ == "finance_rental_terms"
    assert {
        "ck_rental_terms_revenue_positive",
        "ck_rental_terms_deposit_nonnegative",
        "ck_rental_terms_total_components",
        "ck_rental_terms_currency_toman",
        "ck_rental_terms_status",
    } <= _check_names()
    assert event.contains(
        RentalFinancialTerms, "before_update", _protect_rental_terms_update
    )
    assert event.contains(
        RentalFinancialTerms, "before_delete", _protect_rental_terms_delete
    )


class _Query:
    def filter(self, *_args):
        return self

    def with_for_update(self):
        return self

    def one_or_none(self):
        return None


class _Db:
    def __init__(self):
        self.added = []

    def query(self, *_args):
        return _Query()

    def add(self, row):
        self.added.append(row)

    def flush(self):
        return None


def _request(**overrides):
    values = {
        "id": 17,
        "requester_user_id": 10,
        "pricing_rule_id": 8,
        "requested_units": Decimal("2"),
        "price_per_unit_snapshot": Decimal("2000000"),
        "rental_amount_snapshot": Decimal("4000000"),
        "deposit_amount_snapshot": Decimal("500000"),
        "total_amount_snapshot": Decimal("4500000"),
        "currency": "TOMAN",
        "accepted_at": datetime(2026, 7, 20),
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_accepted_rental_snapshots_exact_terms_without_posting_money() -> None:
    db = _Db()
    row = RentalFinancialService(db).snapshot(request=_request(), provider_user_id=30)

    assert row.status == RentalFinancialTermsStatus.UNFUNDED.value
    assert row.rental_revenue_amount == Decimal("4000000")
    assert row.deposit_principal_amount == Decimal("500000")
    assert row.funding_total_amount == Decimal("4500000")
    assert row.rental_revenue_amount + row.deposit_principal_amount == row.funding_total_amount
    assert row.payer_user_id == 10
    assert row.provider_user_id == 30


@pytest.mark.parametrize(
    "case",
    [
        _request(currency="IRR"),
        _request(total_amount_snapshot=Decimal("4000000")),
        _request(rental_amount_snapshot=None),
        _request(deposit_amount_snapshot=Decimal("-1")),
    ],
)
def test_invalid_or_ambiguous_rental_terms_fail_closed(case) -> None:
    with pytest.raises(RentalFinancialContractError):
        RentalFinancialService(_Db()).snapshot(request=case, provider_user_id=30)


def test_terms_status_names_do_not_claim_capture_or_deposit_release() -> None:
    assert {item.value for item in RentalFinancialTermsStatus} == {
        "unfunded",
        "cancelled_unfunded",
        "operationally_completed_unfunded",
    }

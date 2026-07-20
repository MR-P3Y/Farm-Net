from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

import pytest
from pydantic import ValidationError
from sqlalchemy import CheckConstraint, UniqueConstraint, event

from app.main import app
from app.modules.finance.enums import FinalPriceProposalStatus
from app.modules.finance.final_price_service import FinalPriceContractError, FinalPriceService
from app.modules.finance.models import (
    BillingCommissionSnapshot,
    BillingInvoice,
    BillingInvoiceItem,
    FinalPriceProposal,
    _protect_final_price_delete,
    _protect_final_price_update,
)
from app.modules.finance.schemas import FinalPriceDecisionIn, FinalPriceProposalIn


def _names(model, kind):
    return {
        constraint.name
        for constraint in model.__table__.constraints
        if isinstance(constraint, kind)
    }


def test_final_price_table_enforces_version_active_and_accepted_exact_once() -> None:
    assert FinalPriceProposal.__tablename__ == "finance_final_price_proposals"
    assert "uq_final_price_source_version" in _names(FinalPriceProposal, UniqueConstraint)
    checks = _names(FinalPriceProposal, CheckConstraint)
    assert "ck_final_price_amount_positive" in checks
    assert "ck_final_price_currency_toman" in checks
    assert "ck_final_price_source_type" in checks
    assert "ck_final_price_status" in checks
    assert "ck_final_price_active_scope" in checks
    assert "ck_final_price_accepted_scope" in checks
    assert event.contains(FinalPriceProposal, "before_update", _protect_final_price_update)
    assert event.contains(FinalPriceProposal, "before_delete", _protect_final_price_delete)


def test_final_price_input_is_positive_toman_and_decision_is_explicit() -> None:
    payload = FinalPriceProposalIn(amount="150000", description="Final agreed scope")
    assert payload.currency == "TOMAN"
    with pytest.raises(ValidationError):
        FinalPriceProposalIn(amount="150000", currency="IRR", description="Final scope")
    with pytest.raises(ValidationError):
        FinalPriceProposalIn(amount="0", description="Final scope")
    assert FinalPriceDecisionIn(decision="accept").decision == "accept"
    with pytest.raises(ValidationError):
        FinalPriceDecisionIn(decision="approve")


def test_only_service_and_consultation_sources_are_eligible() -> None:
    service = FinalPriceService.__new__(FinalPriceService)
    service._validate_source("service_request")
    service._validate_source("consultation_request")
    with pytest.raises(FinalPriceContractError):
        service._validate_source("rental_request")


def test_final_price_routes_preserve_requester_provider_ownership_permissions() -> None:
    routes = {
        (method.upper(), path)
        for path, operations in app.openapi()["paths"].items()
        for method in operations
        if "final-price" in path
    }
    expected = {
        ("POST", "/api/v1/services/requests/assigned/{request_id}/final-price"),
        ("GET", "/api/v1/services/requests/assigned/{request_id}/final-price"),
        ("GET", "/api/v1/services/requests/{request_id}/final-price"),
        ("PATCH", "/api/v1/services/requests/{request_id}/final-price"),
        ("POST", "/api/v1/consultants/requests/assigned/{request_id}/final-price"),
        ("GET", "/api/v1/consultants/requests/assigned/{request_id}/final-price"),
        ("GET", "/api/v1/consultants/requests/{request_id}/final-price"),
        ("PATCH", "/api/v1/consultants/requests/{request_id}/final-price"),
    }
    assert expected <= set(routes)


class _Query:
    def filter(self, *_args):
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
        if isinstance(row, BillingInvoice):
            row.id = 501

    def flush(self):
        return None


def test_accepted_price_creates_invoice_item_and_immutable_commission_snapshot() -> None:
    db = _Db()
    service = FinalPriceService(db)
    proposal = SimpleNamespace(
        id=77,
        source_type="service_request",
        source_id=12,
        payer_user_id=10,
        provider_user_id=20,
        amount=Decimal("100001.00"),
        description_snapshot="Complete the agreed work",
        decided_at=datetime(2026, 7, 20),
    )
    policy = SimpleNamespace(id=9, percent=Decimal("12.50"))

    invoice = service._create_invoice(row=proposal, policy=policy, title="Service: harvest")

    assert invoice.total_amount == Decimal("100001.00")
    assert invoice.platform_amount == Decimal("12500.13")
    assert invoice.provider_amount == Decimal("87500.87")
    item = next(row for row in db.added if isinstance(row, BillingInvoiceItem))
    snapshot = next(row for row in db.added if isinstance(row, BillingCommissionSnapshot))
    assert item.source_item_id == proposal.id
    assert item.line_total == proposal.amount
    assert snapshot.base_amount == proposal.amount
    assert snapshot.platform_amount + snapshot.provider_amount == proposal.amount
    assert invoice.status == "payment_pending"


def test_status_values_distinguish_rejection_from_supersession() -> None:
    assert FinalPriceProposalStatus.PROPOSED.value == "proposed"
    assert FinalPriceProposalStatus.ACCEPTED.value == "accepted"
    assert FinalPriceProposalStatus.REJECTED.value == "rejected"
    assert FinalPriceProposalStatus.SUPERSEDED.value == "superseded"

from sqlalchemy import CheckConstraint, UniqueConstraint, event

from app.modules.finance.models import (
    BillingCommissionSnapshot,
    BillingInvoice,
    BillingInvoiceItem,
    CommissionPolicy,
    _reject_posted_ledger_mutation,
)


def _names(model, kind):
    return {
        constraint.name
        for constraint in model.__table__.constraints
        if isinstance(constraint, kind)
    }


def test_universal_billing_tables_are_registered() -> None:
    assert CommissionPolicy.__tablename__ == "finance_commission_policies"
    assert BillingInvoice.__tablename__ == "finance_billing_invoices"
    assert BillingInvoiceItem.__tablename__ == "finance_billing_invoice_items"
    assert BillingCommissionSnapshot.__tablename__ == "finance_billing_commission_snapshots"


def test_invoice_and_commission_constraints_preserve_snapshots() -> None:
    assert "ck_commission_policy_default_scope" in _names(CommissionPolicy, CheckConstraint)
    checks = _names(BillingInvoice, CheckConstraint)
    assert "ck_billing_invoice_currency_toman" in checks
    assert "ck_billing_invoice_split_total" in checks
    assert "uq_billing_invoice_source" in _names(BillingInvoice, UniqueConstraint)
    assert "uq_billing_invoice_item_sequence" in _names(BillingInvoiceItem, UniqueConstraint)
    assert "ck_billing_commission_percent" in _names(
        BillingCommissionSnapshot, CheckConstraint
    )
    for model in (BillingInvoiceItem, BillingCommissionSnapshot):
        assert event.contains(model, "before_update", _reject_posted_ledger_mutation)
        assert event.contains(model, "before_delete", _reject_posted_ledger_mutation)

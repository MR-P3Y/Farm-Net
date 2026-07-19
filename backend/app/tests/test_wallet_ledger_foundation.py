from sqlalchemy import CheckConstraint, UniqueConstraint, event

from app.modules.auth.seed import BASE_PERMISSIONS
from app.modules.finance.models import (
    LedgerEntry,
    LedgerTransaction,
    WalletAccount,
    _reject_posted_ledger_mutation,
)


def _constraint_names(model, constraint_type) -> set[str | None]:
    return {
        constraint.name
        for constraint in model.__table__.constraints
        if isinstance(constraint, constraint_type)
    }


def test_wallet_and_ledger_tables_are_registered() -> None:
    assert WalletAccount.__tablename__ == "finance_wallet_accounts"
    assert LedgerTransaction.__tablename__ == "finance_ledger_transactions"
    assert LedgerEntry.__tablename__ == "finance_ledger_entries"


def test_ledger_database_contracts_enforce_core_invariants() -> None:
    transaction_checks = _constraint_names(LedgerTransaction, CheckConstraint)
    transaction_uniques = _constraint_names(LedgerTransaction, UniqueConstraint)
    entry_checks = _constraint_names(LedgerEntry, CheckConstraint)

    assert "ck_ledger_transactions_balanced_totals" in transaction_checks
    assert "ck_ledger_transactions_currency_toman" in transaction_checks
    assert "ck_ledger_transactions_debit_positive" in transaction_checks
    assert "ck_ledger_transactions_credit_positive" in transaction_checks
    assert {"journal_number", "idempotency_key", "reversal_of_id"} <= {
        column.name
        for constraint in LedgerTransaction.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
        for column in constraint.columns
    }
    assert transaction_uniques
    assert "ck_ledger_entries_amount_positive" in entry_checks
    assert "ck_ledger_entries_currency_toman" in entry_checks
    assert "ck_ledger_entries_side" in entry_checks
    assert "uq_ledger_entry_sequence" in _constraint_names(LedgerEntry, UniqueConstraint)


def test_posted_ledger_models_have_orm_immutability_guards() -> None:
    for model in (LedgerTransaction, LedgerEntry):
        assert event.contains(model, "before_update", _reject_posted_ledger_mutation)
        assert event.contains(model, "before_delete", _reject_posted_ledger_mutation)


def test_wallet_ledger_permissions_are_seeded() -> None:
    codes = {permission.code for permission in BASE_PERMISSIONS}
    assert {
        "wallet.read_own",
        "finance.wallets.read",
        "finance.ledger.read",
        "finance.ledger.post_internal",
        "finance.ledger.reconcile",
    } <= codes

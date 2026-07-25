from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    event,
)
from sqlalchemy import inspect
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.money import CurrencyCode
from app.db.base import Base
from app.modules.finance.enums import AccountStatus, LedgerStatus
from app.modules.finance.enums import (
    BillingInvoiceStatus,
    CommissionPolicyStatus,
    FinalPriceProposalStatus,
    RentalFinancialTermsStatus,
    SettlementStatus,
)


class SettlementRequest(Base):
    __tablename__ = "finance_settlement_requests"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    requester_user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    idempotency_key: Mapped[str] = mapped_column(String(180), nullable=False, unique=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), default=SettlementStatus.REQUESTED.value, nullable=False, index=True
    )
    reserve_journal_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("finance_ledger_transactions.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
    )
    decision_journal_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("finance_ledger_transactions.id", ondelete="RESTRICT"),
        unique=True,
    )
    note: Mapped[str | None] = mapped_column(String(500))
    admin_note: Mapped[str | None] = mapped_column(String(1000))
    decided_by_user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="SET NULL"), index=True
    )
    requested_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime)
    simulated_completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_settlement_amount_positive"),
        CheckConstraint("currency = 'TOMAN'", name="ck_settlement_currency_toman"),
        CheckConstraint(
            "status IN ('requested', 'approved', 'rejected', 'simulated_completed')",
            name="ck_settlement_status",
        ),
        Index("ix_settlement_requester_status", "requester_user_id", "status"),
        Index("ix_settlement_status_requested", "status", "requested_at"),
    )


class RentalFinancialTerms(Base):
    __tablename__ = "finance_rental_terms"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    rental_request_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("rental_requests.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
        index=True,
    )
    payer_user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    provider_user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    pricing_rule_id_snapshot: Mapped[int] = mapped_column(BigInteger, nullable=False)
    requested_units_snapshot: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    unit_price_snapshot: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    rental_revenue_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    deposit_principal_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    funding_total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), default=RentalFinancialTermsStatus.UNFUNDED.value, nullable=False, index=True
    )
    accepted_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime)
    operationally_completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        CheckConstraint("requested_units_snapshot > 0", name="ck_rental_terms_units_positive"),
        CheckConstraint("unit_price_snapshot > 0", name="ck_rental_terms_unit_price_positive"),
        CheckConstraint("rental_revenue_amount > 0", name="ck_rental_terms_revenue_positive"),
        CheckConstraint(
            "deposit_principal_amount >= 0", name="ck_rental_terms_deposit_nonnegative"
        ),
        CheckConstraint(
            "funding_total_amount = rental_revenue_amount + deposit_principal_amount",
            name="ck_rental_terms_total_components",
        ),
        CheckConstraint("currency = 'TOMAN'", name="ck_rental_terms_currency_toman"),
        CheckConstraint(
            "status IN ('unfunded', 'cancelled_unfunded', 'operationally_completed_unfunded')",
            name="ck_rental_terms_status",
        ),
        Index("ix_rental_terms_payer_status", "payer_user_id", "status"),
        Index("ix_rental_terms_provider_status", "provider_user_id", "status"),
    )


class FinalPriceProposal(Base):
    __tablename__ = "finance_final_price_proposals"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    payer_user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    provider_user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    proposed_by_user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    description_snapshot: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=FinalPriceProposalStatus.PROPOSED.value, nullable=False, index=True
    )
    active_scope: Mapped[str | None] = mapped_column(String(120), unique=True)
    accepted_scope: Mapped[str | None] = mapped_column(String(120), unique=True)
    decided_by_user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="SET NULL"), index=True
    )
    proposed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "source_type", "source_id", "version", name="uq_final_price_source_version"
        ),
        CheckConstraint("amount > 0", name="ck_final_price_amount_positive"),
        CheckConstraint("currency = 'TOMAN'", name="ck_final_price_currency_toman"),
        CheckConstraint(
            "source_type IN ('service_request', 'consultation_request')",
            name="ck_final_price_source_type",
        ),
        CheckConstraint(
            "status IN ('proposed', 'accepted', 'rejected', 'superseded')",
            name="ck_final_price_status",
        ),
        CheckConstraint(
            "(status = 'proposed' AND active_scope IS NOT NULL) OR "
            "(status <> 'proposed' AND active_scope IS NULL)",
            name="ck_final_price_active_scope",
        ),
        CheckConstraint(
            "(status = 'accepted' AND accepted_scope IS NOT NULL) OR "
            "(status <> 'accepted' AND accepted_scope IS NULL)",
            name="ck_final_price_accepted_scope",
        ),
        Index("ix_final_price_source", "source_type", "source_id", "version"),
        Index("ix_final_price_payer_status", "payer_user_id", "status"),
        Index("ix_final_price_provider_status", "provider_user_id", "status"),
    )


class CommissionPolicy(Base):
    __tablename__ = "finance_commission_policies"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    default_scope: Mapped[str | None] = mapped_column(String(50))
    percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=CommissionPolicyStatus.ACTIVE.value, nullable=False, index=True
    )
    is_default: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        UniqueConstraint("default_scope", name="uq_commission_policy_default_scope"),
        CheckConstraint("percent >= 0 AND percent <= 100", name="ck_commission_policy_percent"),
        CheckConstraint(
            "(is_default = 0 AND default_scope IS NULL) OR "
            "(is_default = 1 AND default_scope = source_type)",
            name="ck_commission_policy_default_scope",
        ),
        Index("ix_commission_policy_source_default", "source_type", "status", "is_default"),
    )


class BillingInvoice(Base):
    __tablename__ = "finance_billing_invoices"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    invoice_number: Mapped[str] = mapped_column(String(70), unique=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    legacy_invoice_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("finance_invoices.id", ondelete="RESTRICT"), unique=True, index=True
    )
    payer_user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    provider_user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(
        String(30), default=BillingInvoiceStatus.PAYMENT_PENDING.value, nullable=False, index=True
    )
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    subtotal_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    surcharge_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    platform_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    provider_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime)
    refunded_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    items: Mapped[list["BillingInvoiceItem"]] = relationship(
        back_populates="invoice", cascade="all, delete-orphan"
    )
    commission_snapshot: Mapped["BillingCommissionSnapshot | None"] = relationship(
        back_populates="invoice", uselist=False, cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("source_type", "source_id", name="uq_billing_invoice_source"),
        CheckConstraint("currency = 'TOMAN'", name="ck_billing_invoice_currency_toman"),
        CheckConstraint("subtotal_amount >= 0", name="ck_billing_invoice_subtotal"),
        CheckConstraint("discount_amount >= 0", name="ck_billing_invoice_discount"),
        CheckConstraint("surcharge_amount >= 0", name="ck_billing_invoice_surcharge"),
        CheckConstraint("total_amount > 0", name="ck_billing_invoice_total"),
        CheckConstraint("platform_amount >= 0", name="ck_billing_invoice_platform"),
        CheckConstraint("provider_amount >= 0", name="ck_billing_invoice_provider"),
        CheckConstraint(
            "platform_amount + provider_amount = total_amount",
            name="ck_billing_invoice_split_total",
        ),
        CheckConstraint(
            "(source_type = 'platform_subscription' AND provider_user_id IS NULL "
            "AND provider_amount = 0 AND platform_amount = total_amount) OR "
            "(source_type <> 'platform_subscription' AND provider_user_id IS NOT NULL)",
            name="ck_billing_invoice_platform_owner",
        ),
        Index("ix_billing_invoice_payer_status", "payer_user_id", "status"),
        Index("ix_billing_invoice_provider_status", "provider_user_id", "status"),
    )


class BillingInvoiceItem(Base):
    __tablename__ = "finance_billing_invoice_items"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    invoice_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("finance_billing_invoices.id", ondelete="RESTRICT"), index=True
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    source_item_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_item_id: Mapped[int | None] = mapped_column(BigInteger)
    title_snapshot: Mapped[str] = mapped_column(String(255), nullable=False)
    description_snapshot: Mapped[str | None] = mapped_column(Text)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    unit_snapshot: Mapped[str] = mapped_column(String(40), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    line_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    invoice: Mapped[BillingInvoice] = relationship(back_populates="items")

    __table_args__ = (
        UniqueConstraint("invoice_id", "sequence", name="uq_billing_invoice_item_sequence"),
        CheckConstraint("sequence > 0", name="ck_billing_item_sequence"),
        CheckConstraint("quantity > 0", name="ck_billing_item_quantity"),
        CheckConstraint("unit_price >= 0", name="ck_billing_item_unit_price"),
        CheckConstraint("line_total >= 0", name="ck_billing_item_line_total"),
    )


class BillingCommissionSnapshot(Base):
    __tablename__ = "finance_billing_commission_snapshots"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    invoice_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("finance_billing_invoices.id", ondelete="RESTRICT"), unique=True
    )
    policy_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("finance_commission_policies.id", ondelete="SET NULL"), index=True
    )
    legacy_snapshot_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("commission_snapshots.id", ondelete="RESTRICT"), unique=True
    )
    calculation_type: Mapped[str] = mapped_column(String(30), nullable=False)
    percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    base_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    platform_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    provider_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    invoice: Mapped[BillingInvoice] = relationship(back_populates="commission_snapshot")

    __table_args__ = (
        CheckConstraint("percent >= 0 AND percent <= 100", name="ck_billing_commission_percent"),
        CheckConstraint("base_amount >= 0", name="ck_billing_commission_base"),
        CheckConstraint("platform_amount >= 0", name="ck_billing_commission_platform"),
        CheckConstraint("provider_amount >= 0", name="ck_billing_commission_provider"),
    )


class WalletAccount(Base):
    __tablename__ = "finance_wallet_accounts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    owner_user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="RESTRICT"), index=True
    )
    account_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    account_kind: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    purpose: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    currency: Mapped[str] = mapped_column(
        String(10), default=CurrencyCode.TOMAN.value, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), default=AccountStatus.ACTIVE.value, nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime)

    entries: Mapped[list["LedgerEntry"]] = relationship(back_populates="account")

    __table_args__ = (
        UniqueConstraint(
            "owner_user_id", "purpose", "currency", name="uq_wallet_owner_purpose_currency"
        ),
        CheckConstraint("currency = 'TOMAN'", name="ck_wallet_accounts_currency_toman"),
        Index("ix_wallet_accounts_owner_status", "owner_user_id", "status"),
    )


class LedgerTransaction(Base):
    __tablename__ = "finance_ledger_transactions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    journal_number: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(180), unique=True, nullable=False)
    legacy_transaction_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("finance_transactions.id", ondelete="RESTRICT"),
        unique=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20), default=LedgerStatus.POSTED.value, nullable=False, index=True
    )
    currency: Mapped[str] = mapped_column(
        String(10), default=CurrencyCode.TOMAN.value, nullable=False
    )
    total_debit: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    total_credit: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    reversal_of_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("finance_ledger_transactions.id", ondelete="RESTRICT"),
        index=True,
    )
    actor_user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="SET NULL"), index=True
    )
    trace_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    posted_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    entries: Mapped[list["LedgerEntry"]] = relationship(
        back_populates="transaction", cascade="all, delete-orphan"
    )
    reversal_of: Mapped["LedgerTransaction | None"] = relationship(
        remote_side="LedgerTransaction.id"
    )

    __table_args__ = (
        UniqueConstraint("reversal_of_id", name="uq_ledger_transaction_reversal"),
        CheckConstraint("currency = 'TOMAN'", name="ck_ledger_transactions_currency_toman"),
        CheckConstraint("total_debit > 0", name="ck_ledger_transactions_debit_positive"),
        CheckConstraint("total_credit > 0", name="ck_ledger_transactions_credit_positive"),
        CheckConstraint(
            "total_debit = total_credit", name="ck_ledger_transactions_balanced_totals"
        ),
        Index("ix_ledger_transactions_source", "source_type", "source_id"),
        Index("ix_ledger_transactions_posted", "posted_at", "id"),
    )


class LedgerEntry(Base):
    __tablename__ = "finance_ledger_entries"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    transaction_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("finance_ledger_transactions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    account_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("finance_wallet_accounts.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    side: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(
        String(10), default=CurrencyCode.TOMAN.value, nullable=False
    )
    memo: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    transaction: Mapped[LedgerTransaction] = relationship(back_populates="entries")
    account: Mapped[WalletAccount] = relationship(back_populates="entries")

    __table_args__ = (
        UniqueConstraint("transaction_id", "sequence", name="uq_ledger_entry_sequence"),
        CheckConstraint("sequence > 0", name="ck_ledger_entries_sequence_positive"),
        CheckConstraint("side IN ('debit', 'credit')", name="ck_ledger_entries_side"),
        CheckConstraint("amount > 0", name="ck_ledger_entries_amount_positive"),
        CheckConstraint("currency = 'TOMAN'", name="ck_ledger_entries_currency_toman"),
        Index("ix_ledger_entries_account_created", "account_id", "created_at"),
    )


def _reject_posted_ledger_mutation(_mapper, _connection, target) -> None:
    raise RuntimeError(f"Posted ledger record {target.__class__.__name__} is immutable")


def _protect_final_price_update(_mapper, _connection, target) -> None:
    history = inspect(target).attrs.status.history
    if history.deleted and history.deleted[0] == FinalPriceProposalStatus.ACCEPTED.value:
        raise RuntimeError("Accepted final-price proposal is immutable")


def _protect_final_price_delete(_mapper, _connection, _target) -> None:
    raise RuntimeError("Final-price proposal history cannot be deleted")


def _protect_rental_terms_update(_mapper, _connection, target) -> None:
    immutable = (
        "rental_request_id",
        "payer_user_id",
        "provider_user_id",
        "pricing_rule_id_snapshot",
        "requested_units_snapshot",
        "unit_price_snapshot",
        "rental_revenue_amount",
        "deposit_principal_amount",
        "funding_total_amount",
        "currency",
        "accepted_at",
    )
    state = inspect(target)
    if any(getattr(state.attrs, name).history.has_changes() for name in immutable):
        raise RuntimeError("Accepted rental financial amounts are immutable")


def _protect_rental_terms_delete(_mapper, _connection, _target) -> None:
    raise RuntimeError("Rental financial terms cannot be deleted")


def _protect_settlement_update(_mapper, _connection, target) -> None:
    immutable = (
        "requester_user_id",
        "idempotency_key",
        "amount",
        "currency",
        "reserve_journal_id",
        "requested_at",
    )
    state = inspect(target)
    if any(getattr(state.attrs, name).history.has_changes() for name in immutable):
        raise RuntimeError("Settlement request financial identity is immutable")


def _protect_settlement_delete(_mapper, _connection, _target) -> None:
    raise RuntimeError("Settlement request history cannot be deleted")


for _model in (LedgerTransaction, LedgerEntry, BillingInvoiceItem, BillingCommissionSnapshot):
    event.listen(_model, "before_update", _reject_posted_ledger_mutation)
    event.listen(_model, "before_delete", _reject_posted_ledger_mutation)

event.listen(FinalPriceProposal, "before_update", _protect_final_price_update)
event.listen(FinalPriceProposal, "before_delete", _protect_final_price_delete)
event.listen(RentalFinancialTerms, "before_update", _protect_rental_terms_update)
event.listen(RentalFinancialTerms, "before_delete", _protect_rental_terms_delete)
event.listen(SettlementRequest, "before_update", _protect_settlement_update)
event.listen(SettlementRequest, "before_delete", _protect_settlement_delete)

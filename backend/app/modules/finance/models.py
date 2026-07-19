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
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.money import CurrencyCode
from app.db.base import Base
from app.modules.finance.enums import AccountStatus, LedgerStatus


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


for _model in (LedgerTransaction, LedgerEntry):
    event.listen(_model, "before_update", _reject_posted_ledger_mutation)
    event.listen(_model, "before_delete", _reject_posted_ledger_mutation)

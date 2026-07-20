from datetime import datetime
from decimal import Decimal

from sqlalchemy import case, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.common.money import BillableSourceType, CurrencyCode, FinancialEventType
from app.modules.finance.enums import AccountKind, AccountPurpose, EntrySide, LedgerStatus
from app.modules.finance.models import LedgerEntry, LedgerTransaction, WalletAccount
from app.modules.finance.schemas import LedgerReconciliationOut
from app.modules.finance.settlement_service import LedgerMovementService
from app.modules.finance.billing_service import UniversalBillingService
from app.modules.orders.enums import FinancialTransactionStatus, FinancialTransactionType
from app.modules.orders.models import FinancialInvoice, FinancialTransaction
from app.modules.stores.models import Store


class OrderLedgerBridge:
    def __init__(self, db: Session) -> None:
        self.db = db

    def post_payment(
        self,
        *,
        invoice: FinancialInvoice,
        transaction: FinancialTransaction,
        actor_user_id: int | None,
        trace_id: str,
    ) -> LedgerTransaction:
        journal = self._post(
            invoice=invoice,
            transaction=transaction,
            actor_user_id=actor_user_id,
            trace_id=trace_id,
            event_type=FinancialEventType.PAYMENT.value,
            lines=(
                (AccountPurpose.PLATFORM_CASH, None, AccountKind.ASSET, EntrySide.DEBIT, invoice.total_amount),
                (AccountPurpose.PROVIDER_PENDING, self._provider_id(invoice), AccountKind.LIABILITY, EntrySide.CREDIT, invoice.provider_amount),
                (AccountPurpose.PLATFORM_REVENUE, None, AccountKind.REVENUE, EntrySide.CREDIT, invoice.platform_amount),
            ),
        )
        UniversalBillingService(self.db).mark_paid(
            legacy_invoice_id=invoice.id, paid_at=invoice.paid_at
        )
        return journal

    def post_refund(
        self,
        *,
        invoice: FinancialInvoice,
        transaction: FinancialTransaction,
        actor_user_id: int | None,
        trace_id: str,
    ) -> LedgerTransaction:
        provider_id = self._provider_id(invoice)
        LedgerMovementService(self.db).reverse_order_release_for_refund(
            order_id=invoice.order_id,
            provider_user_id=provider_id,
            amount=invoice.provider_amount,
            actor_user_id=actor_user_id,
            trace_id=trace_id,
        )
        journal = self._post(
            invoice=invoice,
            transaction=transaction,
            actor_user_id=actor_user_id,
            trace_id=trace_id,
            event_type=FinancialEventType.REFUND.value,
            lines=(
                (AccountPurpose.PROVIDER_PENDING, provider_id, AccountKind.LIABILITY, EntrySide.DEBIT, invoice.provider_amount),
                (AccountPurpose.PLATFORM_REVENUE, None, AccountKind.REVENUE, EntrySide.DEBIT, invoice.platform_amount),
                (AccountPurpose.PLATFORM_CASH, None, AccountKind.ASSET, EntrySide.CREDIT, invoice.total_amount),
            ),
        )
        UniversalBillingService(self.db).mark_refunded(
            legacy_invoice_id=invoice.id, refunded_at=invoice.refunded_at
        )
        return journal

    def _provider_id(self, invoice: FinancialInvoice) -> int:
        owner_id = self.db.query(Store.owner_user_id).filter(Store.id == invoice.store_id).scalar()
        if owner_id is None:
            raise ValueError("Invoice store owner is missing")
        return owner_id

    def _post(self, *, invoice, transaction, actor_user_id, trace_id, event_type, lines):
        existing = self.db.query(LedgerTransaction).filter(
            LedgerTransaction.legacy_transaction_id == transaction.id
        ).one_or_none()
        if existing is not None:
            return existing
        if invoice.currency != CurrencyCode.TOMAN.value or transaction.currency != CurrencyCode.TOMAN.value:
            raise ValueError("Order ledger bridge accepts TOMAN only")
        lines = tuple(line for line in lines if Decimal(line[-1]) > 0)
        debit = sum(
            (Decimal(amount) for *_, side, amount in lines if side == EntrySide.DEBIT),
            Decimal("0"),
        )
        credit = sum(
            (Decimal(amount) for *_, side, amount in lines if side == EntrySide.CREDIT),
            Decimal("0"),
        )
        if debit <= 0 or debit != credit:
            raise ValueError("Ledger journal must be positive and balanced")
        journal = LedgerTransaction(
            journal_number=f"JRN-ORDER-{event_type.upper()}-{transaction.id}",
            event_type=event_type,
            source_type=BillableSourceType.PRODUCT_ORDER.value,
            source_id=invoice.order_id,
            idempotency_key=f"order-finance:{transaction.id}",
            legacy_transaction_id=transaction.id,
            status=LedgerStatus.POSTED.value,
            currency=CurrencyCode.TOMAN.value,
            total_debit=debit,
            total_credit=credit,
            actor_user_id=actor_user_id,
            trace_id=trace_id,
            description=f"Order {event_type} ledger bridge",
            posted_at=transaction.occurred_at or datetime.utcnow(),
        )
        self.db.add(journal)
        self.db.flush()
        for sequence, (purpose, owner_id, kind, side, amount) in enumerate(lines, 1):
            account = self._account(purpose=purpose.value, owner_id=owner_id, kind=kind.value)
            self.db.add(LedgerEntry(
                transaction_id=journal.id, account_id=account.id, sequence=sequence,
                side=side.value, amount=amount, currency=CurrencyCode.TOMAN.value,
            ))
        self.db.flush()
        return journal

    def _account(self, *, purpose: str, owner_id: int | None, kind: str) -> WalletAccount:
        code = f"{'system' if owner_id is None else f'user:{owner_id}'}:{purpose}:TOMAN"
        row = self.db.query(WalletAccount).filter(WalletAccount.account_code == code).with_for_update().one_or_none()
        if row is not None:
            return row
        try:
            with self.db.begin_nested():
                row = WalletAccount(
                    owner_user_id=owner_id, account_code=code, account_kind=kind,
                    purpose=purpose, currency=CurrencyCode.TOMAN.value,
                )
                self.db.add(row)
                self.db.flush()
            return row
        except IntegrityError:
            return self.db.query(WalletAccount).filter(WalletAccount.account_code == code).with_for_update().one()


class LedgerReconciliationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def run(self) -> LedgerReconciliationOut:
        successful = self.db.query(FinancialTransaction).filter(
            FinancialTransaction.status == FinancialTransactionStatus.SUCCEEDED.value
        )
        payment_ids = [row[0] for row in successful.with_entities(FinancialTransaction.id).filter(
            FinancialTransaction.transaction_type == FinancialTransactionType.PAYMENT.value
        ).all()]
        refund_ids = [row[0] for row in successful.with_entities(FinancialTransaction.id).filter(
            FinancialTransaction.transaction_type == FinancialTransactionType.REFUND.value
        ).all()]
        linked = {row[0] for row in self.db.query(LedgerTransaction.legacy_transaction_id).filter(
            LedgerTransaction.legacy_transaction_id.is_not(None)
        ).all()}
        unbalanced = [row[0] for row in self.db.query(LedgerTransaction.id).filter(
            LedgerTransaction.total_debit != LedgerTransaction.total_credit
        ).all()]
        debit_sum = func.sum(case((LedgerEntry.side == EntrySide.DEBIT.value, LedgerEntry.amount), else_=0))
        credit_sum = func.sum(case((LedgerEntry.side == EntrySide.CREDIT.value, LedgerEntry.amount), else_=0))
        mismatch = [row[0] for row in self.db.query(LedgerEntry.transaction_id).group_by(
            LedgerEntry.transaction_id
        ).having((debit_sum != credit_sum) | (func.count(LedgerEntry.id) < 2)).all()]
        return LedgerReconciliationOut(
            successful_payment_transactions=len(payment_ids),
            successful_refund_transactions=len(refund_ids),
            posted_payment_journals=len(set(payment_ids) & linked),
            posted_refund_journals=len(set(refund_ids) & linked),
            missing_payment_transaction_ids=sorted(set(payment_ids) - linked),
            missing_refund_transaction_ids=sorted(set(refund_ids) - linked),
            unbalanced_journal_ids=unbalanced,
            entry_mismatch_journal_ids=mismatch,
        )

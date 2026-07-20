from datetime import datetime
from decimal import Decimal
import hashlib

from sqlalchemy import case, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.common.money import BillableSourceType, CurrencyCode, FinancialEventType
from app.modules.finance.enums import (
    AccountKind,
    AccountPurpose,
    EntrySide,
    LedgerStatus,
    SettlementStatus,
)
from app.modules.finance.models import (
    BillingInvoice,
    LedgerEntry,
    LedgerTransaction,
    SettlementRequest,
    WalletAccount,
)
from app.modules.finance.schemas import SettlementOut, WalletBalanceOut
from app.modules.orders.enums import OrderStatus, PaymentStatus
from app.modules.orders.models import Order


class SettlementContractError(ValueError):
    pass


class LedgerMovementService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def release_delivered_order(
        self, *, order: Order, actor_user_id: int, trace_id: str
    ) -> LedgerTransaction:
        if order.status != OrderStatus.DELIVERED.value:
            raise SettlementContractError("Only a delivered order can release balance")
        if order.payment_status != PaymentStatus.PAID.value:
            raise SettlementContractError("Only paid order revenue can be released")
        invoice = (
            self.db.query(BillingInvoice)
            .filter(
                BillingInvoice.source_type == BillableSourceType.PRODUCT_ORDER.value,
                BillingInvoice.source_id == order.id,
            )
            .one_or_none()
        )
        if invoice is None or invoice.status != "paid":
            raise SettlementContractError("Paid universal invoice is required for release")
        return self._post(
            event_type=FinancialEventType.RELEASE.value,
            source_type=BillableSourceType.PRODUCT_ORDER.value,
            source_id=order.id,
            idempotency_key=f"release:product_order:{order.id}",
            actor_user_id=actor_user_id,
            trace_id=trace_id,
            description=f"Release delivered order {order.id} provider balance",
            lines=(
                (
                    AccountPurpose.PROVIDER_PENDING,
                    invoice.provider_user_id,
                    EntrySide.DEBIT,
                    invoice.provider_amount,
                ),
                (
                    AccountPurpose.PROVIDER_AVAILABLE,
                    invoice.provider_user_id,
                    EntrySide.CREDIT,
                    invoice.provider_amount,
                ),
            ),
        )

    def post_settlement_reserve(
        self, *, user_id: int, amount: Decimal, key: str, trace_id: str
    ) -> LedgerTransaction:
        available_code = f"user:{user_id}:{AccountPurpose.PROVIDER_AVAILABLE.value}:TOMAN"
        available_account = (
            self.db.query(WalletAccount)
            .filter(WalletAccount.account_code == available_code)
            .with_for_update()
            .one_or_none()
        )
        if available_account is None:
            raise SettlementContractError("Settlement amount exceeds available balance")
        if amount > self.balance(user_id).available_amount:
            raise SettlementContractError("Settlement amount exceeds available balance")
        return self._post(
            event_type="settlement_reserve",
            source_type="settlement_request",
            source_id=user_id,
            idempotency_key=f"settlement:reserve:{key}",
            actor_user_id=user_id,
            trace_id=trace_id,
            description="Reserve provider available balance for settlement",
            lines=(
                (AccountPurpose.PROVIDER_AVAILABLE, user_id, EntrySide.DEBIT, amount),
                (AccountPurpose.PROVIDER_RESERVED, user_id, EntrySide.CREDIT, amount),
            ),
        )

    def post_settlement_reject(
        self, *, row: SettlementRequest, actor_user_id: int, trace_id: str
    ) -> LedgerTransaction:
        return self._post(
            event_type="settlement_rejected",
            source_type="settlement_request",
            source_id=row.id,
            idempotency_key=f"settlement:reject:{row.id}",
            actor_user_id=actor_user_id,
            trace_id=trace_id,
            description="Return rejected settlement to available balance",
            lines=(
                (
                    AccountPurpose.PROVIDER_RESERVED,
                    row.requester_user_id,
                    EntrySide.DEBIT,
                    row.amount,
                ),
                (
                    AccountPurpose.PROVIDER_AVAILABLE,
                    row.requester_user_id,
                    EntrySide.CREDIT,
                    row.amount,
                ),
            ),
        )

    def post_simulated_payout(
        self, *, row: SettlementRequest, actor_user_id: int, trace_id: str
    ) -> LedgerTransaction:
        return self._post(
            event_type=FinancialEventType.SETTLEMENT.value,
            source_type="settlement_request",
            source_id=row.id,
            idempotency_key=f"settlement:simulated:{row.id}",
            actor_user_id=actor_user_id,
            trace_id=trace_id,
            description="Simulated payout to clearing; no bank transfer",
            lines=(
                (
                    AccountPurpose.PROVIDER_RESERVED,
                    row.requester_user_id,
                    EntrySide.DEBIT,
                    row.amount,
                ),
                (AccountPurpose.PAYOUT_CLEARING, None, EntrySide.CREDIT, row.amount),
            ),
        )

    def reverse_order_release_for_refund(
        self, *, order_id: int, provider_user_id: int, amount: Decimal,
        actor_user_id: int, trace_id: str,
    ) -> LedgerTransaction | None:
        release = (
            self.db.query(LedgerTransaction)
            .filter(
                LedgerTransaction.idempotency_key == f"release:product_order:{order_id}"
            )
            .with_for_update()
            .one_or_none()
        )
        if release is None:
            return None
        existing = (
            self.db.query(LedgerTransaction)
            .filter(LedgerTransaction.reversal_of_id == release.id)
            .one_or_none()
        )
        if existing is not None:
            return existing
        self._lock_account(AccountPurpose.PROVIDER_AVAILABLE, provider_user_id)
        if self.balance(provider_user_id).available_amount < amount:
            raise SettlementContractError(
                "Refund is blocked because released provider funds are reserved or settled"
            )
        return self._post(
            event_type=FinancialEventType.REVERSAL.value,
            source_type=BillableSourceType.PRODUCT_ORDER.value,
            source_id=order_id,
            idempotency_key=f"reversal:release:product_order:{order_id}",
            actor_user_id=actor_user_id,
            trace_id=trace_id,
            description=f"Reverse order {order_id} release before refund",
            reversal_of_id=release.id,
            lines=(
                (AccountPurpose.PROVIDER_AVAILABLE, provider_user_id, EntrySide.DEBIT, amount),
                (AccountPurpose.PROVIDER_PENDING, provider_user_id, EntrySide.CREDIT, amount),
            ),
        )

    def post_adjustment(
        self, *, provider_user_id: int, amount: Decimal, direction: str,
        idempotency_key: str, reason: str, actor_user_id: int, trace_id: str,
    ) -> LedgerTransaction:
        existing = self.db.query(LedgerTransaction).filter(
            LedgerTransaction.idempotency_key == f"adjustment:{idempotency_key}"
        ).one_or_none()
        if existing is not None:
            expected_description = f"{direction}: {reason}"
            if (
                existing.source_id != provider_user_id
                or existing.total_debit != amount
                or existing.description != expected_description
            ):
                raise SettlementContractError("Adjustment idempotency key payload conflict")
            return existing
        self._lock_account(AccountPurpose.PROVIDER_AVAILABLE, provider_user_id)
        if direction == "debit" and self.balance(provider_user_id).available_amount < amount:
            raise SettlementContractError("Adjustment exceeds provider available balance")
        provider_side = EntrySide.CREDIT if direction == "credit" else EntrySide.DEBIT
        clearing_side = EntrySide.DEBIT if direction == "credit" else EntrySide.CREDIT
        return self._post(
            event_type="adjustment", source_type="provider_wallet",
            source_id=provider_user_id, idempotency_key=f"adjustment:{idempotency_key}",
            actor_user_id=actor_user_id, trace_id=trace_id,
            description=f"{direction}: {reason}",
            lines=(
                (AccountPurpose.ADJUSTMENT_CLEARING, None, clearing_side, amount),
                (AccountPurpose.PROVIDER_AVAILABLE, provider_user_id, provider_side, amount),
            ),
        )

    def balance(self, user_id: int) -> WalletBalanceOut:
        values = {}
        for purpose in (
            AccountPurpose.PROVIDER_PENDING,
            AccountPurpose.PROVIDER_AVAILABLE,
            AccountPurpose.PROVIDER_RESERVED,
        ):
            credit = func.coalesce(
                func.sum(
                    case((LedgerEntry.side == EntrySide.CREDIT.value, LedgerEntry.amount), else_=0)
                ),
                0,
            )
            debit = func.coalesce(
                func.sum(
                    case((LedgerEntry.side == EntrySide.DEBIT.value, LedgerEntry.amount), else_=0)
                ),
                0,
            )
            amount = (
                self.db.query(credit - debit)
                .select_from(WalletAccount)
                .outerjoin(LedgerEntry, LedgerEntry.account_id == WalletAccount.id)
                .filter(
                    WalletAccount.owner_user_id == user_id,
                    WalletAccount.purpose == purpose.value,
                    WalletAccount.currency == CurrencyCode.TOMAN.value,
                )
                .scalar()
            )
            values[purpose.value] = Decimal(amount or 0)
        return WalletBalanceOut(
            currency=CurrencyCode.TOMAN.value,
            pending_amount=values[AccountPurpose.PROVIDER_PENDING.value],
            available_amount=values[AccountPurpose.PROVIDER_AVAILABLE.value],
            reserved_amount=values[AccountPurpose.PROVIDER_RESERVED.value],
        )

    def _post(
        self,
        *,
        event_type,
        source_type,
        source_id,
        idempotency_key,
        actor_user_id,
        trace_id,
        description,
        lines,
        reversal_of_id=None,
    ) -> LedgerTransaction:
        existing = (
            self.db.query(LedgerTransaction)
            .filter(LedgerTransaction.idempotency_key == idempotency_key)
            .one_or_none()
        )
        if existing is not None:
            return existing
        lines = tuple(line for line in lines if Decimal(line[-1]) > 0)
        debit = sum(
            (Decimal(amount) for *_, side, amount in lines if side == EntrySide.DEBIT), Decimal("0")
        )
        credit = sum(
            (Decimal(amount) for *_, side, amount in lines if side == EntrySide.CREDIT),
            Decimal("0"),
        )
        if debit <= 0 or debit != credit:
            raise SettlementContractError("Ledger movement must be positive and balanced")
        journal_suffix = hashlib.sha256(idempotency_key.encode("utf-8")).hexdigest()[:16].upper()
        journal = LedgerTransaction(
            journal_number=f"JRN-{event_type.upper()}-{journal_suffix}",
            event_type=event_type,
            source_type=source_type,
            source_id=source_id,
            idempotency_key=idempotency_key,
            status=LedgerStatus.POSTED.value,
            currency=CurrencyCode.TOMAN.value,
            total_debit=debit,
            total_credit=credit,
            reversal_of_id=reversal_of_id,
            actor_user_id=actor_user_id,
            trace_id=trace_id,
            description=description,
            posted_at=datetime.utcnow(),
        )
        self.db.add(journal)
        self.db.flush()
        for sequence, (purpose, owner_id, side, amount) in enumerate(lines, 1):
            account = self._account(purpose=purpose, owner_id=owner_id)
            self.db.add(
                LedgerEntry(
                    transaction_id=journal.id,
                    account_id=account.id,
                    sequence=sequence,
                    side=side.value,
                    amount=amount,
                    currency=CurrencyCode.TOMAN.value,
                )
            )
        self.db.flush()
        return journal

    def _lock_account(self, purpose: AccountPurpose, owner_id: int | None) -> WalletAccount:
        return self._account(purpose=purpose, owner_id=owner_id)

    def _account(self, *, purpose: AccountPurpose, owner_id: int | None) -> WalletAccount:
        code = f"{'system' if owner_id is None else f'user:{owner_id}'}:{purpose.value}:TOMAN"
        row = (
            self.db.query(WalletAccount)
            .filter(WalletAccount.account_code == code)
            .with_for_update()
            .one_or_none()
        )
        if row is not None:
            return row
        kind = AccountKind.LIABILITY.value
        try:
            with self.db.begin_nested():
                row = WalletAccount(
                    owner_user_id=owner_id,
                    account_code=code,
                    account_kind=kind,
                    purpose=purpose.value,
                    currency=CurrencyCode.TOMAN.value,
                )
                self.db.add(row)
                self.db.flush()
            return row
        except IntegrityError:
            return (
                self.db.query(WalletAccount)
                .filter(WalletAccount.account_code == code)
                .with_for_update()
                .one()
            )


class SettlementService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.ledger = LedgerMovementService(db)

    def create(
        self,
        *,
        user_id: int,
        amount: Decimal,
        currency: str,
        idempotency_key: str,
        note: str | None,
        trace_id: str,
    ) -> SettlementRequest:
        existing = (
            self.db.query(SettlementRequest)
            .filter(SettlementRequest.idempotency_key == idempotency_key)
            .with_for_update()
            .one_or_none()
        )
        if existing is not None:
            if existing.requester_user_id != user_id or existing.amount != amount:
                raise SettlementContractError("Idempotency key payload conflict")
            return existing
        if currency != CurrencyCode.TOMAN.value:
            raise SettlementContractError("Settlement accepts TOMAN only")
        journal = self.ledger.post_settlement_reserve(
            user_id=user_id, amount=amount, key=idempotency_key, trace_id=trace_id
        )
        row = SettlementRequest(
            requester_user_id=user_id,
            idempotency_key=idempotency_key,
            amount=amount,
            currency=currency,
            status=SettlementStatus.REQUESTED.value,
            reserve_journal_id=journal.id,
            note=note,
            requested_at=datetime.utcnow(),
        )
        self.db.add(row)
        self.db.flush()
        return row

    def decide(
        self,
        *,
        settlement_id: int,
        approve: bool,
        admin_user_id: int,
        admin_note: str | None,
        trace_id: str,
    ) -> SettlementRequest:
        row = self._get(settlement_id)
        if row.status != SettlementStatus.REQUESTED.value:
            raise SettlementContractError("Settlement is not awaiting decision")
        row.decided_by_user_id = admin_user_id
        row.decided_at = datetime.utcnow()
        row.admin_note = admin_note
        if approve:
            row.status = SettlementStatus.APPROVED.value
        else:
            journal = self.ledger.post_settlement_reject(
                row=row, actor_user_id=admin_user_id, trace_id=trace_id
            )
            row.decision_journal_id = journal.id
            row.status = SettlementStatus.REJECTED.value
        return row

    def simulate_payout(
        self, *, settlement_id: int, admin_user_id: int, trace_id: str
    ) -> SettlementRequest:
        row = self._get(settlement_id)
        if row.status == SettlementStatus.SIMULATED_COMPLETED.value:
            return row
        if row.status != SettlementStatus.APPROVED.value:
            raise SettlementContractError("Only approved settlement can be simulated")
        journal = self.ledger.post_simulated_payout(
            row=row, actor_user_id=admin_user_id, trace_id=trace_id
        )
        row.decision_journal_id = journal.id
        row.status = SettlementStatus.SIMULATED_COMPLETED.value
        row.simulated_completed_at = datetime.utcnow()
        return row

    def _get(self, settlement_id: int) -> SettlementRequest:
        row = (
            self.db.query(SettlementRequest)
            .filter(SettlementRequest.id == settlement_id)
            .with_for_update()
            .one_or_none()
        )
        if row is None:
            raise SettlementContractError("Settlement not found")
        return row

    @staticmethod
    def output(row: SettlementRequest) -> SettlementOut:
        return SettlementOut(
            id=row.id,
            requester_user_id=row.requester_user_id,
            amount=row.amount,
            currency=row.currency,
            status=row.status,
            note=row.note,
            admin_note=row.admin_note,
            requested_at=row.requested_at,
            decided_at=row.decided_at,
            simulated_completed_at=row.simulated_completed_at,
        )

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.common.money import BillableSourceType, CurrencyCode
from app.modules.finance.enums import (
    BillingInvoiceStatus,
    CommissionPolicyStatus,
    FinalPriceProposalStatus,
)
from app.modules.finance.models import (
    BillingRefund,
    BillingCommissionSnapshot,
    BillingInvoice,
    BillingInvoiceItem,
    CommissionPolicy,
    FinalPriceProposal,
)
from app.modules.finance.schemas import FinalPriceProposalOut


class FinalPriceContractError(ValueError):
    pass


class FinalPriceService:
    ALLOWED_SOURCES = {
        BillableSourceType.SERVICE_REQUEST.value,
        BillableSourceType.CONSULTATION_REQUEST.value,
    }

    def __init__(self, db: Session) -> None:
        self.db = db

    def propose(
        self,
        *,
        source_type: str,
        source_id: int,
        payer_user_id: int,
        provider_user_id: int,
        actor_user_id: int,
        amount: Decimal,
        currency: str,
        description: str,
    ) -> FinalPriceProposal:
        self._validate_source(source_type)
        if actor_user_id != provider_user_id:
            raise FinalPriceContractError("Only the assigned provider may propose final price")
        if payer_user_id == provider_user_id:
            raise FinalPriceContractError("Payer and provider must be different users")
        if currency != CurrencyCode.TOMAN.value or amount <= 0:
            raise FinalPriceContractError("Final price must be positive TOMAN")
        accepted = self._accepted(source_type, source_id)
        if accepted is not None:
            raise FinalPriceContractError("Accepted final price is immutable")

        active = self._active(source_type, source_id)
        if active is not None:
            active.status = FinalPriceProposalStatus.SUPERSEDED.value
            active.active_scope = None
            active.decided_at = datetime.utcnow()

        latest_version = (
            self.db.query(FinalPriceProposal.version)
            .filter(
                FinalPriceProposal.source_type == source_type,
                FinalPriceProposal.source_id == source_id,
            )
            .order_by(FinalPriceProposal.version.desc())
            .with_for_update()
            .first()
        )
        version = (latest_version[0] if latest_version else 0) + 1
        scope = f"{source_type}:{source_id}"
        row = FinalPriceProposal(
            source_type=source_type,
            source_id=source_id,
            version=version,
            payer_user_id=payer_user_id,
            provider_user_id=provider_user_id,
            proposed_by_user_id=actor_user_id,
            amount=amount,
            currency=currency,
            description_snapshot=description,
            status=FinalPriceProposalStatus.PROPOSED.value,
            active_scope=scope,
            proposed_at=datetime.utcnow(),
        )
        self.db.add(row)
        self.db.flush()
        return row

    def decide(
        self,
        *,
        source_type: str,
        source_id: int,
        actor_user_id: int,
        accept: bool,
        title: str,
    ) -> FinalPriceProposal:
        row = self._active(source_type, source_id)
        if row is None:
            accepted = self._accepted(source_type, source_id)
            if accepted is not None and accept and accepted.payer_user_id == actor_user_id:
                return accepted
            raise FinalPriceContractError("No active final-price proposal exists")
        if row.payer_user_id != actor_user_id:
            raise FinalPriceContractError("Only the requester may decide final price")

        policy = self._default_policy(source_type) if accept else None
        row.active_scope = None
        row.decided_by_user_id = actor_user_id
        row.decided_at = datetime.utcnow()
        if not accept:
            row.status = FinalPriceProposalStatus.REJECTED.value
            self.db.flush()
            return row

        row.status = FinalPriceProposalStatus.ACCEPTED.value
        row.accepted_scope = f"{source_type}:{source_id}"
        self.db.flush()
        self._create_invoice(row=row, policy=policy, title=title)
        return row

    def current(self, *, source_type: str, source_id: int) -> FinalPriceProposal | None:
        return self._accepted(source_type, source_id) or self._active(source_type, source_id)

    def require_accepted(self, *, source_type: str, source_id: int) -> FinalPriceProposal:
        row = self._accepted(source_type, source_id)
        if row is None:
            raise FinalPriceContractError("Accepted final price is required before work starts")
        return row

    def require_paid(self, *, source_type: str, source_id: int) -> BillingInvoice:
        self.require_accepted(source_type=source_type, source_id=source_id)
        invoice = (
            self.db.query(BillingInvoice)
            .filter(
                BillingInvoice.source_type == source_type,
                BillingInvoice.source_id == source_id,
            )
            .with_for_update()
            .one_or_none()
        )
        if invoice is None or invoice.status != BillingInvoiceStatus.PAID.value:
            raise FinalPriceContractError("Paid invoice is required before work starts")
        return invoice

    def cancel_unpaid_invoice(self, *, source_type: str, source_id: int) -> None:
        active = self._active(source_type, source_id)
        if active is not None:
            active.status = FinalPriceProposalStatus.SUPERSEDED.value
            active.active_scope = None
            active.decided_at = datetime.utcnow()
        row = (
            self.db.query(BillingInvoice)
            .filter(
                BillingInvoice.source_type == source_type,
                BillingInvoice.source_id == source_id,
            )
            .with_for_update()
            .one_or_none()
        )
        if row is None:
            return
        if row.status != BillingInvoiceStatus.PAYMENT_PENDING.value:
            raise FinalPriceContractError("A paid financial contract cannot be cancelled here")
        row.status = BillingInvoiceStatus.CANCELLED.value
        row.cancelled_at = datetime.utcnow()

    def output(self, row: FinalPriceProposal) -> FinalPriceProposalOut:
        invoice = (
            self.db.query(BillingInvoice.id, BillingInvoice.status)
            .filter(
                BillingInvoice.source_type == row.source_type,
                BillingInvoice.source_id == row.source_id,
            )
            .one_or_none()
        )
        refund = None
        if invoice is not None:
            refund = (
                self.db.query(BillingRefund)
                .filter(BillingRefund.invoice_id == invoice.id)
                .one_or_none()
            )
        return FinalPriceProposalOut(
            id=row.id,
            source_type=row.source_type,
            source_id=row.source_id,
            version=row.version,
            amount=row.amount,
            currency=row.currency,
            description=row.description_snapshot,
            status=row.status,
            proposed_by_user_id=row.proposed_by_user_id,
            decided_by_user_id=row.decided_by_user_id,
            proposed_at=row.proposed_at,
            decided_at=row.decided_at,
            invoice_id=invoice.id if invoice is not None else None,
            invoice_status=invoice.status if invoice is not None else None,
            refund_id=refund.id if refund is not None else None,
            refund_status=refund.status if refund is not None else None,
            refund_review_required=(
                refund.review_required if refund is not None else None
            ),
        )

    def _create_invoice(
        self, *, row: FinalPriceProposal, policy: CommissionPolicy, title: str
    ) -> BillingInvoice:
        existing = (
            self.db.query(BillingInvoice)
            .filter(
                BillingInvoice.source_type == row.source_type,
                BillingInvoice.source_id == row.source_id,
            )
            .one_or_none()
        )
        if existing is not None:
            return existing
        platform = (row.amount * policy.percent / Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        provider = row.amount - platform
        invoice = BillingInvoice(
            invoice_number=f"BILL-{row.source_type.upper()}-{row.source_id}",
            source_type=row.source_type,
            source_id=row.source_id,
            payer_user_id=row.payer_user_id,
            provider_user_id=row.provider_user_id,
            status=BillingInvoiceStatus.PAYMENT_PENDING.value,
            currency=CurrencyCode.TOMAN.value,
            subtotal_amount=row.amount,
            discount_amount=Decimal("0"),
            surcharge_amount=Decimal("0"),
            total_amount=row.amount,
            platform_amount=platform,
            provider_amount=provider,
            issued_at=row.decided_at or datetime.utcnow(),
        )
        self.db.add(invoice)
        self.db.flush()
        self.db.add(
            BillingInvoiceItem(
                invoice_id=invoice.id,
                sequence=1,
                source_item_type=f"{row.source_type}_final_price",
                source_item_id=row.id,
                title_snapshot=title,
                description_snapshot=row.description_snapshot,
                quantity=Decimal("1"),
                unit_snapshot="contract",
                unit_price=row.amount,
                line_total=row.amount,
            )
        )
        self.db.add(
            BillingCommissionSnapshot(
                invoice_id=invoice.id,
                policy_id=policy.id,
                calculation_type="percent",
                percent=policy.percent,
                base_amount=row.amount,
                platform_amount=platform,
                provider_amount=provider,
            )
        )
        self.db.flush()
        return invoice

    def _default_policy(self, source_type: str) -> CommissionPolicy:
        row = (
            self.db.query(CommissionPolicy)
            .filter(
                CommissionPolicy.source_type == source_type,
                CommissionPolicy.default_scope == source_type,
                CommissionPolicy.is_default.is_(True),
                CommissionPolicy.status == CommissionPolicyStatus.ACTIVE.value,
            )
            .with_for_update()
            .one_or_none()
        )
        if row is None:
            raise FinalPriceContractError(
                f"Active default commission policy is required for {source_type}"
            )
        return row

    def _active(self, source_type: str, source_id: int) -> FinalPriceProposal | None:
        return (
            self.db.query(FinalPriceProposal)
            .filter(FinalPriceProposal.active_scope == f"{source_type}:{source_id}")
            .with_for_update()
            .one_or_none()
        )

    def _accepted(self, source_type: str, source_id: int) -> FinalPriceProposal | None:
        return (
            self.db.query(FinalPriceProposal)
            .filter(FinalPriceProposal.accepted_scope == f"{source_type}:{source_id}")
            .with_for_update()
            .one_or_none()
        )

    def _validate_source(self, source_type: str) -> None:
        if source_type not in self.ALLOWED_SOURCES:
            raise FinalPriceContractError("Unsupported final-price source")

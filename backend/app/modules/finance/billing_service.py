from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.common.money import BillableSourceType, CurrencyCode
from app.modules.finance.enums import BillingInvoiceStatus, CommissionPolicyStatus
from app.modules.finance.models import (
    BillingCommissionSnapshot,
    BillingInvoice,
    BillingInvoiceItem,
    CommissionPolicy,
)
from app.modules.orders.models import (
    CommissionSnapshot,
    FinancialInvoice,
    FinancialInvoiceItem,
)
from app.modules.stores.models import Store


class UniversalBillingService:
    PRODUCT_POLICY_CODE = "product-order-default"

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_from_order(
        self,
        *,
        legacy_invoice: FinancialInvoice,
        legacy_snapshot: CommissionSnapshot,
    ) -> BillingInvoice:
        existing = self._by_legacy(legacy_invoice.id)
        if existing is not None:
            return existing
        if legacy_invoice.currency != CurrencyCode.TOMAN.value:
            raise ValueError("Universal billing accepts TOMAN only")
        if (
            legacy_invoice.platform_amount + legacy_invoice.provider_amount
            != legacy_invoice.total_amount
        ):
            raise ValueError("Invoice provider/platform split must equal total")
        provider_id = (
            self.db.query(Store.owner_user_id).filter(Store.id == legacy_invoice.store_id).scalar()
        )
        if provider_id is None:
            raise ValueError("Invoice store owner is missing")
        policy = self._policy(percent=legacy_snapshot.percent)
        row = BillingInvoice(
            invoice_number=f"BILL-{legacy_invoice.invoice_number}",
            source_type=BillableSourceType.PRODUCT_ORDER.value,
            source_id=legacy_invoice.order_id,
            legacy_invoice_id=legacy_invoice.id,
            payer_user_id=legacy_invoice.buyer_user_id,
            provider_user_id=provider_id,
            status=legacy_invoice.status,
            currency=CurrencyCode.TOMAN.value,
            subtotal_amount=legacy_invoice.subtotal_amount,
            discount_amount=legacy_invoice.discount_amount,
            surcharge_amount=legacy_invoice.shipping_amount,
            total_amount=legacy_invoice.total_amount,
            platform_amount=legacy_invoice.platform_amount,
            provider_amount=legacy_invoice.provider_amount,
            issued_at=legacy_invoice.issued_at,
        )
        self.db.add(row)
        self.db.flush()
        items = (
            self.db.query(FinancialInvoiceItem)
            .filter(FinancialInvoiceItem.invoice_id == legacy_invoice.id)
            .order_by(FinancialInvoiceItem.id)
            .all()
        )
        if (
            not items
            or sum((item.line_total for item in items), Decimal("0"))
            != legacy_invoice.subtotal_amount
        ):
            raise ValueError("Invoice item snapshots do not match subtotal")
        for sequence, item in enumerate(items, 1):
            self.db.add(
                BillingInvoiceItem(
                    invoice_id=row.id,
                    sequence=sequence,
                    source_item_type="product_order_item",
                    source_item_id=item.order_item_id,
                    title_snapshot=item.title_snapshot,
                    quantity=Decimal(item.quantity),
                    unit_snapshot=item.unit_snapshot,
                    unit_price=item.unit_price,
                    line_total=item.line_total,
                )
            )
        self.db.add(
            BillingCommissionSnapshot(
                invoice_id=row.id,
                policy_id=policy.id,
                legacy_snapshot_id=legacy_snapshot.id,
                calculation_type=legacy_snapshot.calculation_type,
                percent=legacy_snapshot.percent,
                base_amount=legacy_snapshot.base_amount,
                platform_amount=legacy_snapshot.platform_amount,
                provider_amount=legacy_snapshot.provider_amount,
            )
        )
        self.db.flush()
        return row

    def mark_paid(self, *, legacy_invoice_id: int, paid_at) -> None:
        row = self._ensure_legacy(legacy_invoice_id)
        row.status = BillingInvoiceStatus.PAID.value
        row.paid_at = paid_at

    def mark_refunded(self, *, legacy_invoice_id: int, refunded_at) -> None:
        row = self._ensure_legacy(legacy_invoice_id)
        row.status = BillingInvoiceStatus.REFUNDED.value
        row.refunded_at = refunded_at

    def mark_cancelled(self, *, legacy_invoice_id: int, cancelled_at) -> None:
        row = self._ensure_legacy(legacy_invoice_id)
        row.status = BillingInvoiceStatus.CANCELLED.value
        row.cancelled_at = cancelled_at

    def mark_refund_pending(self, *, legacy_invoice_id: int) -> None:
        row = self._ensure_legacy(legacy_invoice_id)
        row.status = BillingInvoiceStatus.REFUND_PENDING.value

    def _ensure_legacy(self, legacy_invoice_id: int) -> BillingInvoice:
        row = self._by_legacy(legacy_invoice_id)
        if row is not None:
            return row
        legacy_invoice = (
            self.db.query(FinancialInvoice)
            .filter(FinancialInvoice.id == legacy_invoice_id)
            .one_or_none()
        )
        legacy_snapshot = (
            self.db.query(CommissionSnapshot)
            .filter(CommissionSnapshot.invoice_id == legacy_invoice_id)
            .one_or_none()
        )
        if legacy_invoice is None or legacy_snapshot is None:
            raise ValueError("Legacy invoice billing contract is incomplete")
        return self.create_from_order(
            legacy_invoice=legacy_invoice,
            legacy_snapshot=legacy_snapshot,
        )

    def _by_legacy(self, legacy_invoice_id: int) -> BillingInvoice | None:
        return (
            self.db.query(BillingInvoice)
            .filter(BillingInvoice.legacy_invoice_id == legacy_invoice_id)
            .one_or_none()
        )

    def _policy(self, *, percent) -> CommissionPolicy:
        row = (
            self.db.query(CommissionPolicy)
            .filter(CommissionPolicy.code == self.PRODUCT_POLICY_CODE)
            .with_for_update()
            .one_or_none()
        )
        if row is None:
            try:
                with self.db.begin_nested():
                    row = CommissionPolicy(
                        code=self.PRODUCT_POLICY_CODE,
                        title="Default product order commission",
                        source_type=BillableSourceType.PRODUCT_ORDER.value,
                        default_scope=BillableSourceType.PRODUCT_ORDER.value,
                        percent=percent,
                        status=CommissionPolicyStatus.ACTIVE.value,
                        is_default=True,
                    )
                    self.db.add(row)
                    self.db.flush()
            except IntegrityError:
                row = (
                    self.db.query(CommissionPolicy)
                    .filter(CommissionPolicy.code == self.PRODUCT_POLICY_CODE)
                    .with_for_update()
                    .one()
                )
        if row.percent != percent:
            row.percent = percent
        return row

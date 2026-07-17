from app.modules.auth.exceptions import ValidationAuthError
from app.modules.orders.models import (
    AdminAuditLog,
    FinancialInvoice,
    FinancialRefund,
    FinancialTransaction,
    PaymentAttempt,
)
from app.modules.orders.repository import OrderRepository
from app.modules.orders.schemas import (
    AdminAuditLogOut,
    FinancialInvoiceOut,
    FinancialRefundOut,
    FinancialTransactionOut,
    PaymentAttemptOut,
)


class AdminFinanceService:
    MODELS = {
        "invoices": FinancialInvoice,
        "payment_attempts": PaymentAttempt,
        "transactions": FinancialTransaction,
        "refunds": FinancialRefund,
        "audit_logs": AdminAuditLog,
    }

    def __init__(self, db) -> None:
        self.repo = OrderRepository(db)

    def list_rows(self, *, resource: str, page: int, page_size: int):
        model = self.MODELS[resource]
        rows, total = self.repo.list_finance_rows(
            model, page=max(page, 1), page_size=min(max(page_size, 1), 100)
        )
        return [self._out(resource, row) for row in rows], total

    def get_invoice(self, *, invoice_id: int) -> FinancialInvoiceOut:
        row = self.repo.get_finance_row(FinancialInvoice, row_id=invoice_id)
        if row is None:
            raise ValidationAuthError(message="Invoice not found")
        return self._invoice(row)

    def _out(self, resource: str, row):
        schemas = {
            "invoices": FinancialInvoiceOut,
            "payment_attempts": PaymentAttemptOut,
            "transactions": FinancialTransactionOut,
            "refunds": FinancialRefundOut,
            "audit_logs": AdminAuditLogOut,
        }
        return self._schema(schemas[resource], row)

    def _invoice(self, row) -> FinancialInvoiceOut:
        return self._schema(FinancialInvoiceOut, row)

    def _schema(self, schema, row):
        values = {}
        for name in schema.model_fields:
            value = getattr(row, name)
            values[name] = value.isoformat() if hasattr(value, "isoformat") else value
        return schema(**values)

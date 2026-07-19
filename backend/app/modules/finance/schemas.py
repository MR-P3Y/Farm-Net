from pydantic import BaseModel


class LedgerReconciliationOut(BaseModel):
    successful_payment_transactions: int
    successful_refund_transactions: int
    posted_payment_journals: int
    posted_refund_journals: int
    missing_payment_transaction_ids: list[int]
    missing_refund_transaction_ids: list[int]
    unbalanced_journal_ids: list[int]
    entry_mismatch_journal_ids: list[int]

    @property
    def is_clean(self) -> bool:
        return not (
            self.missing_payment_transaction_ids
            or self.missing_refund_transaction_ids
            or self.unbalanced_journal_ids
            or self.entry_mismatch_journal_ids
        )

from datetime import datetime

from sqlalchemy.orm import Session

from app.common.money import CurrencyCode
from app.modules.finance.enums import RentalFinancialTermsStatus
from app.modules.finance.models import RentalFinancialTerms


class RentalFinancialContractError(ValueError):
    pass


class RentalFinancialService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def snapshot(self, *, request, provider_user_id: int) -> RentalFinancialTerms:
        existing = self._get(request.id)
        if existing is not None:
            return existing
        required = (
            request.price_per_unit_snapshot,
            request.rental_amount_snapshot,
            request.deposit_amount_snapshot,
            request.total_amount_snapshot,
        )
        if any(value is None for value in required):
            raise RentalFinancialContractError("Accepted rental snapshots are incomplete")
        if request.currency != CurrencyCode.TOMAN.value:
            raise RentalFinancialContractError("Rental financial terms accept TOMAN only")
        if request.rental_amount_snapshot <= 0 or request.deposit_amount_snapshot < 0:
            raise RentalFinancialContractError("Rental revenue/deposit values are invalid")
        if (
            request.rental_amount_snapshot + request.deposit_amount_snapshot
            != request.total_amount_snapshot
        ):
            raise RentalFinancialContractError("Rental total must equal revenue plus deposit")
        row = RentalFinancialTerms(
            rental_request_id=request.id,
            payer_user_id=request.requester_user_id,
            provider_user_id=provider_user_id,
            pricing_rule_id_snapshot=request.pricing_rule_id,
            requested_units_snapshot=request.requested_units,
            unit_price_snapshot=request.price_per_unit_snapshot,
            rental_revenue_amount=request.rental_amount_snapshot,
            deposit_principal_amount=request.deposit_amount_snapshot,
            funding_total_amount=request.total_amount_snapshot,
            currency=request.currency,
            status=RentalFinancialTermsStatus.UNFUNDED.value,
            accepted_at=request.accepted_at or datetime.utcnow(),
        )
        self.db.add(row)
        self.db.flush()
        return row

    def cancel_unfunded(self, *, rental_request_id: int, at: datetime) -> None:
        row = self._get(rental_request_id)
        if row is None:
            return
        if row.status != RentalFinancialTermsStatus.UNFUNDED.value:
            raise RentalFinancialContractError("Rental financial terms cannot be cancelled")
        row.status = RentalFinancialTermsStatus.CANCELLED_UNFUNDED.value
        row.cancelled_at = at

    def mark_operationally_completed_unfunded(
        self, *, rental_request_id: int, at: datetime
    ) -> None:
        row = self._get(rental_request_id)
        if row is None:
            raise RentalFinancialContractError("Rental financial terms are missing")
        if row.status != RentalFinancialTermsStatus.UNFUNDED.value:
            raise RentalFinancialContractError("Rental financial terms are not unfunded")
        row.status = RentalFinancialTermsStatus.OPERATIONALLY_COMPLETED_UNFUNDED.value
        row.operationally_completed_at = at

    def require(self, *, rental_request_id: int) -> RentalFinancialTerms:
        row = self._get(rental_request_id)
        if row is None:
            raise RentalFinancialContractError("Rental financial terms are missing")
        return row

    def _get(self, rental_request_id: int) -> RentalFinancialTerms | None:
        return (
            self.db.query(RentalFinancialTerms)
            .filter(RentalFinancialTerms.rental_request_id == rental_request_id)
            .with_for_update()
            .one_or_none()
        )

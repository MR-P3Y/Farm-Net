from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.modules.subscriptions.enums import UsageReservationStatus
from app.modules.subscriptions.models import (
    BillingFeatureUsage,
    BillingUsageReservation,
)
from app.modules.subscriptions.quota_repository import QuotaRepository
from app.modules.subscriptions.schemas import QuotaEstimateOut, QuotaReservationOut


class QuotaService:
    def __init__(self, db: Session, repo: QuotaRepository | None = None) -> None:
        self.repo = repo or QuotaRepository(db)

    def estimate(self, user_id: int, feature_code: str, amount: Decimal) -> QuotaEstimateOut:
        code = self._feature_code(feature_code)
        amount = self._amount(amount)
        usage = self._usage(user_id, code, _utcnow(), lock=False)
        return self._estimate_output(usage, amount)

    def reserve(
        self,
        user_id: int,
        feature_code: str,
        amount: Decimal,
        idempotency_key: str,
        *,
        expires_in_seconds: int = 300,
        context: dict | None = None,
    ) -> QuotaReservationOut:
        code = self._feature_code(feature_code)
        amount = self._amount(amount)
        key = self._idempotency_key(idempotency_key)
        if not 30 <= expires_in_seconds <= 3600:
            raise AppException(
                "BILLING_QUOTA_EXPIRY_INVALID",
                "Reservation expiry must be between 30 and 3600 seconds",
                422,
            )
        now = _utcnow()
        existing = self.repo.reservation_by_key(key, lock=True)
        if existing is not None:
            return self._replay(existing, user_id, code, amount)

        usage = self._usage(user_id, code, now, lock=True)
        self._expire_for_usage(usage, now)
        estimate = self._estimate_output(usage, amount)
        if not estimate.allowed:
            raise AppException(
                "BILLING_QUOTA_EXCEEDED",
                "Feature quota exceeded",
                409,
                {
                    "feature_code": code,
                    "requested_value": str(amount),
                    "remaining_value": (
                        None if estimate.remaining_before is None else str(estimate.remaining_before)
                    ),
                },
            )

        row = BillingUsageReservation(
            usage_id=usage.id,
            user_id=user_id,
            feature_code_snapshot=code,
            amount=amount,
            status=UsageReservationStatus.RESERVED.value,
            idempotency_key=key,
            expires_at=now + timedelta(seconds=expires_in_seconds),
            context=context,
        )
        usage.reserved_value += amount
        usage.version += 1
        self.repo.add(row)
        try:
            self.repo.flush()
            self.repo.commit()
        except IntegrityError:
            self.repo.rollback()
            concurrent = self.repo.reservation_by_key(key, lock=False)
            if concurrent is None:
                raise
            return self._replay(concurrent, user_id, code, amount)
        return self._reservation_output(row)

    def finalize(self, user_id: int, reservation_id: int) -> QuotaReservationOut:
        row, usage = self._reservation_and_usage(user_id, reservation_id)
        if row.status == UsageReservationStatus.FINALIZED.value:
            return self._reservation_output(row)
        if row.status != UsageReservationStatus.RESERVED.value:
            raise AppException(
                "BILLING_QUOTA_RESERVATION_TERMINAL",
                "Released or expired reservation cannot be finalized",
                409,
            )
        now = _utcnow()
        if row.expires_at <= now:
            self._release_row(usage, row, now, "reservation_expired", expired=True)
            self.repo.commit()
            raise AppException(
                "BILLING_QUOTA_RESERVATION_EXPIRED",
                "Reservation has expired",
                409,
            )
        usage.reserved_value = max(Decimal("0"), usage.reserved_value - row.amount)
        usage.used_value += row.amount
        usage.version += 1
        row.status = UsageReservationStatus.FINALIZED.value
        row.finalized_at = now
        self.repo.commit()
        return self._reservation_output(row)

    def release(
        self, user_id: int, reservation_id: int, reason: str = "operation_released"
    ) -> QuotaReservationOut:
        row, usage = self._reservation_and_usage(user_id, reservation_id)
        if row.status in {
            UsageReservationStatus.RELEASED.value,
            UsageReservationStatus.EXPIRED.value,
        }:
            return self._reservation_output(row)
        if row.status == UsageReservationStatus.FINALIZED.value:
            raise AppException(
                "BILLING_QUOTA_ALREADY_FINALIZED",
                "Finalized usage cannot be released",
                409,
            )
        self._release_row(usage, row, _utcnow(), reason[:500], expired=False)
        self.repo.commit()
        return self._reservation_output(row)

    def expire_due(self, limit: int = 100) -> int:
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000")
        now = _utcnow()
        rows = self.repo.due_reservations(now, limit)
        expired_count = 0
        for candidate in rows:
            usage = self._locked_usage(candidate.usage_id)
            row = self.repo.reservation_by_id(candidate.id, lock=True)
            if (
                row is not None
                and row.status == UsageReservationStatus.RESERVED.value
                and row.expires_at <= now
            ):
                self._release_row(usage, row, now, "reservation_expired", expired=True)
                expired_count += 1
        if expired_count:
            self.repo.commit()
        return expired_count

    def _usage(
        self, user_id: int, code: str, now: datetime, *, lock: bool
    ) -> BillingFeatureUsage:
        usage = self.repo.current_usage(user_id, code, now, lock=lock)
        if usage is None or not usage.entitlement.is_enabled:
            raise AppException(
                "BILLING_ENTITLEMENT_UNAVAILABLE",
                "Active metered entitlement not found",
                403,
                {"feature_code": code},
            )
        return usage

    def _reservation_and_usage(
        self, user_id: int, reservation_id: int
    ) -> tuple[BillingUsageReservation, BillingFeatureUsage]:
        candidate = self.repo.reservation_by_id(reservation_id, lock=False)
        if candidate is None or candidate.user_id != user_id:
            raise AppException(
                "BILLING_QUOTA_RESERVATION_NOT_FOUND",
                "Quota reservation not found",
                404,
            )
        usage = self._locked_usage(candidate.usage_id)
        row = self.repo.reservation_by_id(reservation_id, lock=True)
        if row is None or row.user_id != user_id or row.usage_id != usage.id:
            raise AppException(
                "BILLING_QUOTA_RESERVATION_NOT_FOUND",
                "Quota reservation not found",
                404,
            )
        return row, usage

    def _locked_usage(self, usage_id: int) -> BillingFeatureUsage:
        usage = self.repo.usage_by_id(usage_id, lock=True)
        if usage is None:
            raise AppException("BILLING_USAGE_NOT_FOUND", "Usage record not found", 404)
        return usage

    def _expire_for_usage(self, usage: BillingFeatureUsage, now: datetime) -> None:
        for row in self.repo.expired_for_usage(usage.id, now):
            self._release_row(usage, row, now, "reservation_expired", expired=True)

    @staticmethod
    def _release_row(
        usage: BillingFeatureUsage,
        row: BillingUsageReservation,
        now: datetime,
        reason: str,
        *,
        expired: bool,
    ) -> None:
        usage.reserved_value = max(Decimal("0"), usage.reserved_value - row.amount)
        usage.version += 1
        row.status = (
            UsageReservationStatus.EXPIRED.value
            if expired
            else UsageReservationStatus.RELEASED.value
        )
        row.released_at = now
        row.release_reason = reason

    @staticmethod
    def _estimate_output(usage: BillingFeatureUsage, amount: Decimal) -> QuotaEstimateOut:
        entitlement = usage.entitlement
        remaining: Decimal | None = None
        allowed = True
        if not entitlement.is_unlimited:
            limit = entitlement.limit_value or Decimal("0")
            remaining = max(Decimal("0"), limit - usage.used_value - usage.reserved_value)
            allowed = amount <= remaining
        return QuotaEstimateOut(
            feature_code=entitlement.feature_code_snapshot,
            requested_value=amount,
            used_value=usage.used_value,
            reserved_value=usage.reserved_value,
            limit_value=entitlement.limit_value,
            unlimited=entitlement.is_unlimited,
            remaining_before=remaining,
            remaining_after=None if remaining is None else max(Decimal("0"), remaining - amount),
            allowed=allowed,
        )

    @staticmethod
    def _replay(
        row: BillingUsageReservation, user_id: int, code: str, amount: Decimal
    ) -> QuotaReservationOut:
        if (
            row.user_id != user_id
            or row.feature_code_snapshot != code
            or row.amount != amount
        ):
            raise AppException(
                "BILLING_IDEMPOTENCY_CONFLICT",
                "Idempotency key was already used with a different request",
                409,
            )
        return QuotaService._reservation_output(row)

    @staticmethod
    def _reservation_output(row: BillingUsageReservation) -> QuotaReservationOut:
        return QuotaReservationOut(
            id=row.id,
            feature_code=row.feature_code_snapshot,
            amount=row.amount,
            status=row.status,
            expires_at=row.expires_at,
            finalized_at=row.finalized_at,
            released_at=row.released_at,
        )

    @staticmethod
    def _feature_code(value: str) -> str:
        code = value.strip().lower()
        if not code or len(code) > 120:
            raise AppException("BILLING_FEATURE_CODE_INVALID", "Invalid feature code", 422)
        return code

    @staticmethod
    def _idempotency_key(value: str) -> str:
        key = value.strip()
        if not 8 <= len(key) <= 180:
            raise AppException(
                "BILLING_IDEMPOTENCY_KEY_INVALID",
                "Idempotency key must be between 8 and 180 characters",
                422,
            )
        return key

    @staticmethod
    def _amount(value: Decimal) -> Decimal:
        amount = value.quantize(Decimal("0.0001"))
        if amount <= 0 or amount > Decimal("99999999999999.9999"):
            raise AppException("BILLING_QUOTA_AMOUNT_INVALID", "Invalid quota amount", 422)
        return amount


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)

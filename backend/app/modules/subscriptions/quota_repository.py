from datetime import datetime

from sqlalchemy.orm import Session, joinedload

from app.modules.subscriptions.models import (
    BillingEntitlement,
    BillingFeature,
    BillingFeatureUsage,
    BillingUsageReservation,
)


class QuotaRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def current_usage(
        self,
        user_id: int,
        feature_code: str,
        now: datetime,
        *,
        lock: bool,
    ) -> BillingFeatureUsage | None:
        query = (
            self.db.query(BillingFeatureUsage)
            .options(joinedload(BillingFeatureUsage.entitlement))
            .join(BillingFeatureUsage.entitlement)
            .join(BillingFeature, BillingFeature.id == BillingFeatureUsage.feature_id)
            .filter(
                BillingFeatureUsage.user_id == user_id,
                BillingEntitlement.feature_code_snapshot == feature_code,
                BillingEntitlement.starts_at <= now,
                BillingEntitlement.ends_at > now,
                BillingFeature.is_metered.is_(True),
                BillingFeature.status == "active",
            )
            .order_by(BillingEntitlement.id.desc())
        )
        if lock:
            query = query.with_for_update()
        return query.first()

    def reservation_by_key(
        self, idempotency_key: str, *, lock: bool
    ) -> BillingUsageReservation | None:
        query = self.db.query(BillingUsageReservation).filter(
            BillingUsageReservation.idempotency_key == idempotency_key
        )
        if lock:
            query = query.with_for_update()
        return query.first()

    def reservation_by_id(
        self, reservation_id: int, *, lock: bool
    ) -> BillingUsageReservation | None:
        query = self.db.query(BillingUsageReservation).filter(
            BillingUsageReservation.id == reservation_id
        )
        if lock:
            query = query.with_for_update()
        return query.first()

    def expired_for_usage(
        self, usage_id: int, now: datetime
    ) -> list[BillingUsageReservation]:
        return (
            self.db.query(BillingUsageReservation)
            .filter(
                BillingUsageReservation.usage_id == usage_id,
                BillingUsageReservation.status == "reserved",
                BillingUsageReservation.expires_at <= now,
            )
            .with_for_update()
            .all()
        )

    def due_reservations(
        self, now: datetime, limit: int
    ) -> list[BillingUsageReservation]:
        return (
            self.db.query(BillingUsageReservation)
            .filter(
                BillingUsageReservation.status == "reserved",
                BillingUsageReservation.expires_at <= now,
            )
            .order_by(BillingUsageReservation.expires_at, BillingUsageReservation.id)
            .limit(limit)
            .all()
        )

    def usage_by_id(self, usage_id: int, *, lock: bool) -> BillingFeatureUsage | None:
        query = self.db.query(BillingFeatureUsage).filter(BillingFeatureUsage.id == usage_id)
        if lock:
            query = query.with_for_update()
        return query.first()

    def add(self, row: BillingUsageReservation) -> None:
        self.db.add(row)

    def flush(self) -> None:
        self.db.flush()

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

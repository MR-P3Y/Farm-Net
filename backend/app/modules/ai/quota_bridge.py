import hashlib
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.modules.subscriptions.models import BillingEntitlement, BillingFeature
from app.modules.subscriptions.quota_service import QuotaService


METERED_AI_FEATURES = {
    "ai.text_chat",
    "ai.farm_context",
    "ai.deep_analysis",
    "ai.image_analysis",
}


class AIQuotaBridge:
    """AI-to-Billing boundary; Billing remains the commercial source of truth."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def authorize(
        self, *, user_id: int, feature_code: str, request_idempotency_key: str
    ) -> tuple[int | None, str]:
        entitlement = self._entitlement(user_id=user_id, feature_code=feature_code)
        if not entitlement.is_enabled:
            raise AppException(
                "AI_ENTITLEMENT_UNAVAILABLE",
                "AI feature is not enabled for the current subscription",
                403,
                {"feature_code": feature_code},
            )
        priority = self.processing_priority(user_id=user_id)
        reservation_id = None
        if feature_code in METERED_AI_FEATURES:
            key = "ai:" + hashlib.sha256(request_idempotency_key.encode()).hexdigest()
            reservation = QuotaService(self.db).reserve(
                user_id,
                feature_code,
                Decimal("1"),
                key,
                expires_in_seconds=3600,
                context={"consumer": "barzegar", "request_key_sha256": key[3:]},
            )
            reservation_id = reservation.id
        return reservation_id, priority

    def finalize(self, *, user_id: int, reservation_id: int | None) -> None:
        if reservation_id is not None:
            QuotaService(self.db).finalize(user_id, reservation_id)
        else:
            self.db.commit()

    def release(
        self, *, user_id: int, reservation_id: int | None, reason: str
    ) -> None:
        if reservation_id is not None:
            QuotaService(self.db).release(user_id, reservation_id, reason)
        else:
            self.db.commit()

    def processing_priority(self, *, user_id: int) -> str:
        entitlement = self._entitlement(
            user_id=user_id, feature_code="ai.processing_priority"
        )
        value = entitlement.policy_value or {}
        return "priority" if entitlement.is_enabled and value.get("value") == "priority" else "standard"

    def _entitlement(self, *, user_id: int, feature_code: str) -> BillingEntitlement:
        now = datetime.now(UTC).replace(tzinfo=None)
        row = (
            self.db.query(BillingEntitlement)
            .join(BillingFeature, BillingFeature.id == BillingEntitlement.feature_id)
            .filter(
                BillingEntitlement.user_id == user_id,
                BillingEntitlement.feature_code_snapshot == feature_code,
                BillingEntitlement.starts_at <= now,
                BillingEntitlement.ends_at > now,
                BillingFeature.status == "active",
            )
            .order_by(BillingEntitlement.id.desc())
            .first()
        )
        if row is None:
            raise AppException(
                "AI_ENTITLEMENT_UNAVAILABLE",
                "Active AI entitlement was not found",
                403,
                {"feature_code": feature_code},
            )
        return row

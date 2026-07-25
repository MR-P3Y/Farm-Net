from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.modules.subscriptions.models import BillingAuditLog, BillingSubscription


class BillingAuditService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def record(
        self,
        *,
        event_key: str,
        action: str,
        target_type: str,
        target_id: int,
        actor_type: str,
        actor_user_id: int | None,
        subscription_id: int | None = None,
        plan_id: int | None = None,
        reason: str | None = None,
        old_value: dict[str, Any] | list[Any] | None = None,
        new_value: dict[str, Any] | list[Any] | None = None,
        trace_id: str | None = None,
    ) -> BillingAuditLog:
        key = event_key.strip()
        existing = (
            self.db.query(BillingAuditLog)
            .filter(BillingAuditLog.event_key == key)
            .one_or_none()
        )
        if existing is not None:
            if (
                existing.action != action
                or existing.target_type != target_type
                or existing.target_id != target_id
            ):
                raise AppException(
                    "BILLING_AUDIT_IDEMPOTENCY_CONFLICT",
                    "Audit event key was reused for another event",
                    409,
                )
            return existing
        if actor_type != "system" and actor_user_id is None:
            raise AppException(
                "BILLING_AUDIT_ACTOR_REQUIRED",
                "A user actor is required for non-system audit events",
                422,
            )
        row = BillingAuditLog(
            event_key=key,
            action=action,
            target_type=target_type,
            target_id=target_id,
            subscription_id=subscription_id,
            plan_id=plan_id,
            actor_type=actor_type,
            actor_user_id=actor_user_id,
            reason=reason.strip() if reason else None,
            old_value=old_value,
            new_value=new_value,
            trace_id=trace_id,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def list(
        self,
        *,
        action: str | None,
        target_type: str | None,
        target_id: int | None,
        actor_user_id: int | None,
        page: int,
        page_size: int,
    ) -> tuple[list[BillingAuditLog], int]:
        query = self.db.query(BillingAuditLog)
        if action:
            query = query.filter(BillingAuditLog.action == action)
        if target_type:
            query = query.filter(BillingAuditLog.target_type == target_type)
        if target_id:
            query = query.filter(BillingAuditLog.target_id == target_id)
        if actor_user_id:
            query = query.filter(BillingAuditLog.actor_user_id == actor_user_id)
        total = query.count()
        rows = (
            query.order_by(BillingAuditLog.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return rows, total


def subscription_snapshot(row: BillingSubscription) -> dict:
    return {
        "id": row.id,
        "user_id": row.user_id,
        "plan_id": row.plan_id,
        "status": row.status,
        "current_period_starts_at": (
            row.current_period_starts_at.isoformat()
            if row.current_period_starts_at
            else None
        ),
        "current_period_ends_at": (
            row.current_period_ends_at.isoformat()
            if row.current_period_ends_at
            else None
        ),
        "grace_ends_at": row.grace_ends_at.isoformat() if row.grace_ends_at else None,
        "auto_renew": row.auto_renew,
        "cancel_at_period_end": row.cancel_at_period_end,
        "activation_source": row.activation_source,
        "version": row.version,
    }

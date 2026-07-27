from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.ai.models import AIRequest, AIUsageRecord
from app.modules.subscriptions.models import BillingUsageReservation


@dataclass(frozen=True)
class AIReconciliationIssue:
    code: str
    request_id: int
    reservation_id: int | None


@dataclass(frozen=True)
class AIReconciliationReport:
    checked_requests: int
    issues: tuple[AIReconciliationIssue, ...]


class AIUsageReconciliationService:
    """Read-only commercial/technical usage consistency audit."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def audit(self, *, limit: int = 1000) -> AIReconciliationReport:
        if not 1 <= limit <= 10_000:
            raise ValueError("limit must be between 1 and 10000")
        requests = list(
            self.db.scalars(select(AIRequest).order_by(AIRequest.id.desc()).limit(limit))
        )
        issues: list[AIReconciliationIssue] = []
        for request in requests:
            reservation = (
                self.db.get(BillingUsageReservation, request.billing_reservation_id)
                if request.billing_reservation_id is not None
                else None
            )
            technical_usage = self.db.scalar(
                select(AIUsageRecord).where(AIUsageRecord.request_id == request.id)
            )
            issue_code = self._issue_code(
                request=request,
                reservation=reservation,
                technical_usage=technical_usage,
            )
            if issue_code is not None:
                issues.append(
                    AIReconciliationIssue(
                        code=issue_code,
                        request_id=request.id,
                        reservation_id=request.billing_reservation_id,
                    )
                )
        return AIReconciliationReport(
            checked_requests=len(requests),
            issues=tuple(issues),
        )

    @staticmethod
    def _issue_code(
        *,
        request: AIRequest,
        reservation: BillingUsageReservation | None,
        technical_usage: AIUsageRecord | None,
    ) -> str | None:
        if request.billing_reservation_id is not None and reservation is None:
            return "AI_BILLING_RESERVATION_MISSING"
        if reservation is not None:
            if reservation.user_id != request.user_id:
                return "AI_BILLING_OWNER_MISMATCH"
            if reservation.feature_code_snapshot != request.feature_code:
                return "AI_BILLING_FEATURE_MISMATCH"
            if request.status == "succeeded" and reservation.status != "finalized":
                return "AI_BILLING_SUCCESS_NOT_FINALIZED"
            if (
                request.status in {"failed", "blocked", "cancelled"}
                and reservation.status not in {"released", "expired"}
            ):
                return "AI_BILLING_TERMINAL_NOT_RELEASED"
            if request.status in {"queued", "running"} and reservation.status != "reserved":
                return "AI_BILLING_ACTIVE_NOT_RESERVED"
        if request.status == "succeeded" and technical_usage is None:
            return "AI_TECHNICAL_USAGE_MISSING"
        if request.status != "succeeded" and technical_usage is not None:
            return "AI_TECHNICAL_USAGE_ON_UNUSABLE_RESULT"
        return None

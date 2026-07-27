import hashlib
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.modules.ai.admin_schemas import (
    AIAdminKnowledgeSourceCreateIn,
    AIAdminKnowledgeReviewIn,
    AIAdminOverviewOut,
)
from app.modules.ai.models import (
    AIAuditLog,
    AIFeedback,
    AIKnowledgeSource,
    AIModelConfiguration,
    AIPromptPolicyVersion,
    AIRequest,
    AIUsageRecord,
)
from app.modules.ai.reconciliation import AIUsageReconciliationService
from app.modules.auth.models import AuthUser


class AIAdminService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def overview(self) -> AIAdminOverviewOut:
        status_counts = dict(
            self.db.execute(
                select(AIRequest.status, func.count(AIRequest.id)).group_by(AIRequest.status)
            ).all()
        )
        usage = self.db.execute(
            select(
                func.coalesce(func.sum(AIUsageRecord.input_tokens), 0),
                func.coalesce(func.sum(AIUsageRecord.output_tokens), 0),
                func.coalesce(func.sum(AIUsageRecord.provider_cost_amount), 0),
            )
        ).one()
        return AIAdminOverviewOut(
            total_requests=sum(status_counts.values()),
            queued_requests=status_counts.get("queued", 0),
            running_requests=status_counts.get("running", 0),
            succeeded_requests=status_counts.get("succeeded", 0),
            failed_requests=status_counts.get("failed", 0),
            blocked_requests=status_counts.get("blocked", 0),
            total_input_tokens=int(usage[0]),
            total_output_tokens=int(usage[1]),
            total_provider_cost_toman=Decimal(usage[2]),
            pending_knowledge_sources=self.db.scalar(
                select(func.count(AIKnowledgeSource.id)).where(
                    AIKnowledgeSource.status.in_(("draft", "in_review"))
                )
            )
            or 0,
            negative_feedback=self.db.scalar(
                select(func.count(AIFeedback.id)).where(AIFeedback.rating == "not_helpful")
            )
            or 0,
            reconciliation_issues=len(AIUsageReconciliationService(self.db).audit().issues),
        )

    def requests(
        self, *, status: str | None, request_kind: str | None, page: int, page_size: int
    ) -> tuple[list[AIRequest], int]:
        query = select(AIRequest)
        count = select(func.count(AIRequest.id))
        if status:
            query = query.where(AIRequest.status == status)
            count = count.where(AIRequest.status == status)
        if request_kind:
            query = query.where(AIRequest.request_kind == request_kind)
            count = count.where(AIRequest.request_kind == request_kind)
        rows = list(
            self.db.scalars(
                query.order_by(AIRequest.requested_at.desc(), AIRequest.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        return rows, self.db.scalar(count) or 0

    def usage(self, *, page: int, page_size: int) -> tuple[list[AIUsageRecord], int]:
        rows = list(
            self.db.scalars(
                select(AIUsageRecord)
                .order_by(AIUsageRecord.recorded_at.desc(), AIUsageRecord.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        total = self.db.scalar(select(func.count(AIUsageRecord.id))) or 0
        return rows, total

    def feedback(self, *, page: int, page_size: int) -> tuple[list[AIFeedback], int]:
        rows = list(
            self.db.scalars(
                select(AIFeedback)
                .order_by(AIFeedback.created_at.desc(), AIFeedback.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        total = self.db.scalar(select(func.count(AIFeedback.id))) or 0
        return rows, total

    def knowledge_sources(self) -> list[AIKnowledgeSource]:
        return list(
            self.db.scalars(
                select(AIKnowledgeSource).order_by(
                    AIKnowledgeSource.updated_at.desc(), AIKnowledgeSource.id.desc()
                )
            )
        )

    def create_source(
        self, *, actor: AuthUser, payload: AIAdminKnowledgeSourceCreateIn
    ) -> AIKnowledgeSource:
        if self.db.scalar(
            select(AIKnowledgeSource).where(AIKnowledgeSource.code == payload.code)
        ):
            raise AppException("AI_KNOWLEDGE_CODE_EXISTS", "Knowledge code already exists", 409)
        row = AIKnowledgeSource(
            **payload.model_dump(),
            status="draft",
            created_by_user_id=actor.id,
        )
        self.db.add(row)
        self.db.flush()
        self._audit(actor=actor, action="knowledge_source.created", target=row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def submit_source(self, *, actor: AuthUser, source_id: int) -> AIKnowledgeSource:
        row = self._source(source_id, lock=True)
        if row.status != "draft":
            raise AppException(
                "AI_KNOWLEDGE_STATE_CONFLICT", "Only draft sources can be submitted", 409
            )
        row.status = "in_review"
        self._audit(actor=actor, action="knowledge_source.submitted", target=row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def review_source(
        self, *, actor: AuthUser, source_id: int, payload: AIAdminKnowledgeReviewIn
    ) -> AIKnowledgeSource:
        row = self._source(source_id, lock=True)
        if row.status != "in_review":
            raise AppException(
                "AI_KNOWLEDGE_STATE_CONFLICT", "Only in-review sources can be reviewed", 409
            )
        row.status = payload.decision
        row.reviewed_by_user_id = actor.id
        row.review_reason = payload.reason.strip()
        row.reviewed_at = datetime.utcnow()
        self._audit(
            actor=actor,
            action=f"knowledge_source.{payload.decision}",
            target=row,
            metadata={"reason": row.review_reason},
        )
        self.db.commit()
        self.db.refresh(row)
        return row

    def audits(self, *, page: int, page_size: int) -> tuple[list[AIAuditLog], int]:
        rows = list(
            self.db.scalars(
                select(AIAuditLog)
                .order_by(AIAuditLog.created_at.desc(), AIAuditLog.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        return rows, self.db.scalar(select(func.count(AIAuditLog.id))) or 0

    def policies(self) -> list[AIPromptPolicyVersion]:
        return list(
            self.db.scalars(
                select(AIPromptPolicyVersion).order_by(
                    AIPromptPolicyVersion.request_kind, AIPromptPolicyVersion.created_at.desc()
                )
            )
        )

    def models(self) -> list[AIModelConfiguration]:
        return list(
            self.db.scalars(
                select(AIModelConfiguration).order_by(
                    AIModelConfiguration.provider_key, AIModelConfiguration.model_key
                )
            )
        )

    def _source(self, source_id: int, *, lock: bool) -> AIKnowledgeSource:
        query = select(AIKnowledgeSource).where(AIKnowledgeSource.id == source_id)
        if lock:
            query = query.with_for_update()
        row = self.db.scalar(query)
        if row is None:
            raise AppException("AI_KNOWLEDGE_SOURCE_NOT_FOUND", "Knowledge source not found", 404)
        return row

    def _audit(
        self,
        *,
        actor: AuthUser,
        action: str,
        target: AIKnowledgeSource,
        metadata: dict | None = None,
    ) -> None:
        stamp = datetime.utcnow().isoformat()
        self.db.add(
            AIAuditLog(
                event_key=hashlib.sha256(
                    f"{action}:{target.id}:{actor.id}:{stamp}".encode()
                ).hexdigest(),
                action=action,
                target_type="knowledge_source",
                target_id=target.id,
                actor_type="admin",
                actor_user_id=actor.id,
                safe_metadata=metadata,
            )
        )

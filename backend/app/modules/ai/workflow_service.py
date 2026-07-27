import hashlib
import json
from datetime import datetime, timedelta

from sqlalchemy import case, or_, select
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.modules.ai.models import (
    AIConversation,
    AIExecutionAttempt,
    AIMessage,
    AIRequest,
)
from app.modules.ai.schemas import AIRequestCreateIn
from app.modules.auth.models import AuthUser


class AIWorkflowService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_conversation(self, *, user: AuthUser, title: str | None) -> AIConversation:
        now = datetime.utcnow()
        row = AIConversation(
            owner_user_id=user.id,
            title=title.strip() if title else None,
            status="active",
            retention_until=now + timedelta(days=90),
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def list_conversations(
        self, *, user: AuthUser, page: int, page_size: int
    ) -> tuple[list[AIConversation], int]:
        query = self.db.query(AIConversation).filter(
            AIConversation.owner_user_id == user.id,
            AIConversation.status.in_(("active", "archived")),
        )
        total = query.count()
        rows = (
            query.order_by(AIConversation.updated_at.desc(), AIConversation.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return rows, total

    def get_conversation(self, *, user: AuthUser, conversation_id: int) -> AIConversation:
        row = self.db.scalar(
            select(AIConversation).where(
                AIConversation.id == conversation_id,
                AIConversation.owner_user_id == user.id,
                AIConversation.status != "deleted",
            )
        )
        if row is None:
            raise AppException("AI_CONVERSATION_NOT_FOUND", "Conversation not found", 404)
        return row

    def submit_request(
        self,
        *,
        user: AuthUser,
        conversation_id: int,
        payload: AIRequestCreateIn,
    ) -> AIRequest:
        conversation = self.get_conversation(user=user, conversation_id=conversation_id)
        if conversation.status != "active":
            raise AppException("AI_CONVERSATION_NOT_ACTIVE", "Conversation is not active", 409)
        content = payload.content.strip()
        fingerprint = self._fingerprint(
            conversation_id=conversation_id,
            feature_code=payload.feature_code,
            request_kind=payload.request_kind,
            content=content,
        )
        existing = self.db.scalar(
            select(AIRequest).where(
                AIRequest.user_id == user.id,
                AIRequest.idempotency_key == payload.idempotency_key,
            )
        )
        if existing is not None:
            if existing.request_fingerprint != fingerprint:
                raise AppException(
                    "AI_IDEMPOTENCY_CONFLICT",
                    "Idempotency key was used with a different request",
                    409,
                )
            return existing

        now = datetime.utcnow()
        row = AIRequest(
            conversation_id=conversation_id,
            user_id=user.id,
            idempotency_key=payload.idempotency_key,
            request_fingerprint=fingerprint,
            feature_code=payload.feature_code,
            request_kind=payload.request_kind,
            status="queued",
            processing_priority="standard",
            prompt_policy_version="barzegar-v1",
            next_attempt_at=now,
            attempt_count=0,
            max_attempts=3,
        )
        self.db.add(row)
        self.db.flush()
        self.db.add(
            AIMessage(
                conversation_id=conversation_id,
                request_id=row.id,
                role="user",
                request_message_kind="input",
                content=content,
                content_sha256=hashlib.sha256(content.encode()).hexdigest(),
            )
        )
        conversation.updated_at = now
        self.db.commit()
        self.db.refresh(row)
        return row

    def get_request(self, *, user: AuthUser, request_id: int) -> AIRequest:
        row = self.db.scalar(
            select(AIRequest).where(AIRequest.id == request_id, AIRequest.user_id == user.id)
        )
        if row is None:
            raise AppException("AI_REQUEST_NOT_FOUND", "AI request not found", 404)
        return row

    def cancel_request(self, *, user: AuthUser, request_id: int) -> AIRequest:
        row = self.db.scalar(
            select(AIRequest)
            .where(AIRequest.id == request_id, AIRequest.user_id == user.id)
            .with_for_update()
        )
        if row is None:
            raise AppException("AI_REQUEST_NOT_FOUND", "AI request not found", 404)
        if row.status != "queued":
            raise AppException(
                "AI_REQUEST_NOT_CANCELLABLE",
                "Only queued requests can be cancelled",
                409,
            )
        row.status = "cancelled"
        row.completed_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(row)
        return row

    @staticmethod
    def _fingerprint(
        *,
        conversation_id: int,
        feature_code: str,
        request_kind: str,
        content: str,
    ) -> str:
        canonical = json.dumps(
            {
                "conversation_id": conversation_id,
                "feature_code": feature_code,
                "request_kind": request_kind,
                "content": content,
                "prompt_policy_version": "barzegar-v1",
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode()).hexdigest()


class AIWorkerService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def claim(
        self,
        *,
        worker_id: str,
        provider_key: str,
        model_key: str,
        lease_seconds: int = 300,
    ) -> tuple[AIRequest, AIExecutionAttempt] | None:
        now = datetime.utcnow()
        exhausted = self.db.scalar(
            select(AIRequest)
            .where(
                AIRequest.status == "running",
                AIRequest.lease_expires_at < now,
                AIRequest.attempt_count >= AIRequest.max_attempts,
            )
            .order_by(AIRequest.lease_expires_at, AIRequest.id)
            .with_for_update(skip_locked=True)
        )
        if exhausted is not None:
            stale_attempt = self.db.scalar(
                select(AIExecutionAttempt)
                .where(
                    AIExecutionAttempt.request_id == exhausted.id,
                    AIExecutionAttempt.status == "running",
                )
                .order_by(AIExecutionAttempt.attempt_no.desc())
                .with_for_update()
            )
            if stale_attempt is not None:
                stale_attempt.status = "timed_out"
                stale_attempt.failure_code = "WORKER_LEASE_EXPIRED"
                stale_attempt.completed_at = now
            exhausted.status = "failed"
            exhausted.failure_code = "AI_MAX_ATTEMPTS_EXHAUSTED"
            exhausted.completed_at = now
            exhausted.locked_by = None
            exhausted.lease_expires_at = None

        row = self.db.scalar(
            select(AIRequest)
            .where(
                or_(
                    ((AIRequest.status == "queued") & (AIRequest.next_attempt_at <= now)),
                    ((AIRequest.status == "running") & (AIRequest.lease_expires_at < now)),
                ),
                AIRequest.attempt_count < AIRequest.max_attempts,
            )
            .order_by(
                case((AIRequest.processing_priority == "priority", 0), else_=1),
                AIRequest.next_attempt_at,
                AIRequest.id,
            )
            .with_for_update(skip_locked=True)
        )
        if row is None:
            if exhausted is not None:
                self.db.commit()
            return None

        if row.status == "running":
            stale_attempt = self.db.scalar(
                select(AIExecutionAttempt)
                .where(
                    AIExecutionAttempt.request_id == row.id,
                    AIExecutionAttempt.status == "running",
                )
                .order_by(AIExecutionAttempt.attempt_no.desc())
                .with_for_update()
            )
            if stale_attempt is not None:
                stale_attempt.status = "timed_out"
                stale_attempt.failure_code = "WORKER_LEASE_EXPIRED"
                stale_attempt.completed_at = now

        row.attempt_count += 1
        row.status = "running"
        row.started_at = row.started_at or now
        row.locked_by = worker_id
        row.lease_expires_at = now + timedelta(seconds=max(30, lease_seconds))
        attempt = AIExecutionAttempt(
            request_id=row.id,
            attempt_no=row.attempt_count,
            provider_key=provider_key,
            model_key=model_key,
            status="running",
            timeout_seconds=min(max(lease_seconds, 30), 600),
            started_at=now,
        )
        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(row)
        self.db.refresh(attempt)
        return row, attempt

    def record_success(self, *, request_id: int, attempt_id: int, content: str) -> AIRequest:
        row, attempt = self._locked_run(request_id=request_id, attempt_id=attempt_id)
        now = datetime.utcnow()
        output = content.strip()
        if not output:
            raise AppException("AI_EMPTY_OUTPUT", "AI output cannot be empty", 409)
        existing = self.db.scalar(
            select(AIMessage).where(
                AIMessage.request_id == row.id,
                AIMessage.request_message_kind == "output",
            )
        )
        if existing is None:
            self.db.add(
                AIMessage(
                    conversation_id=row.conversation_id,
                    request_id=row.id,
                    role="assistant",
                    request_message_kind="output",
                    content=output,
                    content_sha256=hashlib.sha256(output.encode()).hexdigest(),
                )
            )
        attempt.status = "succeeded"
        attempt.completed_at = now
        row.status = "succeeded"
        row.completed_at = now
        row.locked_by = None
        row.lease_expires_at = None
        self.db.commit()
        self.db.refresh(row)
        return row

    def record_failure(
        self,
        *,
        request_id: int,
        attempt_id: int,
        failure_code: str,
        retryable: bool,
    ) -> AIRequest:
        row, attempt = self._locked_run(request_id=request_id, attempt_id=attempt_id)
        now = datetime.utcnow()
        attempt.status = "failed"
        attempt.failure_code = failure_code
        attempt.completed_at = now
        row.locked_by = None
        row.lease_expires_at = None
        if retryable and row.attempt_count < row.max_attempts:
            row.status = "queued"
            row.started_at = None
            row.next_attempt_at = now + timedelta(
                seconds=min(30 * (2 ** (row.attempt_count - 1)), 900)
            )
        else:
            row.status = "failed"
            row.failure_code = failure_code
            row.completed_at = now
        self.db.commit()
        self.db.refresh(row)
        return row

    def _locked_run(
        self, *, request_id: int, attempt_id: int
    ) -> tuple[AIRequest, AIExecutionAttempt]:
        row = self.db.scalar(select(AIRequest).where(AIRequest.id == request_id).with_for_update())
        attempt = self.db.scalar(
            select(AIExecutionAttempt)
            .where(
                AIExecutionAttempt.id == attempt_id,
                AIExecutionAttempt.request_id == request_id,
            )
            .with_for_update()
        )
        if row is None or attempt is None or row.status != "running" or attempt.status != "running":
            raise AppException("AI_RUN_STATE_CONFLICT", "AI run is not in a mutable state", 409)
        return row, attempt

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
from app.modules.ai.context_service import AIContextService
from app.modules.ai.policy_registry import AIPolicyRegistry
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
        expected_feature = {
            "text": "ai.text_chat",
            "farm_context": "ai.farm_context",
            "deep_analysis": "ai.deep_analysis",
            "image_analysis": "ai.image_analysis",
            "smart_diary": "ai.smart_diary",
            "report": "ai.report_export",
        }[payload.request_kind]
        if payload.feature_code != expected_feature:
            raise AppException(
                "AI_FEATURE_KIND_MISMATCH",
                "AI feature does not match the request kind",
                422,
            )
        content = payload.content.strip()
        route = AIPolicyRegistry(self.db).resolve(
            feature_code=payload.feature_code,
            request_kind=payload.request_kind,
        )
        fingerprint = self._fingerprint(
            conversation_id=conversation_id,
            feature_code=payload.feature_code,
            request_kind=payload.request_kind,
            content=content,
            context_consent_id=payload.context_consent_id,
            prompt_policy_version=route.prompt_policy.version,
            routing_policy_version=route.route_version,
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
        context_consent = None
        context_manifest = None
        context_captured_at = None
        if payload.context_consent_id is not None:
            (
                context_consent,
                context_manifest,
                context_captured_at,
            ) = AIContextService(self.db).capture_manifest(
                user_id=user.id,
                consent_id=payload.context_consent_id,
                request_kind=payload.request_kind,
            )
        row = AIRequest(
            conversation_id=conversation_id,
            user_id=user.id,
            idempotency_key=payload.idempotency_key,
            request_fingerprint=fingerprint,
            feature_code=payload.feature_code,
            request_kind=payload.request_kind,
            status="queued",
            processing_priority="standard",
            prompt_policy_version=route.prompt_policy.version,
            routing_policy_version=route.route_version,
            next_attempt_at=now,
            attempt_count=0,
            max_attempts=3,
            context_consent_id=context_consent.id if context_consent else None,
            context_manifest=context_manifest,
            context_captured_at=context_captured_at,
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
        context_consent_id: int | None = None,
        prompt_policy_version: str = "barzegar-v1",
        routing_policy_version: str = "routing-v1",
    ) -> str:
        values = {
            "conversation_id": conversation_id,
            "feature_code": feature_code,
            "request_kind": request_kind,
            "content": content,
            "prompt_policy_version": prompt_policy_version,
            "routing_policy_version": routing_policy_version,
        }
        if context_consent_id is not None:
            values["context_consent_id"] = context_consent_id
        canonical = json.dumps(
            values,
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
        provider_key: str | None = None,
        model_key: str | None = None,
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

        if row.context_manifest is not None and not AIContextService(self.db).is_manifest_fresh(
            request_context=row.context_manifest,
            user_id=row.user_id,
        ):
            row.status = "blocked"
            row.failure_code = "AI_CONTEXT_STALE"
            row.safety_code = "CONTEXT_REFRESH_REQUIRED"
            row.completed_at = now
            row.locked_by = None
            row.lease_expires_at = None
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

        model_configuration_id = None
        if provider_key is None and model_key is None:
            route = AIPolicyRegistry(self.db).resolve_version(
                feature_code=row.feature_code,
                request_kind=row.request_kind,
                route_version=row.routing_policy_version,
                prompt_policy_version=row.prompt_policy_version,
            )
            primary_model = route.models[0]
            provider_key = primary_model.provider_key
            model_key = primary_model.model_key
            model_configuration_id = primary_model.id
        elif provider_key is None or model_key is None:
            raise AppException(
                "AI_PROVIDER_ROUTE_INCOMPLETE",
                "Provider and model must be supplied together",
                500,
            )

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
            model_configuration_id=model_configuration_id,
            routing_policy_version=row.routing_policy_version,
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

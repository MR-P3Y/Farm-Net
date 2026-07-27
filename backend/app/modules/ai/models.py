from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.modules.ai.enums import (
    AIConsentStatus,
    AIConversationStatus,
    AIDataDeletionStatus,
    AIExecutionStatus,
    AIRequestStatus,
)


class AIConversation(Base):
    __tablename__ = "ai_conversations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    owner_user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    title: Mapped[str | None] = mapped_column(String(180))
    status: Mapped[str] = mapped_column(
        String(30), default=AIConversationStatus.ACTIVE.value, nullable=False, index=True
    )
    retention_until: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    deletion_requested_at: Mapped[datetime | None] = mapped_column(DateTime)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    messages: Mapped[list["AIMessage"]] = relationship(back_populates="conversation")
    requests: Mapped[list["AIRequest"]] = relationship(back_populates="conversation")

    __table_args__ = (
        CheckConstraint(
            "status IN ('active','archived','deletion_pending','deleted')",
            name="ck_ai_conversations_status",
        ),
        CheckConstraint(
            "(status = 'deletion_pending' AND deletion_requested_at IS NOT NULL "
            "AND deleted_at IS NULL) OR "
            "(status = 'deleted' AND deletion_requested_at IS NOT NULL "
            "AND deleted_at IS NOT NULL) OR "
            "(status IN ('active','archived') AND deletion_requested_at IS NULL "
            "AND deleted_at IS NULL)",
            name="ck_ai_conversations_deletion_state",
        ),
        Index(
            "ix_ai_conversations_owner_status_updated",
            "owner_user_id",
            "status",
            "updated_at",
        ),
    )


class AIContextConsent(Base):
    __tablename__ = "ai_context_consents"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    farm_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("farms.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    plot_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("farm_plots.id", ondelete="RESTRICT"), index=True
    )
    crop_cycle_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("farm_crop_cycles.id", ondelete="RESTRICT"), index=True
    )
    purpose: Mapped[str] = mapped_column(String(80), nullable=False)
    consent_version: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=AIConsentStatus.ACTIVE.value, nullable=False, index=True
    )
    granted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime)
    revocation_reason: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "purpose IN ('answer_question','deep_analysis','image_analysis',"
            "'smart_diary','report')",
            name="ck_ai_context_consents_purpose",
        ),
        CheckConstraint(
            "status IN ('active','revoked','expired')",
            name="ck_ai_context_consents_status",
        ),
        CheckConstraint(
            "(status = 'active' AND revoked_at IS NULL) OR "
            "(status = 'revoked' AND revoked_at IS NOT NULL) OR "
            "(status = 'expired' AND revoked_at IS NULL AND expires_at IS NOT NULL)",
            name="ck_ai_context_consents_state",
        ),
        CheckConstraint(
            "expires_at IS NULL OR expires_at > granted_at",
            name="ck_ai_context_consents_expiry",
        ),
        Index("ix_ai_context_consents_user_farm_status", "user_id", "farm_id", "status"),
    )


class AIRequest(Base):
    __tablename__ = "ai_requests"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("ai_conversations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    context_consent_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("ai_context_consents.id", ondelete="RESTRICT"), index=True
    )
    idempotency_key: Mapped[str] = mapped_column(String(180), nullable=False)
    feature_code: Mapped[str] = mapped_column(String(120), nullable=False)
    request_kind: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=AIRequestStatus.QUEUED.value, nullable=False, index=True
    )
    processing_priority: Mapped[str] = mapped_column(String(20), nullable=False)
    prompt_policy_version: Mapped[str] = mapped_column(String(80), nullable=False)
    retrieval_version: Mapped[str | None] = mapped_column(String(80))
    context_manifest: Mapped[dict | None] = mapped_column(JSON)
    context_captured_at: Mapped[datetime | None] = mapped_column(DateTime)
    billing_reservation_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("billing_usage_reservations.id", ondelete="RESTRICT"),
        unique=True,
    )
    failure_code: Mapped[str | None] = mapped_column(String(100))
    safety_code: Mapped[str | None] = mapped_column(String(100))
    requested_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)

    conversation: Mapped["AIConversation"] = relationship(back_populates="requests")
    attempts: Mapped[list["AIExecutionAttempt"]] = relationship(back_populates="request")

    __table_args__ = (
        UniqueConstraint("user_id", "idempotency_key", name="uq_ai_requests_user_idempotency"),
        CheckConstraint(
            "feature_code IN ('ai.text_chat','ai.farm_context','ai.deep_analysis',"
            "'ai.image_analysis','ai.smart_diary','ai.report_export')",
            name="ck_ai_requests_feature_code",
        ),
        CheckConstraint(
            "request_kind IN ('text','farm_context','deep_analysis','image_analysis',"
            "'smart_diary','report')",
            name="ck_ai_requests_kind",
        ),
        CheckConstraint(
            "status IN ('queued','running','succeeded','failed','blocked','cancelled')",
            name="ck_ai_requests_status",
        ),
        CheckConstraint(
            "processing_priority IN ('standard','priority')",
            name="ck_ai_requests_priority",
        ),
        CheckConstraint(
            "(context_consent_id IS NULL AND context_manifest IS NULL "
            "AND context_captured_at IS NULL) OR "
            "(context_consent_id IS NOT NULL AND context_manifest IS NOT NULL "
            "AND context_captured_at IS NOT NULL)",
            name="ck_ai_requests_context_manifest",
        ),
        CheckConstraint(
            "(status = 'queued' AND started_at IS NULL AND completed_at IS NULL) OR "
            "(status = 'running' AND started_at IS NOT NULL AND completed_at IS NULL) OR "
            "(status IN ('succeeded','failed','blocked','cancelled') "
            "AND completed_at IS NOT NULL)",
            name="ck_ai_requests_lifecycle",
        ),
        Index("ix_ai_requests_user_status_requested", "user_id", "status", "requested_at"),
    )


class AIMessage(Base):
    __tablename__ = "ai_messages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("ai_conversations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    request_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("ai_requests.id", ondelete="RESTRICT"), index=True
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    safety_label: Mapped[str | None] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    redacted_at: Mapped[datetime | None] = mapped_column(DateTime)

    conversation: Mapped["AIConversation"] = relationship(back_populates="messages")

    __table_args__ = (
        CheckConstraint(
            "role IN ('user','assistant','tool')",
            name="ck_ai_messages_role",
        ),
        CheckConstraint("CHAR_LENGTH(content) > 0", name="ck_ai_messages_content_nonempty"),
        Index("ix_ai_messages_conversation_created", "conversation_id", "created_at"),
    )


class AIExecutionAttempt(Base):
    __tablename__ = "ai_execution_attempts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("ai_requests.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    attempt_no: Mapped[int] = mapped_column(Integer, nullable=False)
    provider_key: Mapped[str] = mapped_column(String(80), nullable=False)
    model_key: Mapped[str] = mapped_column(String(120), nullable=False)
    provider_request_id: Mapped[str | None] = mapped_column(String(180))
    status: Mapped[str] = mapped_column(
        String(20), default=AIExecutionStatus.PENDING.value, nullable=False, index=True
    )
    timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    failure_code: Mapped[str | None] = mapped_column(String(100))
    failure_detail_safe: Mapped[str | None] = mapped_column(String(500))
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    request: Mapped["AIRequest"] = relationship(back_populates="attempts")

    __table_args__ = (
        UniqueConstraint("request_id", "attempt_no", name="uq_ai_attempt_request_no"),
        UniqueConstraint(
            "provider_key",
            "provider_request_id",
            name="uq_ai_attempt_provider_request",
        ),
        CheckConstraint("attempt_no > 0", name="ck_ai_attempt_no_positive"),
        CheckConstraint("timeout_seconds BETWEEN 1 AND 600", name="ck_ai_attempt_timeout"),
        CheckConstraint(
            "status IN ('pending','running','succeeded','failed','timed_out','cancelled')",
            name="ck_ai_attempt_status",
        ),
        CheckConstraint(
            "(status = 'pending' AND started_at IS NULL AND completed_at IS NULL) OR "
            "(status = 'running' AND started_at IS NOT NULL AND completed_at IS NULL) OR "
            "(status IN ('succeeded','failed','timed_out','cancelled') "
            "AND completed_at IS NOT NULL)",
            name="ck_ai_attempt_lifecycle",
        ),
    )


class AIUsageRecord(Base):
    __tablename__ = "ai_usage_records"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("ai_requests.id", ondelete="RESTRICT"), nullable=False, unique=True
    )
    attempt_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("ai_execution_attempts.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    provider_key: Mapped[str] = mapped_column(String(80), nullable=False)
    model_key: Mapped[str] = mapped_column(String(120), nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cached_input_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    provider_cost_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    provider_cost_currency: Mapped[str | None] = mapped_column(String(3))
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    __table_args__ = (
        CheckConstraint(
            "input_tokens >= 0 AND output_tokens >= 0 AND cached_input_tokens >= 0",
            name="ck_ai_usage_tokens_nonnegative",
        ),
        CheckConstraint("latency_ms >= 0", name="ck_ai_usage_latency_nonnegative"),
        CheckConstraint(
            "(provider_cost_amount IS NULL AND provider_cost_currency IS NULL) OR "
            "(provider_cost_amount >= 0 AND CHAR_LENGTH(provider_cost_currency) = 3)",
            name="ck_ai_usage_cost_pair",
        ),
        Index("ix_ai_usage_user_recorded", "user_id", "recorded_at"),
    )


class AIFeedback(Base):
    __tablename__ = "ai_feedback"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("ai_requests.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    rating: Mapped[str] = mapped_column(String(20), nullable=False)
    reason_codes: Mapped[list | None] = mapped_column(JSON)
    comment: Mapped[str | None] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        UniqueConstraint("request_id", "user_id", name="uq_ai_feedback_request_user"),
        CheckConstraint(
            "rating IN ('helpful','not_helpful')",
            name="ck_ai_feedback_rating",
        ),
    )


class AIDataDeletionRequest(Base):
    __tablename__ = "ai_data_deletion_requests"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    conversation_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("ai_conversations.id", ondelete="RESTRICT"), index=True
    )
    idempotency_key: Mapped[str] = mapped_column(String(180), nullable=False)
    scope: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=AIDataDeletionStatus.REQUESTED.value, nullable=False, index=True
    )
    requested_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    process_after: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    failure_code: Mapped[str | None] = mapped_column(String(100))

    __table_args__ = (
        UniqueConstraint(
            "user_id", "idempotency_key", name="uq_ai_deletion_user_idempotency"
        ),
        CheckConstraint(
            "scope IN ('conversation','all_conversations')",
            name="ck_ai_deletion_scope",
        ),
        CheckConstraint(
            "(scope = 'conversation' AND conversation_id IS NOT NULL) OR "
            "(scope = 'all_conversations' AND conversation_id IS NULL)",
            name="ck_ai_deletion_scope_target",
        ),
        CheckConstraint(
            "status IN ('requested','processing','completed','failed')",
            name="ck_ai_deletion_status",
        ),
        CheckConstraint(
            "(status IN ('requested','processing') AND completed_at IS NULL) OR "
            "(status IN ('completed','failed') AND completed_at IS NOT NULL)",
            name="ck_ai_deletion_lifecycle",
        ),
        CheckConstraint(
            "process_after >= requested_at",
            name="ck_ai_deletion_process_after",
        ),
        Index("ix_ai_deletion_status_process", "status", "process_after"),
    )


class AIAuditLog(Base):
    __tablename__ = "ai_audit_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    event_key: Mapped[str] = mapped_column(String(180), nullable=False, unique=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(40), nullable=False)
    target_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    actor_type: Mapped[str] = mapped_column(String(20), nullable=False)
    actor_user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="RESTRICT"), index=True
    )
    request_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("ai_requests.id", ondelete="RESTRICT"), index=True
    )
    safe_metadata: Mapped[dict | None] = mapped_column(JSON)
    trace_id: Mapped[str | None] = mapped_column(String(100), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    __table_args__ = (
        CheckConstraint(
            "actor_type IN ('user','admin','system','worker')",
            name="ck_ai_audit_actor_type",
        ),
        CheckConstraint(
            "(actor_type IN ('user','admin') AND actor_user_id IS NOT NULL) OR "
            "(actor_type IN ('system','worker') AND actor_user_id IS NULL)",
            name="ck_ai_audit_actor",
        ),
        Index("ix_ai_audit_target_created", "target_type", "target_id", "created_at"),
    )

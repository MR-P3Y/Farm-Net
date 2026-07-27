from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
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
        UniqueConstraint("user_id", "idempotency_key", name="uq_ai_deletion_user_idempotency"),
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


class AIKnowledgeSource(Base):
    __tablename__ = "ai_knowledge_sources"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    publisher: Mapped[str] = mapped_column(String(250), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(1000))
    license_code: Mapped[str] = mapped_column(String(80), nullable=False)
    license_evidence: Mapped[str] = mapped_column(String(1000), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft", index=True)
    created_by_user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="RESTRICT"), nullable=False
    )
    reviewed_by_user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="RESTRICT")
    )
    review_reason: Mapped[str | None] = mapped_column(String(1000))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft','in_review','approved','rejected','withdrawn')",
            name="ck_ai_knowledge_sources_status",
        ),
        CheckConstraint(
            "(status IN ('draft','in_review') AND reviewed_at IS NULL) OR "
            "(status IN ('approved','rejected','withdrawn') AND reviewed_at IS NOT NULL "
            "AND reviewed_by_user_id IS NOT NULL)",
            name="ck_ai_knowledge_sources_review_state",
        ),
    )


class AIKnowledgeSourceVersion(Base):
    __tablename__ = "ai_knowledge_source_versions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("ai_knowledge_sources.id", ondelete="RESTRICT"), nullable=False
    )
    version_no: Mapped[int] = mapped_column(Integer, nullable=False)
    edition: Mapped[str | None] = mapped_column(String(120))
    published_at: Mapped[datetime | None] = mapped_column(DateTime)
    effective_from: Mapped[datetime | None] = mapped_column(DateTime)
    effective_until: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft", index=True)
    approved_by_user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("auth_users.id", ondelete="RESTRICT")
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime)
    withdrawal_reason: Mapped[str | None] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    __table_args__ = (
        UniqueConstraint("source_id", "version_no", name="uq_ai_source_version_no"),
        CheckConstraint("version_no > 0", name="ck_ai_source_version_positive"),
        CheckConstraint(
            "status IN ('draft','in_review','approved','rejected','withdrawn')",
            name="ck_ai_source_versions_status",
        ),
        CheckConstraint(
            "effective_until IS NULL OR effective_from IS NOT NULL "
            "AND effective_until > effective_from",
            name="ck_ai_source_versions_effective_range",
        ),
        CheckConstraint(
            "(status = 'approved' AND approved_by_user_id IS NOT NULL "
            "AND approved_at IS NOT NULL) OR status <> 'approved'",
            name="ck_ai_source_versions_approval",
        ),
    )


class AIKnowledgeDocument(Base):
    __tablename__ = "ai_knowledge_documents"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    source_version_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("ai_knowledge_source_versions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(1000), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    byte_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    page_count: Mapped[int | None] = mapped_column(Integer)
    is_encrypted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    extraction_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    __table_args__ = (
        CheckConstraint("byte_size > 0", name="ck_ai_documents_byte_size"),
        CheckConstraint("page_count IS NULL OR page_count > 0", name="ck_ai_documents_page_count"),
        CheckConstraint("mime_type = 'application/pdf'", name="ck_ai_documents_pdf_only"),
        CheckConstraint(
            "extraction_status IN ('pending','running','succeeded','needs_review','failed')",
            name="ck_ai_documents_extraction_status",
        ),
    )


class AIKnowledgeIngestionJob(Base):
    __tablename__ = "ai_knowledge_ingestion_jobs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("ai_knowledge_documents.id", ondelete="RESTRICT"), nullable=False
    )
    idempotency_key: Mapped[str] = mapped_column(String(180), nullable=False, unique=True)
    extractor_version: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    pages_processed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    extracted_characters: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    quality_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    failure_code: Mapped[str | None] = mapped_column(String(100))
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','running','succeeded','needs_review','failed')",
            name="ck_ai_ingestion_jobs_status",
        ),
        CheckConstraint(
            "pages_processed >= 0 AND extracted_characters >= 0",
            name="ck_ai_ingestion_jobs_counts",
        ),
        CheckConstraint(
            "quality_score IS NULL OR quality_score BETWEEN 0 AND 1",
            name="ck_ai_ingestion_jobs_quality",
        ),
        CheckConstraint(
            "(status = 'pending' AND started_at IS NULL AND completed_at IS NULL) OR "
            "(status = 'running' AND started_at IS NOT NULL AND completed_at IS NULL) OR "
            "(status IN ('succeeded','needs_review','failed') "
            "AND started_at IS NOT NULL AND completed_at IS NOT NULL)",
            name="ck_ai_ingestion_jobs_lifecycle",
        ),
        CheckConstraint(
            "(status = 'failed' AND failure_code IS NOT NULL) OR "
            "(status <> 'failed' AND failure_code IS NULL)",
            name="ck_ai_ingestion_jobs_failure",
        ),
    )


class AIKnowledgeExtractedPage(Base):
    __tablename__ = "ai_knowledge_extracted_pages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    ingestion_job_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("ai_knowledge_ingestion_jobs.id", ondelete="RESTRICT"),
        nullable=False,
    )
    document_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("ai_knowledge_documents.id", ondelete="RESTRICT"), nullable=False
    )
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    extracted_text: Mapped[str] = mapped_column(Text, nullable=False)
    text_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    character_count: Mapped[int] = mapped_column(Integer, nullable=False)
    quality_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    needs_review: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    __table_args__ = (
        UniqueConstraint("ingestion_job_id", "page_number", name="uq_ai_extracted_page_job_number"),
        CheckConstraint("page_number > 0", name="ck_ai_extracted_pages_number"),
        CheckConstraint(
            "character_count = CHAR_LENGTH(extracted_text)",
            name="ck_ai_extracted_pages_character_count",
        ),
        CheckConstraint("quality_score BETWEEN 0 AND 1", name="ck_ai_extracted_pages_quality"),
    )


class AIKnowledgeChunk(Base):
    __tablename__ = "ai_knowledge_chunks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    source_version_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("ai_knowledge_source_versions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    document_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("ai_knowledge_documents.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    extracted_page_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("ai_knowledge_extracted_pages.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    character_start: Mapped[int] = mapped_column(Integer, nullable=False)
    character_end: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    text_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    chunker_version: Mapped[str] = mapped_column(String(80), nullable=False)
    token_estimate: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "extracted_page_id",
            "chunker_version",
            "chunk_index",
            name="uq_ai_chunk_page_version_index",
        ),
        CheckConstraint("page_number > 0", name="ck_ai_chunks_page_number"),
        CheckConstraint("chunk_index >= 0", name="ck_ai_chunks_index"),
        CheckConstraint(
            "character_start >= 0 AND character_end > character_start",
            name="ck_ai_chunks_character_range",
        ),
        CheckConstraint(
            "CHAR_LENGTH(chunk_text) = character_end - character_start",
            name="ck_ai_chunks_character_count",
        ),
        CheckConstraint("token_estimate > 0", name="ck_ai_chunks_token_estimate"),
        Index("ix_ai_chunks_document_page_active", "document_id", "page_number", "is_active"),
    )


class AIEmbeddingModel(Base):
    __tablename__ = "ai_embedding_models"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    model_key: Mapped[str] = mapped_column(String(120), nullable=False)
    model_version: Mapped[str] = mapped_column(String(80), nullable=False)
    dimensions: Mapped[int] = mapped_column(Integer, nullable=False)
    distance_metric: Mapped[str] = mapped_column(String(20), nullable=False)
    normalization: Mapped[str] = mapped_column(String(30), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    active_scope: Mapped[str | None] = mapped_column(String(30), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("model_key", "model_version", name="uq_ai_embedding_model_version"),
        CheckConstraint("dimensions BETWEEN 8 AND 65536", name="ck_ai_embedding_dimensions"),
        CheckConstraint(
            "distance_metric IN ('cosine','dot','euclidean')",
            name="ck_ai_embedding_distance",
        ),
        CheckConstraint("normalization IN ('none','l2')", name="ck_ai_embedding_normalization"),
        CheckConstraint(
            "(is_active = 1 AND active_scope = 'global') OR "
            "(is_active = 0 AND active_scope IS NULL)",
            name="ck_ai_embedding_active_scope",
        ),
    )


class AIEmbeddingIndexRecord(Base):
    __tablename__ = "ai_embedding_index_records"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    chunk_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("ai_knowledge_chunks.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    embedding_model_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("ai_embedding_models.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    store_key: Mapped[str] = mapped_column(String(80), nullable=False)
    collection_name: Mapped[str] = mapped_column(String(160), nullable=False)
    point_id: Mapped[str] = mapped_column(String(180), nullable=False)
    vector_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    indexed_at: Mapped[datetime | None] = mapped_column(DateTime)
    removed_at: Mapped[datetime | None] = mapped_column(DateTime)
    failure_code: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("chunk_id", "embedding_model_id", name="uq_ai_embedding_chunk_model"),
        UniqueConstraint(
            "store_key",
            "collection_name",
            "point_id",
            name="uq_ai_embedding_store_point",
        ),
        CheckConstraint(
            "status IN ('pending','indexed','failed','removed')",
            name="ck_ai_embedding_index_status",
        ),
        CheckConstraint(
            "(status = 'pending' AND indexed_at IS NULL AND removed_at IS NULL "
            "AND failure_code IS NULL) OR "
            "(status = 'indexed' AND indexed_at IS NOT NULL AND removed_at IS NULL "
            "AND failure_code IS NULL) OR "
            "(status = 'failed' AND failure_code IS NOT NULL) OR "
            "(status = 'removed' AND indexed_at IS NOT NULL AND removed_at IS NOT NULL)",
            name="ck_ai_embedding_index_lifecycle",
        ),
    )


class AIResponseCitation(Base):
    __tablename__ = "ai_response_citations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    message_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("ai_messages.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    chunk_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("ai_knowledge_chunks.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    citation_order: Mapped[int] = mapped_column(Integer, nullable=False)
    quoted_text: Mapped[str] = mapped_column(Text, nullable=False)
    quoted_text_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    source_title_snapshot: Mapped[str] = mapped_column(String(250), nullable=False)
    source_version_snapshot: Mapped[str] = mapped_column(String(120), nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    retrieval_score: Mapped[Decimal | None] = mapped_column(Numeric(8, 7))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("message_id", "citation_order", name="uq_ai_citation_message_order"),
        UniqueConstraint("message_id", "chunk_id", name="uq_ai_citation_message_chunk"),
        CheckConstraint("citation_order > 0", name="ck_ai_citation_order"),
        CheckConstraint("page_number > 0", name="ck_ai_citation_page"),
        CheckConstraint("CHAR_LENGTH(quoted_text) > 0", name="ck_ai_citation_quote_nonempty"),
        CheckConstraint(
            "retrieval_score IS NULL OR retrieval_score BETWEEN 0 AND 1",
            name="ck_ai_citation_score",
        ),
    )

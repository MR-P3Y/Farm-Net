"""add Barzegar AI core contracts

Revision ID: a21c4b82a6e0
Revises: e17c4b82a6d9
Create Date: 2026-07-27 12:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "a21c4b82a6e0"
down_revision: str | Sequence[str] | None = "e17c4b82a6d9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamps() -> tuple[sa.Column, sa.Column]:
    return (
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )


def upgrade() -> None:
    created_at, updated_at = _timestamps()
    op.create_table(
        "ai_conversations",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("owner_user_id", sa.BigInteger(), nullable=False),
        sa.Column("title", sa.String(180), nullable=True),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("retention_until", sa.DateTime(), nullable=False),
        sa.Column("deletion_requested_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        created_at,
        updated_at,
        sa.CheckConstraint(
            "status IN ('active','archived','deletion_pending','deleted')",
            name="ck_ai_conversations_status",
        ),
        sa.CheckConstraint(
            "(status = 'deletion_pending' AND deletion_requested_at IS NOT NULL "
            "AND deleted_at IS NULL) OR "
            "(status = 'deleted' AND deletion_requested_at IS NOT NULL "
            "AND deleted_at IS NOT NULL) OR "
            "(status IN ('active','archived') AND deletion_requested_at IS NULL "
            "AND deleted_at IS NULL)",
            name="ck_ai_conversations_deletion_state",
        ),
        sa.ForeignKeyConstraint(["owner_user_id"], ["auth_users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_conversations_owner_user_id", "ai_conversations", ["owner_user_id"])
    op.create_index("ix_ai_conversations_status", "ai_conversations", ["status"])
    op.create_index("ix_ai_conversations_retention_until", "ai_conversations", ["retention_until"])
    op.create_index(
        "ix_ai_conversations_owner_status_updated",
        "ai_conversations",
        ["owner_user_id", "status", "updated_at"],
    )

    op.create_table(
        "ai_context_consents",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("farm_id", sa.BigInteger(), nullable=False),
        sa.Column("plot_id", sa.BigInteger(), nullable=True),
        sa.Column("crop_cycle_id", sa.BigInteger(), nullable=True),
        sa.Column("purpose", sa.String(80), nullable=False),
        sa.Column("consent_version", sa.String(40), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("granted_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("revocation_reason", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "purpose IN ('answer_question','deep_analysis','image_analysis','smart_diary','report')",
            name="ck_ai_context_consents_purpose",
        ),
        sa.CheckConstraint(
            "status IN ('active','revoked','expired')",
            name="ck_ai_context_consents_status",
        ),
        sa.CheckConstraint(
            "(status = 'active' AND revoked_at IS NULL) OR "
            "(status = 'revoked' AND revoked_at IS NOT NULL) OR "
            "(status = 'expired' AND revoked_at IS NULL AND expires_at IS NOT NULL)",
            name="ck_ai_context_consents_state",
        ),
        sa.CheckConstraint(
            "expires_at IS NULL OR expires_at > granted_at",
            name="ck_ai_context_consents_expiry",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["auth_users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["farm_id"], ["farms.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["plot_id"], ["farm_plots.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["crop_cycle_id"], ["farm_crop_cycles.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("user_id", "farm_id", "plot_id", "crop_cycle_id", "status"):
        op.create_index(f"ix_ai_context_consents_{column}", "ai_context_consents", [column])
    op.create_index(
        "ix_ai_context_consents_user_farm_status",
        "ai_context_consents",
        ["user_id", "farm_id", "status"],
    )

    op.create_table(
        "ai_requests",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("conversation_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("context_consent_id", sa.BigInteger(), nullable=True),
        sa.Column("idempotency_key", sa.String(180), nullable=False),
        sa.Column("feature_code", sa.String(120), nullable=False),
        sa.Column("request_kind", sa.String(30), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("processing_priority", sa.String(20), nullable=False),
        sa.Column("prompt_policy_version", sa.String(80), nullable=False),
        sa.Column("retrieval_version", sa.String(80), nullable=True),
        sa.Column("context_manifest", sa.JSON(), nullable=True),
        sa.Column("context_captured_at", sa.DateTime(), nullable=True),
        sa.Column("billing_reservation_id", sa.BigInteger(), nullable=True),
        sa.Column("failure_code", sa.String(100), nullable=True),
        sa.Column("safety_code", sa.String(100), nullable=True),
        sa.Column("requested_at", sa.DateTime(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint(
            "feature_code IN ('ai.text_chat','ai.farm_context','ai.deep_analysis',"
            "'ai.image_analysis','ai.smart_diary','ai.report_export')",
            name="ck_ai_requests_feature_code",
        ),
        sa.CheckConstraint(
            "request_kind IN ('text','farm_context','deep_analysis','image_analysis',"
            "'smart_diary','report')",
            name="ck_ai_requests_kind",
        ),
        sa.CheckConstraint(
            "status IN ('queued','running','succeeded','failed','blocked','cancelled')",
            name="ck_ai_requests_status",
        ),
        sa.CheckConstraint(
            "processing_priority IN ('standard','priority')",
            name="ck_ai_requests_priority",
        ),
        sa.CheckConstraint(
            "(context_consent_id IS NULL AND context_manifest IS NULL "
            "AND context_captured_at IS NULL) OR "
            "(context_consent_id IS NOT NULL AND context_manifest IS NOT NULL "
            "AND context_captured_at IS NOT NULL)",
            name="ck_ai_requests_context_manifest",
        ),
        sa.CheckConstraint(
            "(status = 'queued' AND started_at IS NULL AND completed_at IS NULL) OR "
            "(status = 'running' AND started_at IS NOT NULL AND completed_at IS NULL) OR "
            "(status IN ('succeeded','failed','blocked','cancelled') "
            "AND completed_at IS NOT NULL)",
            name="ck_ai_requests_lifecycle",
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"], ["ai_conversations.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["auth_users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["context_consent_id"], ["ai_context_consents.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["billing_reservation_id"],
            ["billing_usage_reservations.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "idempotency_key", name="uq_ai_requests_user_idempotency"
        ),
        sa.UniqueConstraint("billing_reservation_id"),
    )
    for column in ("conversation_id", "user_id", "context_consent_id", "status"):
        op.create_index(f"ix_ai_requests_{column}", "ai_requests", [column])
    op.create_index(
        "ix_ai_requests_user_status_requested",
        "ai_requests",
        ["user_id", "status", "requested_at"],
    )

    op.create_table(
        "ai_messages",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("conversation_id", sa.BigInteger(), nullable=False),
        sa.Column("request_id", sa.BigInteger(), nullable=True),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_sha256", sa.String(64), nullable=False),
        sa.Column("safety_label", sa.String(80), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("redacted_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint("role IN ('user','assistant','tool')", name="ck_ai_messages_role"),
        sa.CheckConstraint("CHAR_LENGTH(content) > 0", name="ck_ai_messages_content_nonempty"),
        sa.ForeignKeyConstraint(
            ["conversation_id"], ["ai_conversations.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(["request_id"], ["ai_requests.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_messages_conversation_id", "ai_messages", ["conversation_id"])
    op.create_index("ix_ai_messages_request_id", "ai_messages", ["request_id"])
    op.create_index(
        "ix_ai_messages_conversation_created",
        "ai_messages",
        ["conversation_id", "created_at"],
    )

    op.create_table(
        "ai_execution_attempts",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("request_id", sa.BigInteger(), nullable=False),
        sa.Column("attempt_no", sa.Integer(), nullable=False),
        sa.Column("provider_key", sa.String(80), nullable=False),
        sa.Column("model_key", sa.String(120), nullable=False),
        sa.Column("provider_request_id", sa.String(180), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("timeout_seconds", sa.Integer(), nullable=False),
        sa.Column("failure_code", sa.String(100), nullable=True),
        sa.Column("failure_detail_safe", sa.String(500), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("attempt_no > 0", name="ck_ai_attempt_no_positive"),
        sa.CheckConstraint(
            "timeout_seconds BETWEEN 1 AND 600", name="ck_ai_attempt_timeout"
        ),
        sa.CheckConstraint(
            "status IN ('pending','running','succeeded','failed','timed_out','cancelled')",
            name="ck_ai_attempt_status",
        ),
        sa.CheckConstraint(
            "(status = 'pending' AND started_at IS NULL AND completed_at IS NULL) OR "
            "(status = 'running' AND started_at IS NOT NULL AND completed_at IS NULL) OR "
            "(status IN ('succeeded','failed','timed_out','cancelled') "
            "AND completed_at IS NOT NULL)",
            name="ck_ai_attempt_lifecycle",
        ),
        sa.ForeignKeyConstraint(["request_id"], ["ai_requests.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("request_id", "attempt_no", name="uq_ai_attempt_request_no"),
        sa.UniqueConstraint(
            "provider_key", "provider_request_id", name="uq_ai_attempt_provider_request"
        ),
    )
    op.create_index("ix_ai_execution_attempts_request_id", "ai_execution_attempts", ["request_id"])
    op.create_index("ix_ai_execution_attempts_status", "ai_execution_attempts", ["status"])

    op.create_table(
        "ai_usage_records",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("request_id", sa.BigInteger(), nullable=False),
        sa.Column("attempt_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("provider_key", sa.String(80), nullable=False),
        sa.Column("model_key", sa.String(120), nullable=False),
        sa.Column("input_tokens", sa.Integer(), nullable=False),
        sa.Column("output_tokens", sa.Integer(), nullable=False),
        sa.Column("cached_input_tokens", sa.Integer(), nullable=False),
        sa.Column("provider_cost_amount", sa.Numeric(18, 8), nullable=True),
        sa.Column("provider_cost_currency", sa.String(3), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "input_tokens >= 0 AND output_tokens >= 0 AND cached_input_tokens >= 0",
            name="ck_ai_usage_tokens_nonnegative",
        ),
        sa.CheckConstraint("latency_ms >= 0", name="ck_ai_usage_latency_nonnegative"),
        sa.CheckConstraint(
            "(provider_cost_amount IS NULL AND provider_cost_currency IS NULL) OR "
            "(provider_cost_amount >= 0 AND CHAR_LENGTH(provider_cost_currency) = 3)",
            name="ck_ai_usage_cost_pair",
        ),
        sa.ForeignKeyConstraint(["request_id"], ["ai_requests.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["attempt_id"], ["ai_execution_attempts.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["auth_users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("request_id"),
        sa.UniqueConstraint("attempt_id"),
    )
    op.create_index("ix_ai_usage_records_user_id", "ai_usage_records", ["user_id"])
    op.create_index("ix_ai_usage_records_recorded_at", "ai_usage_records", ["recorded_at"])
    op.create_index(
        "ix_ai_usage_user_recorded", "ai_usage_records", ["user_id", "recorded_at"]
    )

    op.create_table(
        "ai_feedback",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("request_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("rating", sa.String(20), nullable=False),
        sa.Column("reason_codes", sa.JSON(), nullable=True),
        sa.Column("comment", sa.String(1000), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "rating IN ('helpful','not_helpful')", name="ck_ai_feedback_rating"
        ),
        sa.ForeignKeyConstraint(["request_id"], ["ai_requests.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["auth_users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("request_id", "user_id", name="uq_ai_feedback_request_user"),
    )
    op.create_index("ix_ai_feedback_request_id", "ai_feedback", ["request_id"])
    op.create_index("ix_ai_feedback_user_id", "ai_feedback", ["user_id"])

    op.create_table(
        "ai_data_deletion_requests",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("conversation_id", sa.BigInteger(), nullable=True),
        sa.Column("idempotency_key", sa.String(180), nullable=False),
        sa.Column("scope", sa.String(30), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("requested_at", sa.DateTime(), nullable=False),
        sa.Column("process_after", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("failure_code", sa.String(100), nullable=True),
        sa.CheckConstraint(
            "scope IN ('conversation','all_conversations')", name="ck_ai_deletion_scope"
        ),
        sa.CheckConstraint(
            "(scope = 'conversation' AND conversation_id IS NOT NULL) OR "
            "(scope = 'all_conversations' AND conversation_id IS NULL)",
            name="ck_ai_deletion_scope_target",
        ),
        sa.CheckConstraint(
            "status IN ('requested','processing','completed','failed')",
            name="ck_ai_deletion_status",
        ),
        sa.CheckConstraint(
            "(status IN ('requested','processing') AND completed_at IS NULL) OR "
            "(status IN ('completed','failed') AND completed_at IS NOT NULL)",
            name="ck_ai_deletion_lifecycle",
        ),
        sa.CheckConstraint(
            "process_after >= requested_at", name="ck_ai_deletion_process_after"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["auth_users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["conversation_id"], ["ai_conversations.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "idempotency_key", name="uq_ai_deletion_user_idempotency"
        ),
    )
    op.create_index(
        "ix_ai_data_deletion_requests_user_id", "ai_data_deletion_requests", ["user_id"]
    )
    op.create_index(
        "ix_ai_data_deletion_requests_conversation_id",
        "ai_data_deletion_requests",
        ["conversation_id"],
    )
    op.create_index(
        "ix_ai_data_deletion_requests_status",
        "ai_data_deletion_requests",
        ["status"],
    )
    op.create_index(
        "ix_ai_data_deletion_requests_process_after",
        "ai_data_deletion_requests",
        ["process_after"],
    )
    op.create_index(
        "ix_ai_deletion_status_process",
        "ai_data_deletion_requests",
        ["status", "process_after"],
    )

    op.create_table(
        "ai_audit_logs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("event_key", sa.String(180), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("target_type", sa.String(40), nullable=False),
        sa.Column("target_id", sa.BigInteger(), nullable=False),
        sa.Column("actor_type", sa.String(20), nullable=False),
        sa.Column("actor_user_id", sa.BigInteger(), nullable=True),
        sa.Column("request_id", sa.BigInteger(), nullable=True),
        sa.Column("safe_metadata", sa.JSON(), nullable=True),
        sa.Column("trace_id", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "actor_type IN ('user','admin','system','worker')",
            name="ck_ai_audit_actor_type",
        ),
        sa.CheckConstraint(
            "(actor_type IN ('user','admin') AND actor_user_id IS NOT NULL) OR "
            "(actor_type IN ('system','worker') AND actor_user_id IS NULL)",
            name="ck_ai_audit_actor",
        ),
        sa.ForeignKeyConstraint(
            ["actor_user_id"], ["auth_users.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(["request_id"], ["ai_requests.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_key"),
    )
    for column in ("action", "actor_user_id", "request_id", "trace_id", "created_at"):
        op.create_index(f"ix_ai_audit_logs_{column}", "ai_audit_logs", [column])
    op.create_index(
        "ix_ai_audit_target_created",
        "ai_audit_logs",
        ["target_type", "target_id", "created_at"],
    )


def downgrade() -> None:
    for table in (
        "ai_audit_logs",
        "ai_data_deletion_requests",
        "ai_feedback",
        "ai_usage_records",
        "ai_execution_attempts",
        "ai_messages",
        "ai_requests",
        "ai_context_consents",
        "ai_conversations",
    ):
        op.drop_table(table)

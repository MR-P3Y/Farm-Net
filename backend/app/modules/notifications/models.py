from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.modules.auth.models import AuthUser  # noqa: F401
from app.modules.notifications.enums import (
    NotificationChannel,
    NotificationDeliveryStatus,
    NotificationPriority,
    NotificationStatus,
)


class NotificationEvent(Base):
    __tablename__ = "notification_events"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    event_key: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        unique=True,
    )
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)

    actor_user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    source_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    source_id: Mapped[str | None] = mapped_column(String(80), nullable=True)

    payload_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        Index("ix_notification_events_type_created", "event_type", "created_at"),
        Index("ix_notification_events_source", "source_type", "source_id"),
    )


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    event_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("notification_events.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    recipient_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    channel: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=NotificationChannel.IN_APP.value,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    action_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    priority: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=NotificationPriority.NORMAL.value,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=NotificationStatus.UNREAD.value,
    )

    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "event_id",
            "recipient_user_id",
            "channel",
            name="uq_notifications_event_recipient_channel",
        ),
        Index(
            "ix_notifications_recipient_status_created",
            "recipient_user_id",
            "status",
            "created_at",
        ),
        Index(
            "ix_notifications_recipient_channel_created",
            "recipient_user_id",
            "channel",
            "created_at",
        ),
        Index("ix_notifications_status_created", "status", "created_at"),
    )


class NotificationDeliveryLog(Base):
    __tablename__ = "notification_delivery_logs"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    notification_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("notifications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    channel: Mapped[str] = mapped_column(String(30), nullable=False)
    provider: Mapped[str | None] = mapped_column(String(80), nullable=True)
    provider_message_id: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=NotificationDeliveryStatus.PENDING.value,
    )

    error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    next_attempt_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_attempt_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    locked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        Index(
            "ix_notification_delivery_logs_notification_channel",
            "notification_id",
            "channel",
        ),
        Index("ix_notification_delivery_logs_status_created", "status", "created_at"),
        Index(
            "ix_notification_delivery_logs_retry_ready",
            "status",
            "next_attempt_at",
        ),
        UniqueConstraint(
            "notification_id",
            "channel",
            name="uq_notification_delivery_notification_channel",
        ),
        UniqueConstraint(
            "provider",
            "provider_message_id",
            name="uq_notification_delivery_provider_message",
        ),
    )


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(
        String(80), nullable=False, default="*"
    )
    channel: Mapped[str] = mapped_column(String(30), nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "event_type",
            "channel",
            name="uq_notification_preferences_user_event_channel",
        ),
        Index(
            "ix_notification_preferences_user_event",
            "user_id",
            "event_type",
        ),
    )


class NotificationDeliveryAttempt(Base):
    __tablename__ = "notification_delivery_attempts"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    delivery_log_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("notification_delivery_logs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    provider: Mapped[str | None] = mapped_column(String(80), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (
        UniqueConstraint(
            "delivery_log_id",
            "attempt_number",
            name="uq_notification_delivery_attempt_number",
        ),
        Index(
            "ix_notification_delivery_attempts_status_started",
            "status",
            "started_at",
        ),
    )

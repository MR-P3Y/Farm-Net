from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.exceptions import ValidationAuthError
from app.modules.notifications.enums import (
    NotificationChannel,
    NotificationDeliveryStatus,
    NotificationEventType,
    NotificationPriority,
    NotificationStatus,
)
from app.modules.notifications.models import (
    Notification,
    NotificationDeliveryLog,
    NotificationEvent,
)
from app.modules.notifications.repository import NotificationRepository
from app.modules.notifications.schemas import (
    NotificationEventCreateIn,
    NotificationEventOut,
    NotificationOut,
    NotificationSystemMessageIn,
)


class NotificationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = NotificationRepository(db)

    def create_event(
        self,
        *,
        payload: NotificationEventCreateIn,
        commit: bool = True,
    ) -> NotificationEventOut:
        self._validate_event_type(payload.event_type)

        event_key = payload.event_key or self._generate_event_key(
            event_type=payload.event_type,
            source_type=payload.source_type,
            source_id=payload.source_id,
        )

        existing = self.repo.get_event_by_key(event_key=event_key)
        if existing is not None:
            return NotificationEventOut.model_validate(existing)

        row = NotificationEvent(
            event_key=event_key,
            event_type=payload.event_type,
            actor_user_id=payload.actor_user_id,
            source_type=payload.source_type,
            source_id=payload.source_id,
            payload_json=payload.payload_json,
        )

        try:
            self.repo.add_event(row)

            if commit:
                self.repo.commit()

            self.repo.refresh(row)

            return NotificationEventOut.model_validate(row)

        except IntegrityError:
            self.db.rollback()

            existing = self.repo.get_event_by_key(event_key=event_key)
            if existing is not None:
                return NotificationEventOut.model_validate(existing)

            raise

    def notify_user(
        self,
        *,
        recipient_user_id: int,
        title: str,
        body: str,
        event_id: int | None = None,
        channel: str = NotificationChannel.IN_APP.value,
        action_url: str | None = None,
        priority: str = NotificationPriority.NORMAL.value,
        commit: bool = True,
    ) -> NotificationOut:
        self._validate_channel(channel)
        self._validate_priority(priority)

        if recipient_user_id <= 0:
            raise ValidationAuthError(
                message="Invalid notification recipient",
                details={"recipient_user_id": recipient_user_id},
            )

        if not title.strip():
            raise ValidationAuthError(message="Notification title is required")

        if not body.strip():
            raise ValidationAuthError(message="Notification body is required")

        row = Notification(
            event_id=event_id,
            recipient_user_id=recipient_user_id,
            channel=channel,
            title=title.strip(),
            body=body.strip(),
            action_url=action_url,
            priority=priority,
            status=NotificationStatus.UNREAD.value,
        )

        self.repo.add_notification(row)

        self.repo.add_delivery_log(
            NotificationDeliveryLog(
                notification_id=row.id,
                channel=channel,
                provider="in_app" if channel == NotificationChannel.IN_APP.value else None,
                status=NotificationDeliveryStatus.SENT.value
                if channel == NotificationChannel.IN_APP.value
                else NotificationDeliveryStatus.PENDING.value,
                sent_at=datetime.utcnow()
                if channel == NotificationChannel.IN_APP.value
                else None,
            )
        )

        if commit:
            self.repo.commit()

        self.repo.refresh(row)

        return NotificationOut.model_validate(row)

    def notify_many(
        self,
        *,
        recipient_user_ids: list[int],
        title: str,
        body: str,
        event_id: int | None = None,
        channel: str = NotificationChannel.IN_APP.value,
        action_url: str | None = None,
        priority: str = NotificationPriority.NORMAL.value,
        commit: bool = True,
    ) -> list[NotificationOut]:
        unique_ids = sorted(set(recipient_user_ids))

        if not unique_ids:
            return []

        rows: list[NotificationOut] = []

        for user_id in unique_ids:
            rows.append(
                self.notify_user(
                    recipient_user_id=user_id,
                    title=title,
                    body=body,
                    event_id=event_id,
                    channel=channel,
                    action_url=action_url,
                    priority=priority,
                    commit=False,
                )
            )

        if commit:
            self.repo.commit()

        return rows

    def create_system_message(
        self,
        *,
        payload: NotificationSystemMessageIn,
        actor_user_id: int | None,
    ) -> NotificationOut:
        event = self.create_event(
            payload=NotificationEventCreateIn(
                event_type=NotificationEventType.SYSTEM_MESSAGE.value,
                actor_user_id=actor_user_id,
                source_type="system",
                source_id=str(payload.recipient_user_id),
                payload_json={
                    "recipient_user_id": payload.recipient_user_id,
                    "title": payload.title,
                    "priority": payload.priority,
                },
            ),
            commit=False,
        )

        result = self.notify_user(
            recipient_user_id=payload.recipient_user_id,
            title=payload.title,
            body=payload.body,
            event_id=event.id,
            channel=NotificationChannel.IN_APP.value,
            action_url=payload.action_url,
            priority=payload.priority,
            commit=False,
        )

        self.repo.commit()

        return result

    def list_user_notifications(
        self,
        *,
        recipient_user_id: int,
        status: str | None,
        channel: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[NotificationOut], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        if status is not None:
            self._validate_status(status)

        if channel is not None:
            self._validate_channel(channel)

        rows, total = self.repo.list_user_notifications(
            recipient_user_id=recipient_user_id,
            status=status,
            channel=channel,
            page=page,
            page_size=page_size,
        )

        return [NotificationOut.model_validate(row) for row in rows], total

    def unread_count(self, *, recipient_user_id: int) -> int:
        return self.repo.unread_count(recipient_user_id=recipient_user_id)

    def mark_read(
        self,
        *,
        notification_id: int,
        recipient_user_id: int,
    ) -> NotificationOut:
        row = self.repo.get_user_notification_by_id(
            notification_id=notification_id,
            recipient_user_id=recipient_user_id,
        )

        if row is None:
            raise ValidationAuthError(
                message="Notification not found",
                details={"notification_id": notification_id},
            )

        row.status = NotificationStatus.READ.value
        row.read_at = datetime.utcnow()

        self.repo.commit()
        self.repo.refresh(row)

        return NotificationOut.model_validate(row)

    def mark_all_read(self, *, recipient_user_id: int) -> int:
        rows = self.repo.list_unread_user_notifications(
            recipient_user_id=recipient_user_id,
        )

        now = datetime.utcnow()

        for row in rows:
            row.status = NotificationStatus.READ.value
            row.read_at = now

        self.repo.commit()

        return len(rows)

    def soft_delete(
        self,
        *,
        notification_id: int,
        recipient_user_id: int,
    ) -> NotificationOut:
        row = self.repo.get_user_notification_by_id(
            notification_id=notification_id,
            recipient_user_id=recipient_user_id,
        )

        if row is None:
            raise ValidationAuthError(
                message="Notification not found",
                details={"notification_id": notification_id},
            )

        row.status = NotificationStatus.DELETED.value
        row.deleted_at = datetime.utcnow()

        self.repo.commit()
        self.repo.refresh(row)

        return NotificationOut.model_validate(row)

    def list_admin_notifications(
        self,
        *,
        status: str | None,
        channel: str | None,
        recipient_user_id: int | None,
        page: int,
        page_size: int,
    ) -> tuple[list[NotificationOut], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        if status is not None:
            self._validate_status(status)

        if channel is not None:
            self._validate_channel(channel)

        rows, total = self.repo.list_admin_notifications(
            status=status,
            channel=channel,
            recipient_user_id=recipient_user_id,
            page=page,
            page_size=page_size,
        )

        return [NotificationOut.model_validate(row) for row in rows], total

    def get_admin_notification(
        self,
        *,
        notification_id: int,
    ) -> NotificationOut:
        row = self.repo.get_admin_notification_by_id(
            notification_id=notification_id,
        )

        if row is None:
            raise ValidationAuthError(
                message="Notification not found",
                details={"notification_id": notification_id},
            )

        return NotificationOut.model_validate(row)

    def _generate_event_key(
        self,
        *,
        event_type: str,
        source_type: str | None,
        source_id: str | None,
    ) -> str:
        unique_suffix = uuid4().hex
        clean_event_type = event_type.replace(".", "_")

        if source_type and source_id:
            base = f"{clean_event_type}:{source_type}:{source_id}"
        else:
            base = clean_event_type

        max_base_length = 80 - len(unique_suffix) - 1
        return f"{base[:max_base_length]}:{unique_suffix}"

    def _validate_event_type(self, event_type: str) -> None:
        allowed = {item.value for item in NotificationEventType}

        if event_type not in allowed:
            raise ValidationAuthError(
                message="Invalid notification event type",
                details={"allowed": sorted(allowed)},
            )

    def _validate_channel(self, channel: str) -> None:
        allowed = {item.value for item in NotificationChannel}

        if channel not in allowed:
            raise ValidationAuthError(
                message="Invalid notification channel",
                details={"allowed": sorted(allowed)},
            )

    def _validate_status(self, status: str) -> None:
        allowed = {item.value for item in NotificationStatus}

        if status not in allowed:
            raise ValidationAuthError(
                message="Invalid notification status",
                details={"allowed": sorted(allowed)},
            )

    def _validate_priority(self, priority: str) -> None:
        allowed = {item.value for item in NotificationPriority}

        if priority not in allowed:
            raise ValidationAuthError(
                message="Invalid notification priority",
                details={"allowed": sorted(allowed)},
            )

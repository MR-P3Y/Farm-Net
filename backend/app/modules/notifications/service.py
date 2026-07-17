from __future__ import annotations

from datetime import datetime
from hashlib import sha256
import json
from typing import Any
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
    NotificationPreference,
)
from app.modules.notifications.repository import NotificationRepository
from app.modules.notifications.schemas import (
    NotificationEventCreateIn,
    NotificationEventOut,
    NotificationOut,
    NotificationPreferenceIn,
    NotificationPreferenceOut,
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
            payload_json=payload.payload_json,
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
            with self.db.begin_nested():
                self.repo.add_event(row)

            if commit:
                self.repo.commit()

            self.repo.refresh(row)

            return NotificationEventOut.model_validate(row)

        except IntegrityError:
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

        if event_id is not None:
            existing = self.repo.get_notification_for_event(
                event_id=event_id,
                recipient_user_id=recipient_user_id,
                channel=channel,
            )
            if existing is not None:
                return NotificationOut.model_validate(existing)

        try:
            with self.db.begin_nested():
                self.repo.add_notification(row)
                self.repo.add_delivery_log(
                    NotificationDeliveryLog(
                        notification_id=row.id,
                        channel=channel,
                        provider="in_app"
                        if channel == NotificationChannel.IN_APP.value
                        else None,
                        status=NotificationDeliveryStatus.SENT.value
                        if channel == NotificationChannel.IN_APP.value
                        else NotificationDeliveryStatus.PENDING.value,
                        sent_at=datetime.utcnow()
                        if channel == NotificationChannel.IN_APP.value
                        else None,
                    )
                )
        except IntegrityError:
            if event_id is not None:
                existing = self.repo.get_notification_for_event(
                    event_id=event_id,
                    recipient_user_id=recipient_user_id,
                    channel=channel,
                )
                if existing is not None:
                    return NotificationOut.model_validate(existing)
            raise

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

    def create_event_and_notify_user(
        self,
        *,
        event_type: str,
        recipient_user_id: int,
        title: str,
        body: str,
        actor_user_id: int | None = None,
        source_type: str | None = None,
        source_id: str | None = None,
        payload_json: dict[str, Any] | None = None,
        action_url: str | None = None,
        priority: str = NotificationPriority.NORMAL.value,
        event_key: str | None = None,
        allow_self_notification: bool = False,
        commit: bool = True,
    ) -> NotificationOut | None:
        if actor_user_id == recipient_user_id and not allow_self_notification:
            return None
        event = self.create_event(
            payload=NotificationEventCreateIn(
                event_key=event_key,
                event_type=event_type,
                actor_user_id=actor_user_id,
                source_type=source_type,
                source_id=source_id,
                payload_json=payload_json,
            ),
            commit=False,
        )

        notifications = self._notify_routed_channels(
            event_id=event.id,
            event_type=event_type,
            recipient_user_id=recipient_user_id,
            title=title,
            body=body,
            action_url=action_url,
            priority=priority,
        )

        if commit:
            self.repo.commit()

        return notifications[0] if notifications else None

    def create_event_and_notify_many(
        self,
        *,
        event_type: str,
        recipient_user_ids: list[int],
        title: str,
        body: str,
        actor_user_id: int | None = None,
        source_type: str | None = None,
        source_id: str | None = None,
        payload_json: dict[str, Any] | None = None,
        action_url: str | None = None,
        priority: str = NotificationPriority.NORMAL.value,
        event_key: str | None = None,
        allow_self_notification: bool = False,
        commit: bool = True,
    ) -> list[NotificationOut]:
        recipients = {
            recipient_user_id
            for recipient_user_id in recipient_user_ids
            if allow_self_notification or recipient_user_id != actor_user_id
        }
        if not recipients:
            return []

        event = self.create_event(
            payload=NotificationEventCreateIn(
                event_key=event_key,
                event_type=event_type,
                actor_user_id=actor_user_id,
                source_type=source_type,
                source_id=source_id,
                payload_json=payload_json,
            ),
            commit=False,
        )

        notifications: list[NotificationOut] = []
        for recipient_user_id in sorted(recipients):
            notifications.extend(
                self._notify_routed_channels(
                    event_id=event.id,
                    event_type=event_type,
                    recipient_user_id=recipient_user_id,
                    title=title,
                    body=body,
                    action_url=action_url,
                    priority=priority,
                )
            )

        if commit:
            self.repo.commit()

        return notifications

    def list_preferences(self, *, user_id: int) -> list[NotificationPreferenceOut]:
        return [
            NotificationPreferenceOut.model_validate(row)
            for row in self.repo.list_preferences(user_id=user_id)
        ]

    def set_preference(
        self, *, user_id: int, payload: NotificationPreferenceIn
    ) -> NotificationPreferenceOut:
        self._validate_channel(payload.channel)
        if payload.event_type != "*":
            self._validate_event_type(payload.event_type)

        row = self.repo.get_preference(
            user_id=user_id,
            event_type=payload.event_type,
            channel=payload.channel,
        )
        if row is None:
            row = self.repo.add_preference(
                NotificationPreference(
                    user_id=user_id,
                    event_type=payload.event_type,
                    channel=payload.channel,
                    is_enabled=payload.is_enabled,
                )
            )
        else:
            row.is_enabled = payload.is_enabled

        self.repo.commit()
        self.repo.refresh(row)
        return NotificationPreferenceOut.model_validate(row)

    def resolve_channels(self, *, user_id: int, event_type: str) -> list[str]:
        self._validate_event_type(event_type)
        recipient = self.repo.get_recipient(user_id=user_id)
        if recipient is None:
            return []

        preferences = self.repo.list_routing_preferences(
            user_id=user_id, event_type=event_type
        )
        global_preferences = {
            row.channel: row.is_enabled for row in preferences if row.event_type == "*"
        }
        event_preferences = {
            row.channel: row.is_enabled
            for row in preferences
            if row.event_type == event_type
        }

        routed: list[str] = []
        for channel in NotificationChannel:
            enabled = event_preferences.get(
                channel.value,
                global_preferences.get(
                    channel.value,
                    channel == NotificationChannel.IN_APP,
                ),
            )
            if enabled and self._has_routable_destination(recipient, channel):
                routed.append(channel.value)
        return routed

    def _notify_routed_channels(
        self,
        *,
        event_id: int,
        event_type: str,
        recipient_user_id: int,
        title: str,
        body: str,
        action_url: str | None,
        priority: str,
    ) -> list[NotificationOut]:
        notifications: list[NotificationOut] = []
        for channel in self.resolve_channels(
            user_id=recipient_user_id, event_type=event_type
        ):
            existing = self.repo.get_notification_for_event(
                event_id=event_id,
                recipient_user_id=recipient_user_id,
                channel=channel,
            )
            if existing is not None:
                notifications.append(NotificationOut.model_validate(existing))
                continue
            notifications.append(
                self.notify_user(
                    recipient_user_id=recipient_user_id,
                    title=title,
                    body=body,
                    event_id=event_id,
                    channel=channel,
                    action_url=action_url,
                    priority=priority,
                    commit=False,
                )
            )

        return notifications

    def _has_routable_destination(
        self, recipient: Any, channel: NotificationChannel
    ) -> bool:
        if channel == NotificationChannel.IN_APP:
            return True
        if channel == NotificationChannel.EMAIL:
            return bool(recipient.email and recipient.is_email_verified)
        if channel == NotificationChannel.SMS:
            return bool(recipient.phone and recipient.is_phone_verified)
        # Push and Telegram require destination registries in later steps.
        return False

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
        payload_json: dict[str, Any] | None,
    ) -> str:
        clean_event_type = event_type.replace(".", "_")

        if source_type and source_id:
            base = f"{clean_event_type}:{source_type}:{source_id}"
            canonical_identity = json.dumps(
                {
                    "event_type": event_type,
                    "source_type": source_type,
                    "source_id": source_id,
                    "payload": payload_json or {},
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
                default=str,
            )
            digest = sha256(canonical_identity.encode("utf-8")).hexdigest()[:12]
            max_base_length = 80 - len(digest) - 1
            return f"{base[:max_base_length]}:{digest}"

        unique_suffix = uuid4().hex
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

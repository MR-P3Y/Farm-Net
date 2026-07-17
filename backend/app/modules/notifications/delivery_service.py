from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.modules.auth.exceptions import ValidationAuthError
from app.modules.notifications.enums import NotificationChannel, NotificationDeliveryStatus
from app.modules.notifications.models import NotificationDeliveryAttempt
from app.modules.notifications.repository import NotificationRepository
from app.modules.notifications.schemas import (
    NotificationDeliveryAttemptOut,
    NotificationDeliveryDetailOut,
    NotificationDeliveryLogOut,
)


class NotificationDeliveryService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = NotificationRepository(db)

    def claim_ready(
        self, *, limit: int = 50, lease_seconds: int = 300
    ) -> list[NotificationDeliveryLogOut]:
        now = datetime.now(UTC)
        rows = self.repo.claim_ready_deliveries(
            now=now,
            lease_cutoff=now - timedelta(seconds=max(lease_seconds, 30)),
            limit=min(max(limit, 1), 100),
        )
        claimed: list[NotificationDeliveryLogOut] = []
        for row in rows:
            if row.status == NotificationDeliveryStatus.PROCESSING.value:
                self._close_stale_attempt(row.id, row.attempt_count, now)
                if row.attempt_count >= row.max_attempts:
                    row.status = NotificationDeliveryStatus.FAILED.value
                    row.error_code = "lease_expired"
                    row.error_message = "Delivery worker lease expired"
                    row.locked_at = None
                    continue

            row.attempt_count += 1
            row.status = NotificationDeliveryStatus.PROCESSING.value
            row.last_attempt_at = now
            row.next_attempt_at = None
            row.locked_at = now
            self.repo.add_delivery_attempt(
                NotificationDeliveryAttempt(
                    delivery_log_id=row.id,
                    attempt_number=row.attempt_count,
                    provider=row.provider,
                    status=NotificationDeliveryStatus.PROCESSING.value,
                    started_at=now,
                )
            )
            claimed.append(NotificationDeliveryLogOut.model_validate(row))

        self.repo.commit()
        return claimed

    def record_success(
        self,
        *,
        delivery_log_id: int,
        provider: str,
        provider_message_id: str | None,
    ) -> NotificationDeliveryDetailOut:
        row = self._processing_delivery(delivery_log_id)
        now = datetime.now(UTC)
        row.status = NotificationDeliveryStatus.SENT.value
        row.provider = provider
        row.provider_message_id = provider_message_id
        row.sent_at = now
        row.error_code = None
        row.error_message = None
        row.next_attempt_at = None
        row.locked_at = None
        self._finish_attempt(row.id, row.attempt_count, "sent", now, provider=provider)
        self.repo.commit()
        return self.get_detail(delivery_log_id=delivery_log_id)

    def record_failure(
        self,
        *,
        delivery_log_id: int,
        error_code: str,
        error_message: str,
        base_delay_seconds: int = 60,
        max_delay_seconds: int = 3600,
    ) -> NotificationDeliveryDetailOut:
        row = self._processing_delivery(delivery_log_id)
        now = datetime.now(UTC)
        terminal = row.attempt_count >= row.max_attempts
        row.status = (
            NotificationDeliveryStatus.FAILED.value
            if terminal
            else NotificationDeliveryStatus.PENDING.value
        )
        row.error_code = error_code
        row.error_message = error_message
        row.locked_at = None
        if terminal:
            row.next_attempt_at = None
        else:
            delay = min(
                max(base_delay_seconds, 1) * (2 ** max(row.attempt_count - 1, 0)),
                max(max_delay_seconds, 1),
            )
            row.next_attempt_at = now + timedelta(seconds=delay)
        self._finish_attempt(
            row.id,
            row.attempt_count,
            "failed",
            now,
            error_code=error_code,
            error_message=error_message,
        )
        self.repo.commit()
        return self.get_detail(delivery_log_id=delivery_log_id)

    def list_deliveries(
        self,
        *,
        status: str | None,
        channel: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[NotificationDeliveryLogOut], int]:
        if status is not None:
            allowed = {item.value for item in NotificationDeliveryStatus}
            if status not in allowed:
                raise ValidationAuthError(
                    message="Invalid delivery status",
                    details={"allowed": sorted(allowed)},
                )
        if channel is not None:
            allowed_channels = {item.value for item in NotificationChannel}
            if channel not in allowed_channels:
                raise ValidationAuthError(
                    message="Invalid notification channel",
                    details={"allowed": sorted(allowed_channels)},
                )
        rows, total = self.repo.list_delivery_logs(
            status=status,
            channel=channel,
            page=max(page, 1),
            page_size=min(max(page_size, 1), 100),
        )
        return [NotificationDeliveryLogOut.model_validate(row) for row in rows], total

    def get_detail(self, *, delivery_log_id: int) -> NotificationDeliveryDetailOut:
        row = self.repo.get_delivery_log(delivery_log_id=delivery_log_id)
        if row is None:
            raise ValidationAuthError(message="Notification delivery not found")
        attempts = self.repo.list_delivery_attempts(delivery_log_id=delivery_log_id)
        data = NotificationDeliveryLogOut.model_validate(row).model_dump()
        data["attempts"] = [
            NotificationDeliveryAttemptOut.model_validate(item) for item in attempts
        ]
        return NotificationDeliveryDetailOut.model_validate(data)

    def requeue(self, *, delivery_log_id: int) -> NotificationDeliveryDetailOut:
        row = self.repo.get_delivery_log(
            delivery_log_id=delivery_log_id, for_update=True
        )
        if row is None:
            raise ValidationAuthError(message="Notification delivery not found")
        blocked = {
            NotificationDeliveryStatus.PROCESSING.value,
            NotificationDeliveryStatus.SENT.value,
            NotificationDeliveryStatus.DELIVERED.value,
        }
        if row.channel == "in_app" or row.status in blocked:
            raise ValidationAuthError(message="Notification delivery cannot be requeued")
        row.status = NotificationDeliveryStatus.PENDING.value
        row.max_attempts = max(row.max_attempts, row.attempt_count + 5)
        row.next_attempt_at = datetime.now(UTC)
        row.locked_at = None
        self.repo.commit()
        return self.get_detail(delivery_log_id=delivery_log_id)

    def _processing_delivery(self, delivery_log_id: int):
        row = self.repo.get_delivery_log(
            delivery_log_id=delivery_log_id, for_update=True
        )
        if row is None or row.status != NotificationDeliveryStatus.PROCESSING.value:
            raise ValidationAuthError(message="Delivery is not processing")
        return row

    def _close_stale_attempt(
        self, delivery_log_id: int, attempt_number: int, now: datetime
    ) -> None:
        attempt = self.repo.get_delivery_attempt(
            delivery_log_id=delivery_log_id, attempt_number=attempt_number
        )
        if attempt is not None and attempt.finished_at is None:
            attempt.status = NotificationDeliveryStatus.FAILED.value
            attempt.error_code = "lease_expired"
            attempt.error_message = "Delivery worker lease expired"
            attempt.finished_at = now

    def _finish_attempt(
        self,
        delivery_log_id: int,
        attempt_number: int,
        status: str,
        finished_at: datetime,
        *,
        provider: str | None = None,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> None:
        attempt = self.repo.get_delivery_attempt(
            delivery_log_id=delivery_log_id, attempt_number=attempt_number
        )
        if attempt is None or attempt.finished_at is not None:
            raise ValidationAuthError(message="Delivery attempt is not active")
        attempt.status = status
        attempt.provider = provider or attempt.provider
        attempt.error_code = error_code
        attempt.error_message = error_message
        attempt.finished_at = finished_at

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.modules.notifications.delivery_service import NotificationDeliveryService
from app.modules.notifications.push_provider import (
    HttpJsonPushTransport,
    PushMessage,
    PushProviderError,
    PushTransport,
)


@dataclass(frozen=True)
class PushDispatchResult:
    claimed: int = 0
    sent: int = 0
    failed: int = 0
    disabled: bool = False


class PushDeliveryDispatcher:
    def __init__(self, db: Session, *, settings: Settings | None = None, transport: PushTransport | None = None) -> None:
        self.settings = settings or get_settings()
        self.delivery = NotificationDeliveryService(db)
        self.repo = self.delivery.repo
        self.transport = transport or HttpJsonPushTransport(self.settings)

    def run_once(self, *, limit: int = 50) -> PushDispatchResult:
        if not self._is_configured():
            return PushDispatchResult(disabled=True)
        claimed = self.delivery.claim_ready(limit=limit, channel="push")
        sent = failed = 0
        for delivery in claimed:
            target = self.repo.get_delivery_target(delivery_log_id=delivery.id)
            if target is None:
                self._fail(delivery.id, "delivery_target_missing", "Delivery target missing", True)
                failed += 1
                continue
            _, notification, recipient = target
            devices = self.repo.list_active_devices(user_id=recipient.id)
            if not devices:
                self._fail(delivery.id, "push_destination_unavailable", "No active push device", True)
                failed += 1
                continue
            try:
                message_id = self.transport.send(
                    PushMessage(
                        tokens=[device.token for device in devices],
                        title=notification.title,
                        body=notification.body,
                        action_url=notification.action_url,
                    )
                )
                self.delivery.record_success(
                    delivery_log_id=delivery.id,
                    provider=self.settings.push_provider,
                    provider_message_id=message_id,
                )
                sent += 1
            except PushProviderError as exc:
                self._fail(delivery.id, exc.code, exc.message, exc.terminal)
                failed += 1
        return PushDispatchResult(claimed=len(claimed), sent=sent, failed=failed)

    def _fail(self, delivery_id: int, code: str, message: str, terminal: bool) -> None:
        self.delivery.record_failure(
            delivery_log_id=delivery_id,
            error_code=code,
            error_message=message,
            terminal=terminal,
        )

    def _is_configured(self) -> bool:
        parsed = urlparse(self.settings.push_api_url)
        return bool(
            self.settings.push_enabled
            and self.settings.push_provider == "http_json"
            and parsed.scheme == "https"
            and parsed.netloc
            and self.settings.push_api_key.strip()
        )

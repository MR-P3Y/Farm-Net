from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.modules.notifications.delivery_service import NotificationDeliveryService
from app.modules.notifications.sms_provider import (
    HttpJsonSmsTransport,
    SmsProviderError,
    SmsTransport,
    build_sms_message,
)


@dataclass(frozen=True)
class SmsDispatchResult:
    claimed: int = 0
    sent: int = 0
    failed: int = 0
    disabled: bool = False


class SmsDeliveryDispatcher:
    def __init__(
        self,
        db: Session,
        *,
        settings: Settings | None = None,
        transport: SmsTransport | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.delivery = NotificationDeliveryService(db)
        self.repo = self.delivery.repo
        self.transport = transport or HttpJsonSmsTransport(self.settings)

    def run_once(self, *, limit: int = 50) -> SmsDispatchResult:
        if not self._is_configured():
            return SmsDispatchResult(disabled=True)
        claimed = self.delivery.claim_ready(limit=limit, channel="sms")
        sent = 0
        failed = 0
        for delivery in claimed:
            target = self.repo.get_delivery_target(delivery_log_id=delivery.id)
            if target is None:
                self._fail(delivery.id, "delivery_target_missing", "Delivery target missing", True)
                failed += 1
                continue
            _, notification, recipient = target
            if not recipient.phone or not recipient.is_phone_verified:
                self._fail(
                    delivery.id,
                    "sms_destination_unavailable",
                    "Recipient has no verified phone number",
                    True,
                )
                failed += 1
                continue
            message = build_sms_message(
                to=recipient.phone,
                title=notification.title,
                body=notification.body,
                action_url=notification.action_url,
            )
            try:
                message_id = self.transport.send(message)
                self.delivery.record_success(
                    delivery_log_id=delivery.id,
                    provider=self.settings.sms_provider,
                    provider_message_id=message_id,
                )
                sent += 1
            except SmsProviderError as exc:
                self._fail(delivery.id, exc.code, exc.message, exc.terminal)
                failed += 1
        return SmsDispatchResult(claimed=len(claimed), sent=sent, failed=failed)

    def _fail(self, delivery_id: int, code: str, message: str, terminal: bool) -> None:
        self.delivery.record_failure(
            delivery_log_id=delivery_id,
            error_code=code,
            error_message=message,
            terminal=terminal,
        )

    def _is_configured(self) -> bool:
        parsed = urlparse(self.settings.sms_api_url)
        return bool(
            self.settings.sms_enabled
            and self.settings.sms_provider == "http_json"
            and parsed.scheme == "https"
            and parsed.netloc
            and self.settings.sms_api_key.strip()
            and self.settings.sms_sender.strip()
        )

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.modules.notifications.delivery_service import NotificationDeliveryService
from app.modules.notifications.email_provider import (
    EmailProviderError,
    EmailTransport,
    SmtpEmailTransport,
    build_email_envelope,
)


@dataclass(frozen=True)
class EmailDispatchResult:
    claimed: int = 0
    sent: int = 0
    failed: int = 0
    disabled: bool = False


class EmailDeliveryDispatcher:
    def __init__(
        self,
        db: Session,
        *,
        settings: Settings | None = None,
        transport: EmailTransport | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.delivery = NotificationDeliveryService(db)
        self.repo = self.delivery.repo
        self.transport = transport or SmtpEmailTransport(self.settings)

    def run_once(self, *, limit: int = 50) -> EmailDispatchResult:
        if not self._is_configured():
            return EmailDispatchResult(disabled=True)

        claimed = self.delivery.claim_ready(limit=limit, channel="email")
        sent = 0
        failed = 0
        for delivery in claimed:
            target = self.repo.get_delivery_target(delivery_log_id=delivery.id)
            if target is None:
                self.delivery.record_failure(
                    delivery_log_id=delivery.id,
                    error_code="delivery_target_missing",
                    error_message="Notification delivery target no longer exists",
                    terminal=True,
                )
                failed += 1
                continue
            _, notification, recipient = target
            if not recipient.email or not recipient.is_email_verified:
                self.delivery.record_failure(
                    delivery_log_id=delivery.id,
                    error_code="email_destination_unavailable",
                    error_message="Recipient has no verified email address",
                    terminal=True,
                )
                failed += 1
                continue
            envelope = build_email_envelope(
                to=recipient.email,
                title=notification.title,
                body=notification.body,
                action_url=notification.action_url,
            )
            try:
                message_id = self.transport.send(envelope)
                self.delivery.record_success(
                    delivery_log_id=delivery.id,
                    provider="smtp",
                    provider_message_id=message_id,
                )
                sent += 1
            except EmailProviderError as exc:
                self.delivery.record_failure(
                    delivery_log_id=delivery.id,
                    error_code=exc.code,
                    error_message=exc.message,
                    terminal=exc.terminal,
                )
                failed += 1
        return EmailDispatchResult(claimed=len(claimed), sent=sent, failed=failed)

    def _is_configured(self) -> bool:
        return bool(
            self.settings.email_enabled
            and self.settings.email_provider == "smtp"
            and self.settings.email_host.strip()
            and self.settings.email_from.strip()
            and not (
                self.settings.email_starttls and self.settings.email_use_ssl
            )
        )

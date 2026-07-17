from __future__ import annotations

from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import make_msgid
from html import escape
import smtplib
import ssl
from typing import Protocol
from urllib.parse import urlparse

from app.core.config import Settings


class EmailProviderError(Exception):
    def __init__(self, code: str, message: str, *, terminal: bool = False) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.terminal = terminal


@dataclass(frozen=True)
class EmailEnvelope:
    to: str
    subject: str
    text_body: str
    html_body: str


class EmailTransport(Protocol):
    def send(self, envelope: EmailEnvelope) -> str: ...


class SmtpEmailTransport:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def send(self, envelope: EmailEnvelope) -> str:
        try:
            message = EmailMessage()
            message_id = make_msgid(domain=self._from_domain())
            message["Message-ID"] = message_id
            message["From"] = self.settings.email_from
            message["To"] = envelope.to
            message["Subject"] = envelope.subject.replace("\r", " ").replace("\n", " ")
            message.set_content(envelope.text_body)
            message.add_alternative(envelope.html_body, subtype="html")
            smtp_class = smtplib.SMTP_SSL if self.settings.email_use_ssl else smtplib.SMTP
            with smtp_class(
                self.settings.email_host,
                self.settings.email_port,
                timeout=self.settings.email_timeout_seconds,
            ) as client:
                if self.settings.email_starttls and not self.settings.email_use_ssl:
                    client.starttls(context=ssl.create_default_context())
                if self.settings.email_user:
                    client.login(self.settings.email_user, self.settings.email_password)
                client.send_message(message)
        except smtplib.SMTPRecipientsRefused as exc:
            raise EmailProviderError("recipient_refused", str(exc), terminal=True) from exc
        except ValueError as exc:
            raise EmailProviderError("invalid_email_message", str(exc), terminal=True) from exc
        except (smtplib.SMTPException, OSError) as exc:
            raise EmailProviderError("smtp_error", str(exc)) from exc
        return message_id.strip("<>")

    def _from_domain(self) -> str | None:
        if "@" not in self.settings.email_from:
            return None
        return self.settings.email_from.rsplit("@", 1)[1]


def build_email_envelope(*, to: str, title: str, body: str, action_url: str | None) -> EmailEnvelope:
    safe_action_url = _safe_action_url(action_url)
    action_text = f"\n\n{safe_action_url}" if safe_action_url else ""
    link = (
        f'<p><a href="{escape(safe_action_url, quote=True)}">مشاهده جزئیات</a></p>'
        if safe_action_url
        else ""
    )
    return EmailEnvelope(
        to=to,
        subject=title,
        text_body=f"{body}{action_text}",
        html_body=f"<html><body><p>{escape(body)}</p>{link}</body></html>",
    )


def _safe_action_url(action_url: str | None) -> str | None:
    if not action_url:
        return None
    parsed = urlparse(action_url)
    if action_url.startswith("/") or parsed.scheme in {"http", "https"}:
        return action_url
    return None

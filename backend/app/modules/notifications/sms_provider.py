from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from app.core.config import Settings


class SmsProviderError(Exception):
    def __init__(self, code: str, message: str, *, terminal: bool = False) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.terminal = terminal


@dataclass(frozen=True)
class SmsMessage:
    to: str
    body: str


class SmsTransport(Protocol):
    def send(self, message: SmsMessage) -> str: ...


class HttpJsonSmsTransport:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def send(self, message: SmsMessage) -> str:
        payload = json.dumps(
            {"to": message.to, "message": message.body, "sender": self.settings.sms_sender}
        ).encode("utf-8")
        request = Request(
            self.settings.sms_api_url,
            data=payload,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.settings.sms_api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=self.settings.sms_timeout_seconds) as response:
                response_data = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            terminal = 400 <= exc.code < 500 and exc.code not in {408, 429}
            raise SmsProviderError(
                f"sms_http_{exc.code}", "SMS provider rejected the request", terminal=terminal
            ) from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise SmsProviderError("sms_network_error", str(exc)) from exc
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SmsProviderError("sms_invalid_response", str(exc)) from exc

        message_id = response_data.get("message_id") or response_data.get("id")
        if not message_id:
            raise SmsProviderError("sms_message_id_missing", "Provider response has no message ID")
        return str(message_id)


def build_sms_message(
    *, to: str, title: str, body: str, action_url: str | None, max_length: int = 480
) -> SmsMessage:
    parts = [title.strip(), body.strip()]
    safe_url = _safe_action_url(action_url)
    if safe_url:
        parts.append(safe_url)
    text = "\n".join(part for part in parts if part)
    return SmsMessage(to=to, body=text[: max(max_length, 1)])


def _safe_action_url(action_url: str | None) -> str | None:
    if not action_url:
        return None
    parsed = urlparse(action_url)
    if action_url.startswith("/") or parsed.scheme in {"http", "https"}:
        return action_url
    return None

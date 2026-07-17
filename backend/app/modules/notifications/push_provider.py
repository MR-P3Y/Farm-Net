from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import Settings


class PushProviderError(Exception):
    def __init__(self, code: str, message: str, *, terminal: bool = False) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.terminal = terminal


@dataclass(frozen=True)
class PushMessage:
    tokens: list[str]
    title: str
    body: str
    action_url: str | None


class PushTransport(Protocol):
    def send(self, message: PushMessage) -> str: ...


class HttpJsonPushTransport:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def send(self, message: PushMessage) -> str:
        payload = json.dumps(
            {
                "tokens": message.tokens,
                "notification": {"title": message.title, "body": message.body},
                "data": {"action_url": message.action_url or ""},
            }
        ).encode("utf-8")
        request = Request(
            self.settings.push_api_url,
            data=payload,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.settings.push_api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=self.settings.push_timeout_seconds) as response:
                data = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            terminal = 400 <= exc.code < 500 and exc.code not in {408, 429}
            raise PushProviderError(
                f"push_http_{exc.code}", "Push provider rejected the request", terminal=terminal
            ) from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise PushProviderError("push_network_error", str(exc)) from exc
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise PushProviderError("push_invalid_response", str(exc)) from exc
        message_id = data.get("message_id") or data.get("id")
        if not message_id:
            raise PushProviderError("push_message_id_missing", "Provider response has no message ID")
        return str(message_id)

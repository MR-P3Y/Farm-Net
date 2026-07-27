from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence


@dataclass(frozen=True)
class AIProviderMessage:
    role: str
    content: str


@dataclass(frozen=True)
class AIProviderRequest:
    request_id: int
    messages: Sequence[AIProviderMessage]
    model_key: str
    prompt_policy_version: str
    timeout_seconds: int
    metadata: Mapping[str, str]


@dataclass(frozen=True)
class AIProviderUsage:
    input_tokens: int
    output_tokens: int
    cached_input_tokens: int = 0


@dataclass(frozen=True)
class AIProviderResult:
    provider_request_id: str | None
    model_key: str
    content: str
    finish_reason: str
    usage: AIProviderUsage
    raw_metadata: Mapping[str, Any]


class AIModelProvider(Protocol):
    """Server-side provider boundary; implementations must never expose secrets."""

    @property
    def provider_key(self) -> str: ...

    def generate(self, request: AIProviderRequest) -> AIProviderResult: ...

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence


@dataclass(frozen=True)
class AIProviderMessage:
    role: str
    content: str


@dataclass(frozen=True)
class AIProviderImage:
    media_type: str
    data_base64: str


@dataclass(frozen=True)
class AIProviderRequest:
    request_id: int
    messages: Sequence[AIProviderMessage]
    model_key: str
    prompt_policy_version: str
    timeout_seconds: int
    metadata: Mapping[str, str]
    max_output_tokens: int = 1200
    reasoning_effort: str = "low"
    images: Sequence[AIProviderImage] = ()


@dataclass(frozen=True)
class AIProviderUsage:
    input_tokens: int
    output_tokens: int
    cached_input_tokens: int = 0
    reasoning_tokens: int = 0


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


class AIProviderError(RuntimeError):
    """Sanitized Provider failure suitable for retry routing and audit."""

    def __init__(self, code: str, *, retryable: bool, status_code: int | None = None) -> None:
        super().__init__(code)
        self.code = code
        self.retryable = retryable
        self.status_code = status_code

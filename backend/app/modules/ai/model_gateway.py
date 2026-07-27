import hashlib
from collections.abc import Mapping

import httpx

from app.core.config import Settings, get_settings
from app.modules.ai.contracts import (
    AIModelProvider,
    AIProviderError,
    AIProviderRequest,
    AIProviderResult,
    AIProviderUsage,
)


class OpenAIResponsesProvider:
    """OpenAI Responses API adapter behind Farm-Net's provider-neutral contract."""

    provider_key = "openai"

    def __init__(
        self, *, settings: Settings | None = None, client: httpx.Client | None = None
    ) -> None:
        self.settings = settings or get_settings()
        self._client = client

    def generate(self, request: AIProviderRequest) -> AIProviderResult:
        api_key = self.settings.openai_api_key.strip()
        if not self.settings.ai_provider_enabled or not api_key:
            raise AIProviderError("AI_PROVIDER_DISABLED", retryable=False)

        input_items = []
        non_system_messages = [
            message for message in request.messages if message.role != "system"
        ]
        for index, message in enumerate(non_system_messages):
            content: object = message.content
            if index == len(non_system_messages) - 1 and request.images:
                content = [{"type": "input_text", "text": message.content}]
                content.extend(
                    {
                        "type": "input_image",
                        "image_url": f"data:{image.media_type};base64,{image.data_base64}",
                        "detail": "high",
                    }
                    for image in request.images
                )
            input_items.append({"role": message.role, "content": content})
        instructions = "\n\n".join(
            message.content for message in request.messages if message.role == "system"
        )
        payload: dict[str, object] = {
            "model": request.model_key,
            "input": input_items,
            "store": False,
            "max_output_tokens": request.max_output_tokens,
            "reasoning": {"effort": request.reasoning_effort},
            "safety_identifier": self._safety_identifier(request.metadata),
        }
        if instructions:
            payload["instructions"] = instructions

        owns_client = self._client is None
        client = self._client or httpx.Client(timeout=request.timeout_seconds)
        try:
            response = client.post(
                f"{self.settings.openai_base_url.rstrip('/')}/responses",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            raise AIProviderError("AI_PROVIDER_UNAVAILABLE", retryable=True) from exc
        finally:
            if owns_client:
                client.close()

        if response.status_code >= 400:
            provider_error_code = self._provider_error_code(response)
            permanent_codes = {
                "insufficient_quota",
                "invalid_api_key",
                "model_not_found",
                "unsupported_value",
            }
            retryable = (
                provider_error_code not in permanent_codes
                and (response.status_code in {408, 409, 429} or response.status_code >= 500)
            )
            if provider_error_code == "insufficient_quota":
                code = "AI_PROVIDER_QUOTA_EXHAUSTED"
            else:
                code = "AI_PROVIDER_TRANSIENT" if retryable else "AI_PROVIDER_REJECTED"
            raise AIProviderError(code, retryable=retryable, status_code=response.status_code)

        try:
            body = response.json()
            content = self._output_text(body)
            usage = body.get("usage") or {}
            input_details = usage.get("input_tokens_details") or {}
            output_details = usage.get("output_tokens_details") or {}
        except (TypeError, ValueError) as exc:
            raise AIProviderError("AI_PROVIDER_INVALID_RESPONSE", retryable=False) from exc
        if not content.strip():
            raise AIProviderError("AI_PROVIDER_EMPTY_RESPONSE", retryable=False)

        return AIProviderResult(
            provider_request_id=self._optional_string(body.get("id")),
            model_key=self._optional_string(body.get("model")) or request.model_key,
            content=content,
            finish_reason=self._optional_string(body.get("status")) or "completed",
            usage=AIProviderUsage(
                input_tokens=self._nonnegative_int(usage.get("input_tokens")),
                output_tokens=self._nonnegative_int(usage.get("output_tokens")),
                cached_input_tokens=self._nonnegative_int(input_details.get("cached_tokens")),
                reasoning_tokens=self._nonnegative_int(output_details.get("reasoning_tokens")),
            ),
            raw_metadata={
                "status": self._optional_string(body.get("status")),
                "incomplete_reason": self._incomplete_reason(body),
            },
        )

    @staticmethod
    def _output_text(body: Mapping[str, object]) -> str:
        direct = body.get("output_text")
        if isinstance(direct, str):
            return direct
        parts: list[str] = []
        output = body.get("output")
        if isinstance(output, list):
            for item in output:
                if not isinstance(item, dict):
                    continue
                content = item.get("content")
                if not isinstance(content, list):
                    continue
                for part in content:
                    if isinstance(part, dict) and isinstance(part.get("text"), str):
                        parts.append(part["text"])
        return "\n".join(parts)

    @staticmethod
    def _safety_identifier(metadata: Mapping[str, str]) -> str:
        stable_value = metadata.get("user_id") or metadata.get("trace_id") or "anonymous"
        return "farm-net-" + hashlib.sha256(stable_value.encode()).hexdigest()[:32]

    @staticmethod
    def _optional_string(value: object) -> str | None:
        return value if isinstance(value, str) and value else None

    @staticmethod
    def _nonnegative_int(value: object) -> int:
        return value if isinstance(value, int) and value >= 0 else 0

    @staticmethod
    def _incomplete_reason(body: Mapping[str, object]) -> str | None:
        details = body.get("incomplete_details")
        if isinstance(details, dict):
            return OpenAIResponsesProvider._optional_string(details.get("reason"))
        return None

    @staticmethod
    def _provider_error_code(response: httpx.Response) -> str | None:
        try:
            body = response.json()
        except ValueError:
            return None
        error = body.get("error") if isinstance(body, dict) else None
        if not isinstance(error, dict):
            return None
        return OpenAIResponsesProvider._optional_string(error.get("code"))


class AIModelGateway:
    def __init__(self, providers: Mapping[str, AIModelProvider]) -> None:
        self._providers = dict(providers)

    def generate(self, provider_key: str, request: AIProviderRequest) -> AIProviderResult:
        provider = self._providers.get(provider_key)
        if provider is None:
            raise AIProviderError("AI_PROVIDER_NOT_REGISTERED", retryable=False)
        return provider.generate(request)

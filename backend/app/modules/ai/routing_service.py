from collections.abc import Mapping, Sequence

from app.modules.ai.contracts import (
    AIProviderError,
    AIProviderMessage,
    AIProviderRequest,
    AIProviderResult,
)
from app.modules.ai.model_gateway import AIModelGateway
from app.modules.ai.policy_registry import ResolvedAIRoute


class AIRoutingService:
    def __init__(self, gateway: AIModelGateway) -> None:
        self.gateway = gateway

    def generate(
        self,
        *,
        request_id: int,
        route: ResolvedAIRoute,
        messages: Sequence[AIProviderMessage],
        metadata: Mapping[str, str],
    ) -> tuple[AIProviderResult, str]:
        policy_messages = (
            AIProviderMessage(role="system", content=route.prompt_policy.system_prompt),
            *messages,
        )
        last_error: AIProviderError | None = None
        for index, model in enumerate(route.models):
            try:
                result = self.gateway.generate(
                    model.provider_key,
                    AIProviderRequest(
                        request_id=request_id,
                        messages=policy_messages,
                        model_key=model.model_key,
                        prompt_policy_version=route.prompt_policy.version,
                        timeout_seconds=model.timeout_seconds,
                        metadata=metadata,
                        max_output_tokens=model.max_output_tokens,
                        reasoning_effort=model.reasoning_effort,
                    ),
                )
                return result, route.route_version
            except AIProviderError as exc:
                last_error = exc
                if not exc.retryable or index + 1 >= len(route.models):
                    raise
        assert last_error is not None
        raise last_error

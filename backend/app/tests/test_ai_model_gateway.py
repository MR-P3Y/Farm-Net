from types import SimpleNamespace

import httpx
import pytest
from sqlalchemy import CheckConstraint, UniqueConstraint

from app.core.config import Settings
from app.modules.ai.contracts import (
    AIProviderError,
    AIProviderMessage,
    AIProviderRequest,
    AIProviderResult,
    AIProviderUsage,
)
from app.modules.ai.model_gateway import AIModelGateway, OpenAIResponsesProvider
from app.modules.ai.models import (
    AIModelConfiguration,
    AIPromptPolicyVersion,
    AIRoutingPolicyVersion,
)
from app.modules.ai.policy_registry import ResolvedAIRoute
from app.modules.ai.routing_service import AIRoutingService


def _constraint_names(model, kind) -> set[str | None]:
    return {
        constraint.name
        for constraint in model.__table__.constraints
        if isinstance(constraint, kind)
    }


def _request() -> AIProviderRequest:
    return AIProviderRequest(
        request_id=7,
        messages=(
            AIProviderMessage(role="system", content="قوانین"),
            AIProviderMessage(role="user", content="سلام"),
        ),
        model_key="gpt-5.6-luna",
        prompt_policy_version="barzegar-v1",
        timeout_seconds=30,
        metadata={"user_id": "42"},
    )


def test_registry_tables_are_versioned_active_and_secret_free() -> None:
    assert {
        AIPromptPolicyVersion.__tablename__,
        AIModelConfiguration.__tablename__,
        AIRoutingPolicyVersion.__tablename__,
    } == {
        "ai_prompt_policy_versions",
        "ai_model_configurations",
        "ai_routing_policy_versions",
    }
    assert "uq_ai_prompt_policy_version" in _constraint_names(
        AIPromptPolicyVersion, UniqueConstraint
    )
    assert "uq_ai_model_configuration_version" in _constraint_names(
        AIModelConfiguration, UniqueConstraint
    )
    assert "ck_ai_routing_policy_fallback" in _constraint_names(
        AIRoutingPolicyVersion, CheckConstraint
    )
    assert "api_key" not in AIModelConfiguration.__table__.c


def test_openai_adapter_uses_responses_api_and_returns_sanitized_usage() -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["body"] = request.read().decode()
        return httpx.Response(
            200,
            json={
                "id": "resp_1",
                "model": "gpt-5.6-luna",
                "status": "completed",
                "output_text": "پاسخ برزگر",
                "usage": {
                    "input_tokens": 12,
                    "output_tokens": 8,
                    "input_tokens_details": {"cached_tokens": 3},
                    "output_tokens_details": {"reasoning_tokens": 2},
                },
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    settings = Settings(
        ai_provider_enabled=True,
        openai_api_key="not-a-real-key",
        database_url="mysql+pymysql://farmnet:farmnet@localhost/farmnet",
    )
    result = OpenAIResponsesProvider(settings=settings, client=client).generate(_request())

    assert captured["url"].endswith("/v1/responses")
    assert "not-a-real-key" not in captured["body"]
    assert result.content == "پاسخ برزگر"
    assert result.usage.cached_input_tokens == 3
    assert result.usage.reasoning_tokens == 2
    assert "api_key" not in result.raw_metadata


def test_openai_adapter_classifies_transient_and_permanent_failures() -> None:
    settings = Settings(
        ai_provider_enabled=True,
        openai_api_key="not-a-real-key",
        database_url="mysql+pymysql://farmnet:farmnet@localhost/farmnet",
    )
    for status, retryable in ((429, True), (500, True), (400, False)):
        client = httpx.Client(
            transport=httpx.MockTransport(
                lambda _request, status=status: httpx.Response(status, json={"error": {}})
            )
        )
        with pytest.raises(AIProviderError) as error:
            OpenAIResponsesProvider(settings=settings, client=client).generate(_request())
        assert error.value.retryable is retryable

    quota_client = httpx.Client(
        transport=httpx.MockTransport(
            lambda _request: httpx.Response(
                429,
                json={"error": {"code": "insufficient_quota"}},
            )
        )
    )
    with pytest.raises(AIProviderError) as quota_error:
        OpenAIResponsesProvider(settings=settings, client=quota_client).generate(_request())
    assert quota_error.value.code == "AI_PROVIDER_QUOTA_EXHAUSTED"
    assert quota_error.value.retryable is False


class _Provider:
    provider_key = "openai"

    def __init__(self, outcomes: list[object]) -> None:
        self.outcomes = outcomes
        self.models: list[str] = []

    def generate(self, request: AIProviderRequest) -> AIProviderResult:
        self.models.append(request.model_key)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome  # type: ignore[return-value]


def _route() -> ResolvedAIRoute:
    prompt = SimpleNamespace(system_prompt="قوانین برزگر", version="barzegar-v1")
    primary = SimpleNamespace(
        provider_key="openai",
        model_key="gpt-5.6-luna",
        timeout_seconds=30,
        max_output_tokens=1000,
        reasoning_effort="low",
    )
    fallback = SimpleNamespace(
        provider_key="openai",
        model_key="gpt-5.6-terra",
        timeout_seconds=60,
        max_output_tokens=2000,
        reasoning_effort="medium",
    )
    return ResolvedAIRoute(
        route_version="routing-v1",
        prompt_policy=prompt,  # type: ignore[arg-type]
        models=(primary, fallback),  # type: ignore[arg-type]
    )


def test_routing_falls_back_once_only_for_retryable_failure() -> None:
    success = AIProviderResult(
        provider_request_id="resp_2",
        model_key="gpt-5.6-terra",
        content="پاسخ",
        finish_reason="completed",
        usage=AIProviderUsage(input_tokens=1, output_tokens=1),
        raw_metadata={},
    )
    provider = _Provider(
        [AIProviderError("AI_PROVIDER_TRANSIENT", retryable=True), success]
    )
    service = AIRoutingService(AIModelGateway({"openai": provider}))
    result, route_version = service.generate(
        request_id=1,
        route=_route(),
        messages=(AIProviderMessage(role="user", content="سلام"),),
        metadata={"user_id": "1"},
    )
    assert result is success
    assert route_version == "routing-v1"
    assert provider.models == ["gpt-5.6-luna", "gpt-5.6-terra"]

    provider = _Provider([AIProviderError("AI_PROVIDER_REJECTED", retryable=False)])
    with pytest.raises(AIProviderError):
        AIRoutingService(AIModelGateway({"openai": provider})).generate(
            request_id=2,
            route=_route(),
            messages=(AIProviderMessage(role="user", content="سلام"),),
            metadata={"user_id": "2"},
        )
    assert provider.models == ["gpt-5.6-luna"]

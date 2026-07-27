from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.modules.ai.models import (
    AIModelConfiguration,
    AIPromptPolicyVersion,
    AIRoutingPolicyVersion,
)


@dataclass(frozen=True)
class ResolvedAIRoute:
    route_version: str
    prompt_policy: AIPromptPolicyVersion
    models: tuple[AIModelConfiguration, ...]


class AIPolicyRegistry:
    """Read-only runtime resolver for immutable, activated configuration versions."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def resolve(self, *, feature_code: str, request_kind: str) -> ResolvedAIRoute:
        active_scope = f"{feature_code}:{request_kind}"
        route = self.db.scalar(
            select(AIRoutingPolicyVersion).where(
                AIRoutingPolicyVersion.active_scope == active_scope,
                AIRoutingPolicyVersion.status == "active",
            )
        )
        if route is None:
            raise AppException("AI_ROUTE_NOT_CONFIGURED", "AI route is not configured", 503)

        prompt = self.db.get(AIPromptPolicyVersion, route.prompt_policy_id)
        primary = self.db.get(AIModelConfiguration, route.primary_model_configuration_id)
        fallback = (
            self.db.get(AIModelConfiguration, route.fallback_model_configuration_id)
            if route.fallback_model_configuration_id is not None
            else None
        )
        if (
            prompt is None
            or prompt.status != "active"
            or primary is None
            or not primary.enabled
            or (fallback is not None and not fallback.enabled)
        ):
            raise AppException(
                "AI_ROUTE_CONFIGURATION_INVALID", "AI route configuration is invalid", 503
            )
        models = (primary,) if fallback is None else (primary, fallback)
        if len(models) != route.max_provider_attempts:
            raise AppException(
                "AI_ROUTE_CONFIGURATION_INVALID", "AI route configuration is invalid", 503
            )
        return ResolvedAIRoute(
            route_version=route.version, prompt_policy=prompt, models=models
        )

    def resolve_version(
        self,
        *,
        feature_code: str,
        request_kind: str,
        route_version: str,
        prompt_policy_version: str,
    ) -> ResolvedAIRoute:
        route = self.db.scalar(
            select(AIRoutingPolicyVersion).where(
                AIRoutingPolicyVersion.feature_code == feature_code,
                AIRoutingPolicyVersion.request_kind == request_kind,
                AIRoutingPolicyVersion.version == route_version,
            )
        )
        if route is None:
            raise AppException("AI_ROUTE_VERSION_NOT_FOUND", "AI route version was not found", 503)
        resolved = self._resolve_row(route)
        if resolved.prompt_policy.version != prompt_policy_version:
            raise AppException(
                "AI_PROMPT_POLICY_VERSION_MISMATCH",
                "AI prompt policy version does not match the route",
                503,
            )
        return resolved

    def _resolve_row(self, route: AIRoutingPolicyVersion) -> ResolvedAIRoute:
        prompt = self.db.get(AIPromptPolicyVersion, route.prompt_policy_id)
        primary = self.db.get(AIModelConfiguration, route.primary_model_configuration_id)
        fallback = (
            self.db.get(AIModelConfiguration, route.fallback_model_configuration_id)
            if route.fallback_model_configuration_id is not None
            else None
        )
        if (
            prompt is None
            or primary is None
            or not primary.enabled
            or (fallback is not None and not fallback.enabled)
        ):
            raise AppException(
                "AI_ROUTE_CONFIGURATION_INVALID", "AI route configuration is invalid", 503
            )
        models = (primary,) if fallback is None else (primary, fallback)
        if len(models) != route.max_provider_attempts:
            raise AppException(
                "AI_ROUTE_CONFIGURATION_INVALID", "AI route configuration is invalid", 503
            )
        return ResolvedAIRoute(
            route_version=route.version, prompt_policy=prompt, models=models
        )

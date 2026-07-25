# ruff: noqa: E402

import argparse
from datetime import UTC, datetime
from decimal import Decimal
import json
import os
from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from app.core.config import Settings
from app.modules.notifications.email_provider import (
    SmtpEmailTransport,
    build_email_envelope,
)
from app.modules.notifications.push_provider import HttpJsonPushTransport, PushMessage
from app.modules.notifications.sms_provider import HttpJsonSmsTransport, build_sms_message
from app.modules.orders.payment_gateway import ZarinpalGateway


PROVIDERS = ("email", "sms", "push", "payment")
CONFIRMATION = "LIVE-STAGING-DELIVERY"


def result(provider: str, mode: str, status: str, code: str) -> dict[str, str]:
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "provider": provider,
        "mode": mode,
        "status": status,
        "code": code,
    }


def safe_code(value: object) -> str:
    candidate = str(value).upper()
    if not candidate or len(candidate) > 64:
        return "PROVIDER_REJECTED"
    if not all(character.isalnum() or character in "_-" for character in candidate):
        return "PROVIDER_REJECTED"
    return candidate


def verify_provider(
    settings: Settings,
    provider: str,
    *,
    execute: bool,
    confirmation: str,
) -> dict[str, str]:
    mode = "execute" if execute else "preflight"
    enabled = {
        "email": settings.email_enabled,
        "sms": settings.sms_enabled,
        "push": settings.push_enabled,
        "payment": settings.payment_gateway_enabled,
    }[provider]
    if not enabled:
        return result(provider, mode, "blocked", "PROVIDER_DISABLED")

    try:
        settings.validate_runtime_safety()
    except ValueError:
        return result(provider, mode, "blocked", "RUNTIME_CONFIGURATION_INVALID")

    if not execute:
        return result(provider, mode, "ready", "CONFIGURATION_VALID")
    if settings.app_env.strip().lower() != "staging":
        return result(provider, mode, "blocked", "STAGING_ENVIRONMENT_REQUIRED")
    if confirmation != CONFIRMATION:
        return result(provider, mode, "blocked", "EXPLICIT_CONFIRMATION_REQUIRED")

    try:
        if provider == "email":
            recipient = os.environ.get("STAGING_EMAIL_RECIPIENT", "").strip()
            if not recipient:
                return result(provider, mode, "blocked", "TEST_RECIPIENT_REQUIRED")
            envelope = build_email_envelope(
                to=recipient,
                title="Farm-Net staging verification",
                body="Credentialed Email provider verification.",
                action_url=settings.public_base_url,
            )
            SmtpEmailTransport(settings).send(envelope)
        elif provider == "sms":
            recipient = os.environ.get("STAGING_SMS_RECIPIENT", "").strip()
            if not recipient:
                return result(provider, mode, "blocked", "TEST_RECIPIENT_REQUIRED")
            message = build_sms_message(
                to=recipient,
                title="Farm-Net",
                body="Staging SMS provider verification.",
                action_url=None,
            )
            HttpJsonSmsTransport(settings).send(message)
        elif provider == "push":
            token = os.environ.get("STAGING_PUSH_TOKEN", "").strip()
            if not token:
                return result(provider, mode, "blocked", "TEST_TOKEN_REQUIRED")
            HttpJsonPushTransport(settings).send(
                PushMessage(
                    tokens=[token],
                    title="Farm-Net",
                    body="Staging Push provider verification.",
                    action_url=settings.public_base_url,
                )
            )
        else:
            if not settings.payment_zarinpal_sandbox:
                return result(provider, mode, "blocked", "PAYMENT_SANDBOX_REQUIRED")
            ZarinpalGateway(settings).request_payment(
                amount=Decimal("1000"),
                invoice_id=0,
                description="Farm-Net credentialed staging verification",
            )
    except Exception as exc:
        code = getattr(exc, "code", f"{type(exc).__name__}_ERROR")
        return result(provider, mode, "failed", safe_code(code))
    return result(provider, mode, "verified", "EXTERNAL_PROVIDER_ACCEPTED")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Safely verify credentialed Farm-Net staging providers"
    )
    parser.add_argument("--provider", choices=(*PROVIDERS, "all"), default="all")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirm", default="")
    parser.add_argument(
        "--require-verified",
        action="store_true",
        help="Return non-zero unless every selected provider was externally verified.",
    )
    args = parser.parse_args()

    settings = Settings()
    selected = PROVIDERS if args.provider == "all" else (args.provider,)
    results = [
        verify_provider(
            settings,
            provider,
            execute=args.execute,
            confirmation=args.confirm,
        )
        for provider in selected
    ]
    print(json.dumps({"providers": results}, sort_keys=True), flush=True)
    if args.require_verified and any(item["status"] != "verified" for item in results):
        return 2
    return 1 if any(item["status"] == "failed" for item in results) else 0


if __name__ == "__main__":
    sys.exit(main())

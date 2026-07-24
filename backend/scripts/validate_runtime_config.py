import json
from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.config import get_settings  # noqa: E402


def main() -> None:
    settings = get_settings()
    print(
        json.dumps(
            {
                "status": "ok",
                "app_env": settings.app_env,
                "app_version": settings.app_version,
                "debug": settings.app_debug,
                "dev_otp": settings.auth_dev_otp_enabled,
                "rate_limit": settings.rate_limit_enabled,
                "cors_origin_count": len(settings.cors_origin_list),
                "trusted_proxy_count": len(settings.trusted_proxy_host_set),
                "media_storage_absolute": settings.media_storage_path_is_absolute,
                "providers": {
                    "email": settings.email_enabled,
                    "sms": settings.sms_enabled,
                    "push": settings.push_enabled,
                    "payment": settings.payment_gateway_enabled,
                    "payment_sandbox": settings.payment_zarinpal_sandbox,
                },
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

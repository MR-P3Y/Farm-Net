from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import trace_id_middleware
from app.core.rate_limit import create_rate_limit_middleware
from app.modules.auth.router import router as auth_router
from app.modules.health.router import router as health_router


settings = get_settings()


def create_app() -> FastAPI:
    setup_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.app_debug,
    )

    app.middleware("http")(trace_id_middleware)
    app.middleware("http")(
        create_rate_limit_middleware(
            enabled=settings.rate_limit_enabled,
            max_requests=settings.rate_limit_requests,
            window_seconds=settings.rate_limit_window_seconds,
        )
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(health_router, prefix=settings.api_v1_prefix)
    app.include_router(auth_router, prefix=settings.api_v1_prefix)

    register_exception_handlers(app)

    return app


app = create_app()

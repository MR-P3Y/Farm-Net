from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import trace_id_middleware
from app.core.rate_limit import create_rate_limit_middleware
from app.modules.admin.router import router as admin_router
from app.modules.auth.router import router as auth_router
from app.modules.geo.router import router as geo_router
from app.modules.health.router import router as health_router
from app.modules.media.access_router import router as media_access_router
from app.modules.media.admin_access_router import router as admin_media_access_router
from app.modules.media.router import router as media_router
from app.modules.orders.admin_router import router as admin_orders_router
from app.modules.orders.checkout_router import router as checkout_router
from app.modules.orders.commission_router import router as commission_router
from app.modules.orders.payments_router import router as payments_router
from app.modules.orders.router import router as orders_router
from app.modules.orders.seller_router import router as seller_orders_router
from app.modules.products.public_router import router as public_products_router
from app.modules.products.router import router as products_router
from app.modules.profiles.router import router as profile_router
from app.modules.stores.public_router import router as public_stores_router
from app.modules.stores.router import router as stores_router


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
    app.include_router(admin_router, prefix=settings.api_v1_prefix)
    app.include_router(geo_router, prefix=settings.api_v1_prefix)
    app.include_router(profile_router, prefix=settings.api_v1_prefix)
    app.include_router(stores_router, prefix=settings.api_v1_prefix)
    app.include_router(public_stores_router, prefix=settings.api_v1_prefix)
    app.include_router(public_products_router, prefix=settings.api_v1_prefix)
    app.include_router(products_router, prefix=settings.api_v1_prefix)
    app.include_router(orders_router, prefix=settings.api_v1_prefix)
    app.include_router(checkout_router, prefix=settings.api_v1_prefix)
    app.include_router(payments_router, prefix=settings.api_v1_prefix)
    app.include_router(seller_orders_router, prefix=settings.api_v1_prefix)
    app.include_router(admin_orders_router, prefix=settings.api_v1_prefix)
    app.include_router(commission_router, prefix=settings.api_v1_prefix)
    app.include_router(media_router, prefix=settings.api_v1_prefix)
    app.include_router(media_access_router, prefix=settings.api_v1_prefix)
    app.include_router(admin_media_access_router, prefix=settings.api_v1_prefix)

    register_exception_handlers(app)

    return app


app = create_app()

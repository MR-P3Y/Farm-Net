from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import trace_id_middleware
from app.core.observability import configure_app_info
from app.core.openapi import install_typed_openapi
from app.core.rate_limit import create_rate_limit_middleware
from app.core.security_headers import create_security_headers_middleware
from app.modules.admin.router import router as admin_router
from app.modules.auth.router import router as auth_router
from app.modules.consultants.admin_router import router as admin_consultants_router
from app.modules.consultants.router import router as consultants_router
from app.modules.expert.admin_router import router as admin_expert_router
from app.modules.expert.router import router as expert_router
from app.modules.farms.router import router as farms_router
from app.modules.farms.cycle_router import cycle_router as farm_cycle_router
from app.modules.farms.cycle_router import reference_router as farm_reference_router
from app.modules.farms.environment_router import router as farm_environment_router
from app.modules.farms.diary_router import router as farm_diary_router
from app.modules.geo.router import router as geo_router
from app.modules.health.router import router as health_router
from app.modules.health.observability_router import router as observability_router
from app.modules.media.access_router import router as media_access_router
from app.modules.media.admin_access_router import router as admin_media_access_router
from app.modules.media.admin_router import router as admin_media_router
from app.modules.media.router import router as media_router
from app.modules.notifications.admin_router import router as admin_notifications_router
from app.modules.notifications.router import router as notifications_router
from app.modules.orders.admin_router import router as admin_orders_router
from app.modules.orders.checkout_router import router as checkout_router
from app.modules.orders.finance_router import router as finance_router
from app.modules.finance.router import router as user_finance_router
from app.modules.orders.commission_router import router as commission_router
from app.modules.orders.payments_router import router as payments_router
from app.modules.orders.router import router as orders_router
from app.modules.orders.seller_router import router as seller_orders_router
from app.modules.products.public_router import router as public_products_router
from app.modules.products.router import router as products_router
from app.modules.profiles.router import router as profile_router
from app.modules.social.admin_router import router as admin_social_router
from app.modules.social.router import router as social_router
from app.modules.search.router import router as search_router
from app.modules.services.admin_router import router as admin_services_router
from app.modules.services.router import router as services_router
from app.modules.rentals.admin_router import router as admin_rentals_router
from app.modules.rentals.router import router as rentals_router
from app.modules.reviews.router import router as reviews_router
from app.modules.reviews.admin_router import router as admin_reviews_router
from app.modules.stores.public_router import router as public_stores_router
from app.modules.stores.router import router as stores_router
from app.modules.weather.admin_router import router as admin_weather_router
from app.modules.weather.router import router as weather_router


settings = get_settings()


def create_app() -> FastAPI:
    setup_logging(settings.log_level)
    configure_app_info(version=settings.app_version, environment=settings.app_env)

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
            backend=settings.rate_limit_backend,
            redis_url=settings.redis_url,
            search_max_requests=settings.search_rate_limit_requests,
            search_window_seconds=settings.search_rate_limit_window_seconds,
            auth_max_requests=settings.auth_rate_limit_requests,
            auth_window_seconds=settings.auth_rate_limit_window_seconds,
            max_keys=settings.rate_limit_max_keys,
            trusted_proxy_hosts=settings.trusted_proxy_host_set,
        )
    )
    app.middleware("http")(
        create_security_headers_middleware(
            environment=settings.app_env,
            trusted_proxy_hosts=settings.trusted_proxy_host_set,
        )
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=[
            "Accept",
            "Authorization",
            "Content-Type",
            "X-Trace-Id",
        ],
        expose_headers=[
            "X-Trace-Id",
            "Retry-After",
            "RateLimit-Limit",
            "RateLimit-Remaining",
        ],
        max_age=600,
    )

    app.include_router(health_router)
    app.include_router(health_router, prefix=settings.api_v1_prefix)
    app.include_router(observability_router)
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
    app.include_router(finance_router, prefix=settings.api_v1_prefix)
    app.include_router(user_finance_router, prefix=settings.api_v1_prefix)
    app.include_router(commission_router, prefix=settings.api_v1_prefix)
    app.include_router(media_router, prefix=settings.api_v1_prefix)
    app.include_router(media_access_router, prefix=settings.api_v1_prefix)
    app.include_router(admin_media_access_router, prefix=settings.api_v1_prefix)
    app.include_router(admin_media_router, prefix=settings.api_v1_prefix)
    app.include_router(notifications_router, prefix=settings.api_v1_prefix)
    app.include_router(admin_notifications_router, prefix=settings.api_v1_prefix)
    app.include_router(weather_router, prefix=settings.api_v1_prefix)
    app.include_router(admin_weather_router, prefix=settings.api_v1_prefix)
    app.include_router(consultants_router, prefix=settings.api_v1_prefix)
    app.include_router(admin_consultants_router, prefix=settings.api_v1_prefix)
    app.include_router(services_router, prefix=settings.api_v1_prefix)
    app.include_router(admin_services_router, prefix=settings.api_v1_prefix)
    app.include_router(rentals_router, prefix=settings.api_v1_prefix)
    app.include_router(admin_rentals_router, prefix=settings.api_v1_prefix)
    app.include_router(reviews_router, prefix=settings.api_v1_prefix)
    app.include_router(admin_reviews_router, prefix=settings.api_v1_prefix)
    app.include_router(social_router, prefix=settings.api_v1_prefix)
    app.include_router(search_router, prefix=settings.api_v1_prefix)
    app.include_router(admin_social_router, prefix=settings.api_v1_prefix)
    app.include_router(expert_router, prefix=settings.api_v1_prefix)
    app.include_router(admin_expert_router, prefix=settings.api_v1_prefix)
    app.include_router(farms_router, prefix=settings.api_v1_prefix)
    app.include_router(farm_cycle_router, prefix=settings.api_v1_prefix)
    app.include_router(farm_reference_router, prefix=settings.api_v1_prefix)
    app.include_router(farm_environment_router, prefix=settings.api_v1_prefix)
    app.include_router(farm_diary_router, prefix=settings.api_v1_prefix)

    register_exception_handlers(app)
    install_typed_openapi(app)

    return app


app = create_app()

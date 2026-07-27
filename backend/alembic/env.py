from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import get_settings
from app.db.base import Base
from app.modules.auth import models as auth_models  # noqa: F401
from app.modules.geo import models as geo_models  # noqa: F401
from app.modules.profiles import models as profile_models  # noqa: F401
from app.modules.stores import models as store_models  # noqa: F401
from app.modules.products import models as product_models  # noqa: F401
from app.modules.orders import models as order_models  # noqa: F401
from app.modules.media import models as media_models  # noqa: F401
from app.modules.notifications import models as notification_models  # noqa: F401
from app.modules.weather import models as weather_models  # noqa: F401
from app.modules.social import models as social_models  # noqa: F401
from app.modules.services import models as service_models  # noqa: F401
from app.modules.expert import models as expert_models  # noqa: F401
from app.modules.consultants import models as consultant_models  # noqa: F401
from app.modules.rentals import models as rental_models  # noqa: F401
from app.modules.finance import models as finance_models  # noqa: F401
from app.modules.reviews import models as review_models  # noqa: F401
from app.modules.farms import models as farm_models  # noqa: F401
from app.modules.subscriptions import models as subscription_models  # noqa: F401
from app.modules.ai import models as ai_models  # noqa: F401


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

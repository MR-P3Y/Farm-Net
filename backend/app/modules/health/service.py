from sqlalchemy.orm import Session

from app.core.database import check_database
from app.core.redis import check_redis


def get_health_status(db: Session) -> dict[str, str]:
    database_status = "ok" if check_database(db) else "error"
    redis_status = "ok" if check_redis() else "error"

    return {
        "app": "ok",
        "database": database_status,
        "redis": redis_status,
    }
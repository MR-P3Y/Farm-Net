from pydantic import BaseModel


class HealthStatus(BaseModel):
    app: str
    database: str
    redis: str
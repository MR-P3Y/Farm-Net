from datetime import datetime

from pydantic import BaseModel, Field

from app.modules.favorites.enums import FavoriteSubjectType


class FavoriteItemOut(BaseModel):
    id: int
    subject_type: FavoriteSubjectType
    subject_id: int
    title: str | None = None
    subtitle: str | None = None
    image_url: str | None = None
    route: str | None = None
    is_available: bool
    created_at: datetime


class FavoriteStatusOut(BaseModel):
    subject_type: FavoriteSubjectType
    favorite_subject_ids: list[int] = Field(default_factory=list)

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SocialCategoryOut(BaseModel):
    id: int
    code: str
    title: str
    description: str | None = None
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SocialPostCreateIn(BaseModel):
    category_id: int | None = None

    title: str = Field(min_length=3, max_length=255)
    body: str = Field(min_length=3)

    post_type: str = Field(min_length=2, max_length=40)
    visibility: str = Field(default="public", min_length=2, max_length=40)

    media_file_id: int | None = None

    country_code: str | None = Field(default=None, max_length=2)
    province_id: int | None = None
    city_id: int | None = None
    village_id: int | None = None

    province_name: str | None = Field(default=None, max_length=120)
    city_name: str | None = Field(default=None, max_length=120)
    village_name: str | None = Field(default=None, max_length=120)

    latitude: str | None = Field(default=None, max_length=40)
    longitude: str | None = Field(default=None, max_length=40)

    metadata_json: dict[str, Any] | None = None


class SocialPostOut(BaseModel):
    id: int

    author_user_id: int
    category_id: int | None = None

    title: str
    body: str

    post_type: str
    status: str
    visibility: str

    media_file_id: int | None = None

    country_code: str | None = None
    province_id: int | None = None
    city_id: int | None = None
    village_id: int | None = None

    province_name: str | None = None
    city_name: str | None = None
    village_name: str | None = None

    latitude: str | None = None
    longitude: str | None = None

    views_count: int
    comments_count: int
    reactions_count: int
    reports_count: int

    metadata_json: dict[str, Any] | None = None

    published_at: datetime | None = None
    deleted_at: datetime | None = None

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SocialPostListFilter(BaseModel):
    category_id: int | None = None
    post_type: str | None = None
    q: str | None = None
    page: int = 1
    page_size: int = 20


class SocialPostModerationIn(BaseModel):
    reason: str | None = Field(default=None, max_length=1000)


class SocialCommentCreateIn(BaseModel):
    body: str = Field(min_length=2, max_length=5000)
    parent_comment_id: int | None = None


class SocialCommentOut(BaseModel):
    id: int
    post_id: int
    author_user_id: int
    parent_comment_id: int | None = None

    body: str
    status: str

    reactions_count: int
    reports_count: int

    deleted_at: datetime | None = None

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class NotificationEventCreateIn(BaseModel):
    event_key: str | None = Field(default=None, max_length=80)
    event_type: str = Field(min_length=3, max_length=80)

    actor_user_id: int | None = None

    source_type: str | None = Field(default=None, max_length=80)
    source_id: str | None = Field(default=None, max_length=80)

    payload_json: dict[str, Any] | None = None


class NotificationCreateIn(BaseModel):
    recipient_user_id: int
    channel: str = Field(default="in_app", max_length=30)

    title: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1)

    action_url: str | None = Field(default=None, max_length=500)

    priority: str = Field(default="normal", max_length=30)


class NotificationSystemMessageIn(BaseModel):
    recipient_user_id: int

    title: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1)

    action_url: str | None = Field(default=None, max_length=500)
    priority: str = Field(default="normal", max_length=30)


class NotificationPreferenceIn(BaseModel):
    event_type: str = Field(default="*", min_length=1, max_length=80)
    channel: str = Field(max_length=30)
    is_enabled: bool


class NotificationPreferenceOut(BaseModel):
    id: int
    user_id: int
    event_type: str
    channel: str
    is_enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NotificationEventOut(BaseModel):
    id: int
    event_key: str
    event_type: str

    actor_user_id: int | None = None

    source_type: str | None = None
    source_id: str | None = None

    payload_json: dict[str, Any] | None = None

    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationOut(BaseModel):
    id: int

    event_id: int | None = None
    recipient_user_id: int

    channel: str

    title: str
    body: str
    action_url: str | None = None

    priority: str
    status: str

    read_at: datetime | None = None

    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = {"from_attributes": True}


class NotificationDeliveryLogOut(BaseModel):
    id: int
    notification_id: int

    channel: str
    provider: str | None = None
    provider_message_id: str | None = None

    status: str

    error_code: str | None = None
    error_message: str | None = None

    attempt_count: int
    max_attempts: int
    next_attempt_at: datetime | None = None
    last_attempt_at: datetime | None = None
    locked_at: datetime | None = None

    sent_at: datetime | None = None
    delivered_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationDeliveryAttemptOut(BaseModel):
    id: int
    delivery_log_id: int
    attempt_number: int
    provider: str | None = None
    status: str
    error_code: str | None = None
    error_message: str | None = None
    started_at: datetime
    finished_at: datetime | None = None

    model_config = {"from_attributes": True}


class NotificationDeliveryDetailOut(NotificationDeliveryLogOut):
    attempts: list[NotificationDeliveryAttemptOut]


class NotificationDeliveryFailureIn(BaseModel):
    error_code: str = Field(min_length=1, max_length=80)
    error_message: str = Field(min_length=1)

from __future__ import annotations

from sqlalchemy.orm import Session

from app.modules.notifications.models import (
    Notification,
    NotificationDeliveryLog,
    NotificationEvent,
)


class NotificationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def commit(self) -> None:
        self.db.commit()

    def refresh(self, row: object) -> None:
        self.db.refresh(row)

    def add_event(self, row: NotificationEvent) -> NotificationEvent:
        self.db.add(row)
        self.db.flush()
        return row

    def add_notification(self, row: Notification) -> Notification:
        self.db.add(row)
        self.db.flush()
        return row

    def add_delivery_log(
        self,
        row: NotificationDeliveryLog,
    ) -> NotificationDeliveryLog:
        self.db.add(row)
        self.db.flush()
        return row

    def get_event_by_key(self, *, event_key: str) -> NotificationEvent | None:
        return (
            self.db.query(NotificationEvent)
            .filter(NotificationEvent.event_key == event_key)
            .one_or_none()
        )

    def get_notification_by_id(
        self,
        *,
        notification_id: int,
    ) -> Notification | None:
        return (
            self.db.query(Notification)
            .filter(Notification.id == notification_id)
            .one_or_none()
        )

    def get_user_notification_by_id(
        self,
        *,
        notification_id: int,
        recipient_user_id: int,
    ) -> Notification | None:
        return (
            self.db.query(Notification)
            .filter(
                Notification.id == notification_id,
                Notification.recipient_user_id == recipient_user_id,
                Notification.status != "deleted",
            )
            .one_or_none()
        )

    def list_user_notifications(
        self,
        *,
        recipient_user_id: int,
        status: str | None = None,
        channel: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Notification], int]:
        query = self.db.query(Notification).filter(
            Notification.recipient_user_id == recipient_user_id,
            Notification.status != "deleted",
        )

        if status:
            query = query.filter(Notification.status == status)

        if channel:
            query = query.filter(Notification.channel == channel)

        total = query.count()

        rows = (
            query.order_by(Notification.created_at.desc(), Notification.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return rows, total

    def unread_count(self, *, recipient_user_id: int) -> int:
        return (
            self.db.query(Notification)
            .filter(
                Notification.recipient_user_id == recipient_user_id,
                Notification.channel == "in_app",
                Notification.status == "unread",
            )
            .count()
        )

    def list_unread_user_notifications(
        self,
        *,
        recipient_user_id: int,
    ) -> list[Notification]:
        return (
            self.db.query(Notification)
            .filter(
                Notification.recipient_user_id == recipient_user_id,
                Notification.channel == "in_app",
                Notification.status == "unread",
            )
            .all()
        )

    def list_admin_notifications(
        self,
        *,
        status: str | None = None,
        channel: str | None = None,
        recipient_user_id: int | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Notification], int]:
        query = self.db.query(Notification)

        if status:
            query = query.filter(Notification.status == status)

        if channel:
            query = query.filter(Notification.channel == channel)

        if recipient_user_id:
            query = query.filter(Notification.recipient_user_id == recipient_user_id)

        total = query.count()

        rows = (
            query.order_by(Notification.created_at.desc(), Notification.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return rows, total

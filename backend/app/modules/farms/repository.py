from sqlalchemy.orm import Session

from app.modules.farms.models import Farm


class FarmRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, row: Farm) -> Farm:
        self.db.add(row)
        self.db.flush()
        return row

    def get_owned(
        self,
        *,
        farm_id: int,
        owner_user_id: int,
        for_update: bool = False,
    ) -> Farm | None:
        query = self.db.query(Farm).filter(
            Farm.id == farm_id,
            Farm.owner_user_id == owner_user_id,
        )
        if for_update:
            query = query.with_for_update()
        return query.one_or_none()

    def list_owned(
        self,
        *,
        owner_user_id: int,
        include_archived: bool,
        offset: int,
        limit: int,
    ) -> tuple[list[Farm], int]:
        query = self.db.query(Farm).filter(Farm.owner_user_id == owner_user_id)
        if not include_archived:
            query = query.filter(Farm.status == "active")
        total = query.count()
        rows = (
            query.order_by(Farm.updated_at.desc(), Farm.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return rows, total

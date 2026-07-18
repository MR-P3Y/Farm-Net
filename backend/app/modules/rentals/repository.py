from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.modules.rentals.models import LessorProfile, RentalCategory, RentalEquipment


class RentalRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_category(self, category_id: int) -> RentalCategory | None:
        return self.db.query(RentalCategory).filter(RentalCategory.id == category_id).one_or_none()

    def get_category_by_code(self, code: str) -> RentalCategory | None:
        return self.db.query(RentalCategory).filter(RentalCategory.code == code).one_or_none()

    def list_categories(self, *, active_only: bool, q: str | None) -> list[RentalCategory]:
        query = self.db.query(RentalCategory)
        if active_only:
            query = query.filter(RentalCategory.is_active.is_(True))
        if q:
            like = f"%{q.strip()}%"
            query = query.filter(
                or_(
                    RentalCategory.code.ilike(like),
                    RentalCategory.title.ilike(like),
                    RentalCategory.description.ilike(like),
                )
            )
        return query.order_by(
            RentalCategory.sort_order, RentalCategory.title, RentalCategory.id
        ).all()

    def category_counts(self, category_id: int) -> tuple[int, int]:
        children = (
            self.db.query(RentalCategory).filter(RentalCategory.parent_id == category_id).count()
        )
        equipment = (
            self.db.query(RentalEquipment)
            .filter(
                RentalEquipment.category_id == category_id, RentalEquipment.deleted_at.is_(None)
            )
            .count()
        )
        return children, equipment

    def get_profile_by_user(self, user_id: int) -> LessorProfile | None:
        return (
            self.db.query(LessorProfile)
            .filter(LessorProfile.user_id == user_id, LessorProfile.deleted_at.is_(None))
            .one_or_none()
        )

    def get_profile(self, profile_id: int) -> LessorProfile | None:
        return (
            self.db.query(LessorProfile)
            .filter(LessorProfile.id == profile_id, LessorProfile.deleted_at.is_(None))
            .one_or_none()
        )

    def list_profiles(
        self,
        *,
        status: str | None,
        province_id: int | None,
        city_id: int | None,
        q: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[LessorProfile], int]:
        query = self.db.query(LessorProfile).filter(LessorProfile.deleted_at.is_(None))
        if status:
            query = query.filter(LessorProfile.status == status)
        if province_id:
            query = query.filter(LessorProfile.province_id == province_id)
        if city_id:
            query = query.filter(LessorProfile.city_id == city_id)
        if q:
            like = f"%{q.strip()}%"
            query = query.filter(
                or_(
                    LessorProfile.display_name.ilike(like),
                    LessorProfile.bio.ilike(like),
                    LessorProfile.phone.ilike(like),
                )
            )
        total = query.count()
        return query.order_by(LessorProfile.created_at.desc(), LessorProfile.id.desc()).offset(
            (page - 1) * page_size
        ).limit(page_size).all(), total

    def equipment_count(self, profile_id: int) -> int:
        return (
            self.db.query(RentalEquipment)
            .filter(
                RentalEquipment.lessor_profile_id == profile_id,
                RentalEquipment.deleted_at.is_(None),
            )
            .count()
        )

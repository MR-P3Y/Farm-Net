from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.modules.media.models import MediaFile
from app.modules.rentals.models import (
    LessorProfile,
    RentalCategory,
    RentalEquipment,
    RentalEquipmentMedia,
)


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

    def get_media(self, media_file_id: int) -> MediaFile | None:
        return self.db.query(MediaFile).filter(MediaFile.id == media_file_id).one_or_none()

    def get_equipment(self, equipment_id: int) -> RentalEquipment | None:
        return (
            self.db.query(RentalEquipment)
            .options(
                joinedload(RentalEquipment.category),
                joinedload(RentalEquipment.media),
                joinedload(RentalEquipment.lessor_profile),
            )
            .filter(RentalEquipment.id == equipment_id, RentalEquipment.deleted_at.is_(None))
            .one_or_none()
        )

    def get_public_equipment(self, equipment_id: int) -> RentalEquipment | None:
        return (
            self.db.query(RentalEquipment)
            .join(LessorProfile)
            .options(
                joinedload(RentalEquipment.category),
                joinedload(RentalEquipment.media),
                joinedload(RentalEquipment.lessor_profile),
            )
            .filter(
                RentalEquipment.id == equipment_id,
                RentalEquipment.status == "approved",
                RentalEquipment.is_active.is_(True),
                RentalEquipment.deleted_at.is_(None),
                LessorProfile.status == "approved",
                LessorProfile.deleted_at.is_(None),
            )
            .one_or_none()
        )

    def list_equipment(
        self,
        *,
        public: bool,
        lessor_profile_id: int | None = None,
        status: str | None = None,
        category_id: int | None = None,
        province_id: int | None = None,
        city_id: int | None = None,
        operator_mode: str | None = None,
        q: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[RentalEquipment], int]:
        query = (
            self.db.query(RentalEquipment)
            .options(
                joinedload(RentalEquipment.category),
                joinedload(RentalEquipment.media),
                joinedload(RentalEquipment.lessor_profile),
            )
            .filter(RentalEquipment.deleted_at.is_(None))
        )
        if public:
            query = query.join(LessorProfile).filter(
                RentalEquipment.status == "approved",
                RentalEquipment.is_active.is_(True),
                LessorProfile.status == "approved",
                LessorProfile.deleted_at.is_(None),
            )
        if lessor_profile_id:
            query = query.filter(RentalEquipment.lessor_profile_id == lessor_profile_id)
        if status:
            query = query.filter(RentalEquipment.status == status)
        if category_id:
            query = query.filter(RentalEquipment.category_id == category_id)
        if province_id:
            query = query.filter(RentalEquipment.province_id == province_id)
        if city_id:
            query = query.filter(RentalEquipment.city_id == city_id)
        if operator_mode:
            query = query.filter(RentalEquipment.operator_mode == operator_mode)
        if q:
            like = f"%{q.strip()}%"
            query = query.filter(
                or_(
                    RentalEquipment.title.ilike(like),
                    RentalEquipment.description.ilike(like),
                    RentalEquipment.manufacturer.ilike(like),
                    RentalEquipment.model_name.ilike(like),
                )
            )
        total = query.count()
        rows = (
            query.order_by(RentalEquipment.created_at.desc(), RentalEquipment.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return rows, total

    def replace_equipment_media(
        self, equipment: RentalEquipment, rows: list[RentalEquipmentMedia]
    ) -> None:
        self.db.query(RentalEquipmentMedia).filter(
            RentalEquipmentMedia.equipment_id == equipment.id
        ).delete(synchronize_session=False)
        for row in rows:
            row.equipment_id = equipment.id
            self.db.add(row)
        self.db.flush()

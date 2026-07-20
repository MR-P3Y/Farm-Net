from decimal import Decimal

from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.common.money import CurrencyCode
from app.common.search import normalize_search_text
from app.common.search_sql import search_match_expression, search_relevance_expression

from app.modules.media.models import MediaFile
from app.modules.rentals.enums import RentalDiscoverySort
from app.modules.rentals.models import (
    LessorProfile,
    RentalCategory,
    RentalEquipment,
    RentalEquipmentMedia,
    RentalPricingRule,
    RentalAvailabilityBlock,
    RentalRequest,
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
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        available_from=None,
        available_to=None,
        sort: RentalDiscoverySort | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[RentalEquipment], int]:
        query = (
            self.db.query(RentalEquipment)
            .options(
                joinedload(RentalEquipment.category),
                joinedload(RentalEquipment.media),
                joinedload(RentalEquipment.lessor_profile),
                joinedload(RentalEquipment.pricing_rules),
            )
            .outerjoin(RentalCategory, RentalEquipment.category_id == RentalCategory.id)
            .filter(RentalEquipment.deleted_at.is_(None))
        )
        if public:
            query = query.filter(
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
            query = query.filter(RentalEquipment.category_id.in_(self._category_scope(category_id)))
        if province_id:
            query = query.filter(RentalEquipment.province_id == province_id)
        if city_id:
            query = query.filter(RentalEquipment.city_id == city_id)
        if operator_mode:
            query = query.filter(RentalEquipment.operator_mode == operator_mode)
        normalized_q = normalize_search_text(q) if q else None
        if normalized_q:
            query = query.filter(
                search_match_expression(
                    normalized_q,
                    RentalEquipment.title,
                    RentalEquipment.slug,
                    RentalEquipment.description,
                    RentalEquipment.manufacturer,
                    RentalEquipment.model_name,
                    LessorProfile.display_name,
                    RentalCategory.title,
                )
            )

        minimum_price = (
            select(func.min(RentalPricingRule.price_amount))
            .where(
                RentalPricingRule.equipment_id == RentalEquipment.id,
                RentalPricingRule.is_active.is_(True),
                RentalPricingRule.currency == CurrencyCode.TOMAN.value,
            )
            .correlate(RentalEquipment)
            .scalar_subquery()
        )
        if min_price is not None:
            query = query.filter(minimum_price >= min_price)
        if max_price is not None:
            query = query.filter(minimum_price <= max_price)

        if available_from is not None and available_to is not None:
            query = query.filter(
                ~RentalEquipment.availability_blocks.any(
                    (RentalAvailabilityBlock.starts_at < available_to)
                    & (RentalAvailabilityBlock.ends_at > available_from)
                ),
                ~RentalEquipment.requests.any(
                    RentalRequest.status.in_(("accepted", "in_progress"))
                    & (RentalRequest.starts_at < available_to)
                    & (RentalRequest.ends_at > available_from)
                ),
            )
        total = query.count()

        null_price = case((minimum_price.is_(None), 1), else_=0)
        if sort == RentalDiscoverySort.PRICE_ASC:
            ordering = (null_price.asc(), minimum_price.asc(), RentalEquipment.id.desc())
        elif sort == RentalDiscoverySort.PRICE_DESC:
            ordering = (null_price.asc(), minimum_price.desc(), RentalEquipment.id.desc())
        elif sort == RentalDiscoverySort.RELEVANCE and normalized_q:
            ordering = (
                search_relevance_expression(
                    normalized_q,
                    RentalEquipment.title,
                    RentalEquipment.slug,
                    RentalEquipment.description,
                    RentalEquipment.manufacturer,
                    RentalEquipment.model_name,
                    LessorProfile.display_name,
                    RentalCategory.title,
                ).desc(),
                RentalEquipment.created_at.desc(),
                RentalEquipment.id.desc(),
            )
        else:
            ordering = (RentalEquipment.created_at.desc(), RentalEquipment.id.desc())
        rows = (
            query.order_by(*ordering)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return rows, total

    def _category_scope(self, category_id: int) -> set[int]:
        rows = self.db.query(RentalCategory.id, RentalCategory.parent_id).filter(
            RentalCategory.is_active.is_(True)
        ).all()
        children: dict[int, list[int]] = {}
        known_ids = set()
        for row_id, parent_id in rows:
            known_ids.add(row_id)
            if parent_id is not None:
                children.setdefault(parent_id, []).append(row_id)
        if category_id not in known_ids:
            return {category_id}
        scope = {category_id}
        pending = [category_id]
        while pending:
            for child_id in children.get(pending.pop(), []):
                if child_id not in scope:
                    scope.add(child_id)
                    pending.append(child_id)
        return scope

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

    def list_pricing_rules(
        self, equipment_id: int, *, active_only: bool = False
    ) -> list[RentalPricingRule]:
        query = self.db.query(RentalPricingRule).filter(
            RentalPricingRule.equipment_id == equipment_id
        )
        if active_only:
            query = query.filter(RentalPricingRule.is_active.is_(True))
        return query.order_by(
            RentalPricingRule.unit, RentalPricingRule.operator_included, RentalPricingRule.id
        ).all()

    def replace_pricing_rules(self, equipment_id: int, rows: list[RentalPricingRule]) -> None:
        self.db.query(RentalPricingRule).filter(
            RentalPricingRule.equipment_id == equipment_id
        ).delete(synchronize_session=False)
        for row in rows:
            row.equipment_id = equipment_id
            self.db.add(row)
        self.db.flush()

    def list_availability_blocks(
        self, equipment_id: int, *, starts_at=None, ends_at=None
    ) -> list[RentalAvailabilityBlock]:
        query = self.db.query(RentalAvailabilityBlock).filter(
            RentalAvailabilityBlock.equipment_id == equipment_id
        )
        if starts_at is not None and ends_at is not None:
            query = query.filter(
                RentalAvailabilityBlock.starts_at < ends_at,
                RentalAvailabilityBlock.ends_at > starts_at,
            )
        return query.order_by(RentalAvailabilityBlock.starts_at, RentalAvailabilityBlock.id).all()

    def get_availability_block(self, block_id: int) -> RentalAvailabilityBlock | None:
        return (
            self.db.query(RentalAvailabilityBlock)
            .filter(RentalAvailabilityBlock.id == block_id)
            .one_or_none()
        )

    def has_booking_overlap(self, equipment_id: int, starts_at, ends_at) -> bool:
        return (
            self.db.query(RentalRequest.id)
            .filter(
                RentalRequest.equipment_id == equipment_id,
                RentalRequest.status.in_(("accepted", "in_progress")),
                RentalRequest.starts_at < ends_at,
                RentalRequest.ends_at > starts_at,
            )
            .first()
            is not None
        )

    def get_pricing_rule(self, pricing_rule_id: int) -> RentalPricingRule | None:
        return (
            self.db.query(RentalPricingRule)
            .filter(RentalPricingRule.id == pricing_rule_id)
            .one_or_none()
        )

    def get_request(self, request_id: int, *, lock: bool = False) -> RentalRequest | None:
        query = self.db.query(RentalRequest).filter(RentalRequest.id == request_id)
        if lock:
            query = query.with_for_update()
        return query.one_or_none()

    def lock_equipment(self, equipment_id: int) -> RentalEquipment | None:
        return (
            self.db.query(RentalEquipment)
            .filter(RentalEquipment.id == equipment_id)
            .with_for_update()
            .one_or_none()
        )

    def list_requests(
        self,
        *,
        requester_user_id: int | None = None,
        lessor_profile_id: int | None = None,
        equipment_id: int | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[RentalRequest], int]:
        query = self.db.query(RentalRequest).options(
            joinedload(RentalRequest.status_logs),
            joinedload(RentalRequest.equipment),
            joinedload(RentalRequest.lessor_profile),
        )
        if requester_user_id:
            query = query.filter(RentalRequest.requester_user_id == requester_user_id)
        if lessor_profile_id:
            query = query.filter(RentalRequest.lessor_profile_id == lessor_profile_id)
        if equipment_id:
            query = query.filter(RentalRequest.equipment_id == equipment_id)
        if status:
            query = query.filter(RentalRequest.status == status)
        total = query.count()
        rows = (
            query.order_by(RentalRequest.created_at.desc(), RentalRequest.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return rows, total

    def conflicting_booking(
        self, equipment_id: int, starts_at, ends_at, *, exclude_request_id: int | None = None
    ) -> RentalRequest | None:
        query = self.db.query(RentalRequest).filter(
            RentalRequest.equipment_id == equipment_id,
            RentalRequest.status.in_(("accepted", "in_progress")),
            RentalRequest.starts_at < ends_at,
            RentalRequest.ends_at > starts_at,
        )
        if exclude_request_id:
            query = query.filter(RentalRequest.id != exclude_request_id)
        return query.with_for_update().first()

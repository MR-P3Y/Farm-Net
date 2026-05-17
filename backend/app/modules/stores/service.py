import re
from datetime import datetime
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.exceptions import ValidationAuthError
from app.modules.auth.models import AuthUser
from app.modules.stores.enums import (
    StoreMemberRole,
    StoreMemberStatus,
    StoreStatus,
    StoreType,
)
from app.modules.stores.models import Store, StoreStatusHistory
from app.modules.stores.repository import StoreRepository
from app.modules.stores.schemas import (
    StoreCreateIn,
    StoreOut,
    StoreStatusHistoryOut,
    StoreUpdateIn,
)


class StoreService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = StoreRepository(db)

    def create_my_store(
        self,
        *,
        user: AuthUser,
        payload: StoreCreateIn,
    ) -> StoreOut:
        existing = self.repo.get_user_active_store(user_id=user.id)
        if existing is not None:
            raise ValidationAuthError(
                message="User already has a store",
                details={
                    "store_id": existing.id,
                    "status": existing.status,
                },
            )

        self._validate_payload_common(
            name=payload.name,
            slug=payload.slug,
            store_type=payload.store_type,
            postal_code=payload.postal_code,
            latitude=payload.latitude,
            longitude=payload.longitude,
        )
        self._validate_geo_consistency(
            province_id=payload.province_id,
            county_id=payload.county_id,
            district_id=payload.district_id,
            city_id=payload.city_id,
            village_id=payload.village_id,
        )

        store = self.repo.create_store(
            owner_user_id=user.id,
            name=payload.name,
            slug=payload.slug,
            status=StoreStatus.DRAFT.value,
            store_type=payload.store_type,
            description=payload.description,
            phone=payload.phone,
            email=payload.email,
            province_id=payload.province_id,
            county_id=payload.county_id,
            district_id=payload.district_id,
            city_id=payload.city_id,
            village_id=payload.village_id,
            address=payload.address,
            postal_code=payload.postal_code,
            latitude=payload.latitude,
            longitude=payload.longitude,
            logo_file_id=payload.logo_file_id,
            banner_file_id=payload.banner_file_id,
        )

        self.repo.create_store_member(
            store_id=store.id,
            user_id=user.id,
            role=StoreMemberRole.OWNER.value,
            status=StoreMemberStatus.ACTIVE.value,
            invited_by=None,
            joined_at=datetime.utcnow(),
        )

        self.repo.create_status_history(
            store_id=store.id,
            changed_by=user.id,
            from_status=None,
            to_status=StoreStatus.DRAFT.value,
            note="Store created as draft",
        )

        try:
            self.repo.commit()
        except IntegrityError as exc:
            self.repo.rollback()
            raise ValidationAuthError(
                message="Store data conflicts with existing data",
                details={"field": "slug"},
            ) from exc

        self.repo.refresh(store)
        return self._store_out(store)

    def get_my_store(self, *, user: AuthUser) -> StoreOut | None:
        store = self.repo.get_user_active_store(user_id=user.id)
        if store is None:
            return None

        return self._store_out(store)

    def get_my_store_by_id(
        self,
        *,
        user: AuthUser,
        store_id: int,
    ) -> StoreOut:
        store = self.repo.get_user_store_by_id(
            user_id=user.id,
            store_id=store_id,
        )

        if store is None:
            raise ValidationAuthError(
                message="Store not found",
                details={"store_id": store_id},
            )

        return self._store_out(store)

    def update_my_store(
        self,
        *,
        user: AuthUser,
        store_id: int,
        payload: StoreUpdateIn,
    ) -> StoreOut:
        store = self.repo.get_user_store_by_id(
            user_id=user.id,
            store_id=store_id,
        )

        if store is None:
            raise ValidationAuthError(
                message="Store not found",
                details={"store_id": store_id},
            )

        if store.status not in {
            StoreStatus.DRAFT.value,
            StoreStatus.REJECTED.value,
            StoreStatus.APPROVED.value,
        }:
            raise ValidationAuthError(
                message="Store cannot be updated in current status",
                details={"current_status": store.status},
            )

        next_name = payload.name if payload.name is not None else store.name
        next_slug = payload.slug if payload.slug is not None else store.slug
        next_store_type = (
            payload.store_type if payload.store_type is not None else store.store_type
        )
        next_postal_code = (
            payload.postal_code
            if payload.postal_code is not None
            else store.postal_code
        )
        next_latitude = (
            payload.latitude if payload.latitude is not None else store.latitude
        )
        next_longitude = (
            payload.longitude if payload.longitude is not None else store.longitude
        )

        next_province_id = (
            payload.province_id
            if payload.province_id is not None
            else store.province_id
        )
        next_county_id = (
            payload.county_id if payload.county_id is not None else store.county_id
        )
        next_district_id = (
            payload.district_id
            if payload.district_id is not None
            else store.district_id
        )
        next_city_id = payload.city_id if payload.city_id is not None else store.city_id
        next_village_id = (
            payload.village_id if payload.village_id is not None else store.village_id
        )

        self._validate_payload_common(
            name=next_name,
            slug=next_slug,
            store_type=next_store_type,
            postal_code=next_postal_code,
            latitude=next_latitude,
            longitude=next_longitude,
        )
        self._validate_geo_consistency(
            province_id=next_province_id,
            county_id=next_county_id,
            district_id=next_district_id,
            city_id=next_city_id,
            village_id=next_village_id,
        )

        store.name = next_name
        store.slug = next_slug
        store.store_type = next_store_type
        store.postal_code = next_postal_code
        store.latitude = next_latitude
        store.longitude = next_longitude

        if payload.description is not None:
            store.description = payload.description
        if payload.phone is not None:
            store.phone = payload.phone
        if payload.email is not None:
            store.email = payload.email
        if payload.province_id is not None:
            store.province_id = payload.province_id
        if payload.county_id is not None:
            store.county_id = payload.county_id
        if payload.district_id is not None:
            store.district_id = payload.district_id
        if payload.city_id is not None:
            store.city_id = payload.city_id
        if payload.village_id is not None:
            store.village_id = payload.village_id
        if payload.address is not None:
            store.address = payload.address
        if payload.logo_file_id is not None:
            store.logo_file_id = payload.logo_file_id
        if payload.banner_file_id is not None:
            store.banner_file_id = payload.banner_file_id

        try:
            self.repo.commit()
        except IntegrityError as exc:
            self.repo.rollback()
            raise ValidationAuthError(
                message="Store data conflicts with existing data",
                details={"field": "slug"},
            ) from exc

        self.repo.refresh(store)
        return self._store_out(store)

    def submit_my_store(
        self,
        *,
        user: AuthUser,
        store_id: int,
    ) -> StoreOut:
        store = self.repo.get_user_store_by_id(
            user_id=user.id,
            store_id=store_id,
        )

        if store is None:
            raise ValidationAuthError(
                message="Store not found",
                details={"store_id": store_id},
            )

        if store.status not in {
            StoreStatus.DRAFT.value,
            StoreStatus.REJECTED.value,
        }:
            raise ValidationAuthError(
                message="Store cannot be submitted in current status",
                details={"current_status": store.status},
            )

        missing = []
        if not store.name:
            missing.append("name")
        if not store.slug:
            missing.append("slug")
        if not store.province_id:
            missing.append("province_id")
        if not store.county_id:
            missing.append("county_id")
        if not store.address:
            missing.append("address")

        if missing:
            raise ValidationAuthError(
                message="Store is not ready for submit",
                details={"missing": missing},
            )

        self._validate_geo_consistency(
            province_id=store.province_id,
            county_id=store.county_id,
            district_id=store.district_id,
            city_id=store.city_id,
            village_id=store.village_id,
        )

        old_status = store.status
        store.status = StoreStatus.PENDING_REVIEW.value

        self.repo.create_status_history(
            store_id=store.id,
            changed_by=user.id,
            from_status=old_status,
            to_status=StoreStatus.PENDING_REVIEW.value,
            note="Store submitted for review",
        )

        self.repo.commit()
        self.repo.refresh(store)

        return self._store_out(store)

    def list_my_store_status_history(
        self,
        *,
        user: AuthUser,
        store_id: int,
    ) -> list[StoreStatusHistoryOut]:
        store = self.repo.get_user_store_by_id(
            user_id=user.id,
            store_id=store_id,
        )

        if store is None:
            raise ValidationAuthError(
                message="Store not found",
                details={"store_id": store_id},
            )

        rows = self.repo.list_status_history(store_id=store.id)
        return [self._history_out(item) for item in rows]

    def _validate_payload_common(
        self,
        *,
        name: str,
        slug: str,
        store_type: str,
        postal_code: str | None,
        latitude: Decimal | None,
        longitude: Decimal | None,
    ) -> None:
        allowed_types = {item.value for item in StoreType}

        if store_type not in allowed_types:
            raise ValidationAuthError(
                message="Invalid store_type",
                details={"allowed": sorted(allowed_types)},
            )

        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,118}[a-z0-9]", slug):
            raise ValidationAuthError(
                message="Invalid slug",
                details={
                    "format": "lowercase letters, numbers and dashes, 3-120 chars",
                },
            )

        if postal_code is not None and not re.fullmatch(r"\d{10}", postal_code):
            raise ValidationAuthError(
                message="Invalid postal_code",
                details={"format": "10 digits"},
            )

        if latitude is not None and not (Decimal("-90") <= latitude <= Decimal("90")):
            raise ValidationAuthError(
                message="Invalid latitude",
                details={"range": "-90 to 90"},
            )

        if longitude is not None and not (
            Decimal("-180") <= longitude <= Decimal("180")
        ):
            raise ValidationAuthError(
                message="Invalid longitude",
                details={"range": "-180 to 180"},
            )

        if not name.strip():
            raise ValidationAuthError(
                message="Store name is required",
                details={"field": "name"},
            )

    def _validate_geo_consistency(
        self,
        *,
        province_id: int | None,
        county_id: int | None,
        district_id: int | None,
        city_id: int | None,
        village_id: int | None,
    ) -> None:
        if province_id is not None:
            province = self.repo.get_province(province_id)
            if province is None:
                raise ValidationAuthError(
                    message="Invalid province_id",
                    details={"province_id": province_id},
                )

        if county_id is not None:
            county = self.repo.get_county(county_id)
            if county is None:
                raise ValidationAuthError(
                    message="Invalid county_id",
                    details={"county_id": county_id},
                )

            if province_id is not None and county.province_id != province_id:
                raise ValidationAuthError(
                    message="county_id does not belong to province_id",
                    details={
                        "province_id": province_id,
                        "county_id": county_id,
                    },
                )

        if district_id is not None:
            district = self.repo.get_district(district_id)
            if district is None:
                raise ValidationAuthError(
                    message="Invalid district_id",
                    details={"district_id": district_id},
                )

            if province_id is not None and district.province_id != province_id:
                raise ValidationAuthError(
                    message="district_id does not belong to province_id",
                    details={
                        "province_id": province_id,
                        "district_id": district_id,
                    },
                )

            if county_id is not None and district.county_id != county_id:
                raise ValidationAuthError(
                    message="district_id does not belong to county_id",
                    details={
                        "county_id": county_id,
                        "district_id": district_id,
                    },
                )

        if city_id is not None:
            city = self.repo.get_city(city_id)
            if city is None:
                raise ValidationAuthError(
                    message="Invalid city_id",
                    details={"city_id": city_id},
                )

            if province_id is not None and city.province_id != province_id:
                raise ValidationAuthError(
                    message="city_id does not belong to province_id",
                    details={
                        "province_id": province_id,
                        "city_id": city_id,
                    },
                )

            if county_id is not None and city.county_id != county_id:
                raise ValidationAuthError(
                    message="city_id does not belong to county_id",
                    details={
                        "county_id": county_id,
                        "city_id": city_id,
                    },
                )

        if village_id is not None:
            village = self.repo.get_village(village_id)
            if village is None:
                raise ValidationAuthError(
                    message="Invalid village_id",
                    details={"village_id": village_id},
                )

            if province_id is not None and village.province_id != province_id:
                raise ValidationAuthError(
                    message="village_id does not belong to province_id",
                    details={
                        "province_id": province_id,
                        "village_id": village_id,
                    },
                )

            if county_id is not None and village.county_id != county_id:
                raise ValidationAuthError(
                    message="village_id does not belong to county_id",
                    details={
                        "county_id": county_id,
                        "village_id": village_id,
                    },
                )

    def _store_out(self, store: Store) -> StoreOut:
        return StoreOut(
            id=store.id,
            owner_user_id=store.owner_user_id,
            name=store.name,
            slug=store.slug,
            description=store.description,
            status=store.status,
            store_type=store.store_type,
            phone=store.phone,
            email=store.email,
            province_id=store.province_id,
            county_id=store.county_id,
            district_id=store.district_id,
            city_id=store.city_id,
            village_id=store.village_id,
            address=store.address,
            postal_code=store.postal_code,
            latitude=store.latitude,
            longitude=store.longitude,
            logo_file_id=store.logo_file_id,
            banner_file_id=store.banner_file_id,
            admin_note=store.admin_note,
            approved_at=store.approved_at.isoformat() if store.approved_at else None,
            approved_by=store.approved_by,
            rejected_at=store.rejected_at.isoformat() if store.rejected_at else None,
            rejected_by=store.rejected_by,
            created_at=store.created_at.isoformat(),
            updated_at=store.updated_at.isoformat(),
        )

    def _history_out(self, row: StoreStatusHistory) -> StoreStatusHistoryOut:
        return StoreStatusHistoryOut(
            id=row.id,
            store_id=row.store_id,
            changed_by=row.changed_by,
            from_status=row.from_status,
            to_status=row.to_status,
            note=row.note,
            created_at=row.created_at.isoformat(),
        )

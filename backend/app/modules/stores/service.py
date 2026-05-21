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
from app.modules.stores.models import Store, StoreMember, StoreStatusHistory
from app.modules.stores.repository import StoreRepository
from app.modules.stores.schemas import (
    StoreCreateIn,
    StoreMemberCreateIn,
    StoreMemberOut,
    StoreMemberUpdateIn,
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
        store = self._get_owned_store(user=user, store_id=store_id)
        return self._store_out(store)

    def update_my_store(
        self,
        *,
        user: AuthUser,
        store_id: int,
        payload: StoreUpdateIn,
    ) -> StoreOut:
        store = self._get_owned_store(user=user, store_id=store_id)

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

        if payload.logo_media_file_key:
            logo = self.repo.get_active_store_logo_media(
                file_key=payload.logo_media_file_key,
            )

            if logo is None or logo.owner_user_id != user.id:
                raise ValidationAuthError(
                    message="Store logo media file not found",
                    details={"logo_media_file_key": payload.logo_media_file_key},
                )

            store.logo_media_file_id = logo.id

        if payload.banner_media_file_key:
            banner = self.repo.get_active_store_banner_media(
                file_key=payload.banner_media_file_key,
            )

            if banner is None or banner.owner_user_id != user.id:
                raise ValidationAuthError(
                    message="Store banner media file not found",
                    details={"banner_media_file_key": payload.banner_media_file_key},
                )

            store.banner_media_file_id = banner.id

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
        store = self._get_owned_store(user=user, store_id=store_id)

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
        store = self._get_owned_store(user=user, store_id=store_id)
        rows = self.repo.list_status_history(store_id=store.id)
        return [self._history_out(item) for item in rows]

    def list_store_members(
        self,
        *,
        user: AuthUser,
        store_id: int,
    ) -> list[StoreMemberOut]:
        store = self._get_owned_store(user=user, store_id=store_id)
        members = self.repo.list_store_members(store_id=store.id)
        return [self._member_out(item) for item in members]

    def add_store_member(
        self,
        *,
        user: AuthUser,
        store_id: int,
        payload: StoreMemberCreateIn,
    ) -> StoreMemberOut:
        store = self._get_owned_store(user=user, store_id=store_id)
        self._ensure_store_owner(user=user, store=store)

        role = self._validate_new_member_role(payload.role)

        target_user = self.repo.get_user_by_id(user_id=payload.user_id)
        if target_user is None:
            raise ValidationAuthError(
                message="User not found",
                details={"user_id": payload.user_id},
            )

        if payload.user_id == store.owner_user_id:
            raise ValidationAuthError(
                message="Store owner is already a member",
                details={"user_id": payload.user_id},
            )

        existing = self.repo.get_store_member_by_user_id(
            store_id=store.id,
            user_id=payload.user_id,
        )

        if existing is not None:
            if existing.status == StoreMemberStatus.REMOVED.value:
                existing.role = role
                existing.status = StoreMemberStatus.ACTIVE.value
                existing.invited_by = user.id
                existing.joined_at = datetime.utcnow()
                self.repo.commit()
                self.repo.refresh(existing)
                return self._member_out(existing)

            raise ValidationAuthError(
                message="User is already a store member",
                details={
                    "user_id": payload.user_id,
                    "member_id": existing.id,
                    "status": existing.status,
                },
            )

        member = self.repo.create_store_member(
            store_id=store.id,
            user_id=payload.user_id,
            role=role,
            status=StoreMemberStatus.ACTIVE.value,
            invited_by=user.id,
            joined_at=datetime.utcnow(),
        )

        self.repo.commit()
        self.repo.refresh(member)

        return self._member_out(member)

    def update_store_member(
        self,
        *,
        user: AuthUser,
        store_id: int,
        member_id: int,
        payload: StoreMemberUpdateIn,
    ) -> StoreMemberOut:
        store = self._get_owned_store(user=user, store_id=store_id)
        self._ensure_store_owner(user=user, store=store)

        member = self.repo.get_store_member_by_id(
            store_id=store.id,
            member_id=member_id,
        )

        if member is None:
            raise ValidationAuthError(
                message="Store member not found",
                details={"member_id": member_id},
            )

        self._ensure_not_owner_member(member)

        if payload.role is not None:
            member.role = self._validate_new_member_role(payload.role)

        if payload.status is not None:
            member.status = self._validate_member_status(payload.status)

        self.repo.commit()
        self.repo.refresh(member)

        return self._member_out(member)

    def remove_store_member(
        self,
        *,
        user: AuthUser,
        store_id: int,
        member_id: int,
    ) -> StoreMemberOut:
        store = self._get_owned_store(user=user, store_id=store_id)
        self._ensure_store_owner(user=user, store=store)

        member = self.repo.get_store_member_by_id(
            store_id=store.id,
            member_id=member_id,
        )

        if member is None:
            raise ValidationAuthError(
                message="Store member not found",
                details={"member_id": member_id},
            )

        self._ensure_not_owner_member(member)

        member.status = StoreMemberStatus.REMOVED.value

        self.repo.commit()
        self.repo.refresh(member)

        return self._member_out(member)

    def _get_owned_store(
        self,
        *,
        user: AuthUser,
        store_id: int,
    ) -> Store:
        store = self.repo.get_user_store_by_id(
            user_id=user.id,
            store_id=store_id,
        )

        if store is None:
            raise ValidationAuthError(
                message="Store not found",
                details={"store_id": store_id},
            )

        return store

    def _ensure_store_owner(
        self,
        *,
        user: AuthUser,
        store: Store,
    ) -> None:
        if store.owner_user_id != user.id:
            raise ValidationAuthError(
                message="Only store owner can manage members",
                details={"store_id": store.id},
            )

    def _validate_new_member_role(self, role: str) -> str:
        allowed = {
            StoreMemberRole.MANAGER.value,
            StoreMemberRole.STAFF.value,
            StoreMemberRole.VIEWER.value,
        }

        if role not in allowed:
            raise ValidationAuthError(
                message="Invalid store member role",
                details={"allowed": sorted(allowed)},
            )

        return role

    def _validate_member_status(self, status: str) -> str:
        allowed = {
            StoreMemberStatus.ACTIVE.value,
            StoreMemberStatus.SUSPENDED.value,
            StoreMemberStatus.REMOVED.value,
        }

        if status not in allowed:
            raise ValidationAuthError(
                message="Invalid store member status",
                details={"allowed": sorted(allowed)},
            )

        return status

    def _ensure_not_owner_member(self, member: StoreMember) -> None:
        if member.role == StoreMemberRole.OWNER.value:
            raise ValidationAuthError(
                message="Store owner member cannot be modified",
                details={"member_id": member.id},
            )

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
        logo_media = (
            self.repo.get_media_by_id(media_file_id=store.logo_media_file_id)
            if store.logo_media_file_id
            else None
        )
        banner_media = (
            self.repo.get_media_by_id(media_file_id=store.banner_media_file_id)
            if store.banner_media_file_id
            else None
        )
        logo_file_key = logo_media.file_key if logo_media else None
        banner_file_key = banner_media.file_key if banner_media else None

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
            logo_media_file_id=store.logo_media_file_id,
            logo_file_key=logo_file_key,
            logo_url=self._media_public_url(file_key=logo_file_key),
            banner_media_file_id=store.banner_media_file_id,
            banner_file_key=banner_file_key,
            banner_url=self._media_public_url(file_key=banner_file_key),
            admin_note=store.admin_note,
            approved_at=store.approved_at.isoformat() if store.approved_at else None,
            approved_by=store.approved_by,
            rejected_at=store.rejected_at.isoformat() if store.rejected_at else None,
            rejected_by=store.rejected_by,
            created_at=store.created_at.isoformat(),
            updated_at=store.updated_at.isoformat(),
        )

    def _media_public_url(self, *, file_key: str | None) -> str | None:
        if not file_key:
            return None
        return f"/api/v1/media/public/{file_key}"

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

    def _member_out(self, member: StoreMember) -> StoreMemberOut:
        return StoreMemberOut(
            id=member.id,
            store_id=member.store_id,
            user_id=member.user_id,
            role=member.role,
            status=member.status,
            invited_by=member.invited_by,
            joined_at=member.joined_at.isoformat() if member.joined_at else None,
            created_at=member.created_at.isoformat(),
            updated_at=member.updated_at.isoformat(),
        )

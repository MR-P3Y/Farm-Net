from sqlalchemy.orm import Session

from app.modules.media.enums import MediaPurpose, MediaStatus, MediaVisibility
from app.modules.media.models import MediaFile
from app.modules.auth.models import AuthUser
from app.modules.geo.models import (
    GeoCity,
    GeoCounty,
    GeoDistrict,
    GeoProvince,
    GeoVillage,
)
from app.modules.stores.models import Store, StoreMember, StoreStatusHistory


class StoreRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_user_active_store(self, *, user_id: int) -> Store | None:
        return (
            self.db.query(Store)
            .filter(
                Store.owner_user_id == user_id,
                Store.deleted_at.is_(None),
            )
            .order_by(Store.created_at.desc())
            .first()
        )

    def get_store_by_id(self, *, store_id: int) -> Store | None:
        return (
            self.db.query(Store)
            .filter(
                Store.id == store_id,
                Store.deleted_at.is_(None),
            )
            .one_or_none()
        )

    def get_user_store_by_id(self, *, user_id: int, store_id: int) -> Store | None:
        return (
            self.db.query(Store)
            .filter(
                Store.id == store_id,
                Store.owner_user_id == user_id,
                Store.deleted_at.is_(None),
            )
            .one_or_none()
        )

    def get_store_by_slug(self, *, slug: str) -> Store | None:
        return (
            self.db.query(Store)
            .filter(
                Store.slug == slug,
                Store.deleted_at.is_(None),
            )
            .one_or_none()
        )

    def list_stores(
        self,
        *,
        status: str | None = None,
        owner_user_id: int | None = None,
        q: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Store], int]:
        query = self.db.query(Store).filter(Store.deleted_at.is_(None))

        if status:
            query = query.filter(Store.status == status)

        if owner_user_id:
            query = query.filter(Store.owner_user_id == owner_user_id)

        if q:
            pattern = f"%{q}%"
            query = query.filter((Store.name.like(pattern)) | (Store.slug.like(pattern)))

        total = query.count()

        items = (
            query.order_by(Store.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return items, total

    def list_public_stores(
        self,
        *,
        q: str | None = None,
        province_id: int | None = None,
        county_id: int | None = None,
        city_id: int | None = None,
        store_type: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Store], int]:
        query = self.db.query(Store).filter(
            Store.status == "approved",
            Store.deleted_at.is_(None),
        )

        if q:
            pattern = f"%{q}%"
            query = query.filter(
                (Store.name.like(pattern))
                | (Store.slug.like(pattern))
                | (Store.description.like(pattern))
            )

        if province_id:
            query = query.filter(Store.province_id == province_id)

        if county_id:
            query = query.filter(Store.county_id == county_id)

        if city_id:
            query = query.filter(Store.city_id == city_id)

        if store_type:
            query = query.filter(Store.store_type == store_type)

        total = query.count()

        items = (
            query.order_by(Store.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return items, total

    def get_public_store_by_slug(self, *, slug: str) -> Store | None:
        return (
            self.db.query(Store)
            .filter(
                Store.slug == slug,
                Store.status == "approved",
                Store.deleted_at.is_(None),
            )
            .one_or_none()
        )

    def get_active_store_logo_media(
        self,
        *,
        file_key: str,
    ) -> MediaFile | None:
        return (
            self.db.query(MediaFile)
            .filter(
                MediaFile.file_key == file_key,
                MediaFile.purpose == MediaPurpose.STORE_LOGO.value,
                MediaFile.visibility == MediaVisibility.PUBLIC.value,
                MediaFile.status == MediaStatus.ACTIVE.value,
            )
            .one_or_none()
        )

    def get_active_store_banner_media(
        self,
        *,
        file_key: str,
    ) -> MediaFile | None:
        return (
            self.db.query(MediaFile)
            .filter(
                MediaFile.file_key == file_key,
                MediaFile.purpose == MediaPurpose.STORE_BANNER.value,
                MediaFile.visibility == MediaVisibility.PUBLIC.value,
                MediaFile.status == MediaStatus.ACTIVE.value,
            )
            .one_or_none()
        )

    def get_media_by_id(
        self,
        *,
        media_file_id: int,
    ) -> MediaFile | None:
        return (
            self.db.query(MediaFile)
            .filter(MediaFile.id == media_file_id)
            .one_or_none()
        )

    def get_user_by_id(self, *, user_id: int) -> AuthUser | None:
        return self.db.query(AuthUser).filter(AuthUser.id == user_id).one_or_none()

    def list_store_members(self, *, store_id: int) -> list[StoreMember]:
        return (
            self.db.query(StoreMember)
            .filter(StoreMember.store_id == store_id)
            .order_by(StoreMember.created_at.asc())
            .all()
        )

    def get_store_member_by_id(
        self,
        *,
        store_id: int,
        member_id: int,
    ) -> StoreMember | None:
        return (
            self.db.query(StoreMember)
            .filter(
                StoreMember.store_id == store_id,
                StoreMember.id == member_id,
            )
            .one_or_none()
        )

    def get_store_member_by_user_id(
        self,
        *,
        store_id: int,
        user_id: int,
    ) -> StoreMember | None:
        return (
            self.db.query(StoreMember)
            .filter(
                StoreMember.store_id == store_id,
                StoreMember.user_id == user_id,
            )
            .one_or_none()
        )

    def create_store(
        self,
        *,
        owner_user_id: int,
        name: str,
        slug: str,
        status: str,
        store_type: str,
        description: str | None,
        phone: str | None,
        email: str | None,
        province_id: int | None,
        county_id: int | None,
        district_id: int | None,
        city_id: int | None,
        village_id: int | None,
        address: str | None,
        postal_code: str | None,
        latitude,
        longitude,
        logo_file_id: str | None,
        banner_file_id: str | None,
    ) -> Store:
        store = Store(
            owner_user_id=owner_user_id,
            name=name,
            slug=slug,
            status=status,
            store_type=store_type,
            description=description,
            phone=phone,
            email=email,
            province_id=province_id,
            county_id=county_id,
            district_id=district_id,
            city_id=city_id,
            village_id=village_id,
            address=address,
            postal_code=postal_code,
            latitude=latitude,
            longitude=longitude,
            logo_file_id=logo_file_id,
            banner_file_id=banner_file_id,
        )
        self.db.add(store)
        self.db.flush()
        return store

    def create_store_member(
        self,
        *,
        store_id: int,
        user_id: int,
        role: str,
        status: str,
        invited_by: int | None,
        joined_at,
    ) -> StoreMember:
        member = StoreMember(
            store_id=store_id,
            user_id=user_id,
            role=role,
            status=status,
            invited_by=invited_by,
            joined_at=joined_at,
        )
        self.db.add(member)
        self.db.flush()
        return member

    def create_status_history(
        self,
        *,
        store_id: int,
        changed_by: int | None,
        from_status: str | None,
        to_status: str,
        note: str | None,
    ) -> StoreStatusHistory:
        history = StoreStatusHistory(
            store_id=store_id,
            changed_by=changed_by,
            from_status=from_status,
            to_status=to_status,
            note=note,
        )
        self.db.add(history)
        self.db.flush()
        return history

    def list_status_history(self, *, store_id: int) -> list[StoreStatusHistory]:
        return (
            self.db.query(StoreStatusHistory)
            .filter(StoreStatusHistory.store_id == store_id)
            .order_by(StoreStatusHistory.created_at.asc())
            .all()
        )

    def get_province(self, province_id: int) -> GeoProvince | None:
        return (
            self.db.query(GeoProvince)
            .filter(
                GeoProvince.id == province_id,
                GeoProvince.is_active.is_(True),
            )
            .one_or_none()
        )

    def get_county(self, county_id: int) -> GeoCounty | None:
        return (
            self.db.query(GeoCounty)
            .filter(
                GeoCounty.id == county_id,
                GeoCounty.is_active.is_(True),
            )
            .one_or_none()
        )

    def get_district(self, district_id: int) -> GeoDistrict | None:
        return (
            self.db.query(GeoDistrict)
            .filter(
                GeoDistrict.id == district_id,
                GeoDistrict.is_active.is_(True),
            )
            .one_or_none()
        )

    def get_city(self, city_id: int) -> GeoCity | None:
        return (
            self.db.query(GeoCity)
            .filter(
                GeoCity.id == city_id,
                GeoCity.is_active.is_(True),
            )
            .one_or_none()
        )

    def get_village(self, village_id: int) -> GeoVillage | None:
        return (
            self.db.query(GeoVillage)
            .filter(
                GeoVillage.id == village_id,
                GeoVillage.is_active.is_(True),
            )
            .one_or_none()
        )

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    def refresh(self, instance) -> None:
        self.db.refresh(instance)

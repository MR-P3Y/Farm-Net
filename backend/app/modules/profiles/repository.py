from sqlalchemy.orm import Session

from app.modules.geo.models import (
    GeoCity,
    GeoCounty,
    GeoDistrict,
    GeoProvince,
    GeoRuralDistrict,
    GeoVillage,
)
from app.modules.profiles.models import UserDocument, UserProfile


class ProfileRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_profile_by_user_id(self, user_id: int) -> UserProfile | None:
        return (
            self.db.query(UserProfile)
            .filter(UserProfile.user_id == user_id)
            .one_or_none()
        )

    def create_profile(self, *, user_id: int) -> UserProfile:
        profile = UserProfile(user_id=user_id)
        self.db.add(profile)
        self.db.flush()
        return profile

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

    def get_rural_district(self, rural_district_id: int) -> GeoRuralDistrict | None:
        return (
            self.db.query(GeoRuralDistrict)
            .filter(
                GeoRuralDistrict.id == rural_district_id,
                GeoRuralDistrict.is_active.is_(True),
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

    def create_document(
        self,
        *,
        user_id: int,
        document_type: str,
        file_path: str,
        file_name: str,
        mime_type: str | None,
        size_bytes: int | None,
        status: str,
    ) -> UserDocument:
        document = UserDocument(
            user_id=user_id,
            document_type=document_type,
            file_path=file_path,
            file_name=file_name,
            mime_type=mime_type,
            size_bytes=size_bytes,
            status=status,
        )
        self.db.add(document)
        self.db.flush()
        return document

    def list_user_documents(self, *, user_id: int) -> list[UserDocument]:
        return (
            self.db.query(UserDocument)
            .filter(
                UserDocument.user_id == user_id,
                UserDocument.deleted_at.is_(None),
            )
            .order_by(UserDocument.created_at.desc())
            .all()
        )

    def get_user_document(
        self,
        *,
        user_id: int,
        document_id: int,
    ) -> UserDocument | None:
        return (
            self.db.query(UserDocument)
            .filter(
                UserDocument.id == document_id,
                UserDocument.user_id == user_id,
                UserDocument.deleted_at.is_(None),
            )
            .one_or_none()
        )

    def commit(self) -> None:
        self.db.commit()

    def refresh(self, instance) -> None:
        self.db.refresh(instance)

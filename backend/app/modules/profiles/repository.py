from sqlalchemy.orm import Session

from app.modules.geo.models import (
    GeoCity,
    GeoCounty,
    GeoDistrict,
    GeoProvince,
    GeoRuralDistrict,
    GeoVillage,
)
from app.modules.profiles.models import (
    UserDocument,
    UserProfile,
    VerificationRequest,
    VerificationRequestDocument,
    VerificationReview,
)


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

    def get_active_verification_request(
        self,
        *,
        user_id: int,
        target_role: str,
        active_statuses: set[str],
    ) -> VerificationRequest | None:
        return (
            self.db.query(VerificationRequest)
            .filter(
                VerificationRequest.user_id == user_id,
                VerificationRequest.target_role == target_role,
                VerificationRequest.status.in_(active_statuses),
            )
            .order_by(VerificationRequest.created_at.desc())
            .first()
        )

    def create_verification_request(
        self,
        *,
        user_id: int,
        target_role: str,
        status: str,
        request_note: str | None,
    ) -> VerificationRequest:
        request = VerificationRequest(
            user_id=user_id,
            target_role=target_role,
            status=status,
            request_note=request_note,
        )
        self.db.add(request)
        self.db.flush()
        return request

    def list_user_verification_requests(
        self,
        *,
        user_id: int,
    ) -> list[VerificationRequest]:
        return (
            self.db.query(VerificationRequest)
            .filter(VerificationRequest.user_id == user_id)
            .order_by(VerificationRequest.created_at.desc())
            .all()
        )

    def list_verification_requests(
        self,
        *,
        status: str | None = None,
        target_role: str | None = None,
        user_id: int | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[VerificationRequest], int]:
        query = self.db.query(VerificationRequest)

        if status:
            query = query.filter(VerificationRequest.status == status)

        if target_role:
            query = query.filter(VerificationRequest.target_role == target_role)

        if user_id:
            query = query.filter(VerificationRequest.user_id == user_id)

        total = query.count()

        items = (
            query.order_by(VerificationRequest.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return items, total

    def get_user_verification_request(
        self,
        *,
        user_id: int,
        request_id: int,
    ) -> VerificationRequest | None:
        return (
            self.db.query(VerificationRequest)
            .filter(
                VerificationRequest.id == request_id,
                VerificationRequest.user_id == user_id,
            )
            .one_or_none()
        )

    def get_verification_request_by_id(
        self,
        request_id: int,
    ) -> VerificationRequest | None:
        return (
            self.db.query(VerificationRequest)
            .filter(VerificationRequest.id == request_id)
            .one_or_none()
        )

    def get_verification_request_document_link(
        self,
        *,
        request_id: int,
        document_id: int,
    ) -> VerificationRequestDocument | None:
        return (
            self.db.query(VerificationRequestDocument)
            .filter(
                VerificationRequestDocument.verification_request_id == request_id,
                VerificationRequestDocument.document_id == document_id,
            )
            .one_or_none()
        )

    def attach_document_to_verification_request(
        self,
        *,
        request_id: int,
        document_id: int,
    ) -> VerificationRequestDocument:
        existing = self.get_verification_request_document_link(
            request_id=request_id,
            document_id=document_id,
        )

        if existing is not None:
            return existing

        link = VerificationRequestDocument(
            verification_request_id=request_id,
            document_id=document_id,
        )
        self.db.add(link)
        self.db.flush()
        return link

    def create_verification_review(
        self,
        *,
        request_id: int,
        reviewer_id: int | None,
        action: str,
        note: str | None,
    ) -> VerificationReview:
        review = VerificationReview(
            verification_request_id=request_id,
            reviewer_id=reviewer_id,
            action=action,
            note=note,
        )
        self.db.add(review)
        self.db.flush()
        return review

    def commit(self) -> None:
        self.db.commit()

    def refresh(self, instance) -> None:
        self.db.refresh(instance)

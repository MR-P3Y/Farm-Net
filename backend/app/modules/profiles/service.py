from datetime import datetime
import re

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.exceptions import ValidationAuthError
from app.modules.auth.models import AuthUser
from app.modules.profiles.enums import DocumentStatus, DocumentType, Gender
from app.modules.profiles.models import UserDocument, UserProfile
from app.modules.profiles.repository import ProfileRepository
from app.modules.profiles.schemas import (
    DocumentCreateIn,
    DocumentOut,
    ProfileMeOut,
    ProfileUpdateIn,
)


class ProfileService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ProfileRepository(db)

    def get_my_profile(self, user: AuthUser) -> ProfileMeOut:
        profile = self.repo.get_profile_by_user_id(user.id)

        if profile is None:
            return ProfileMeOut(
                user_id=user.id,
                profile_completed=False,
            )

        return self._profile_out(profile)

    def update_my_profile(
        self,
        *,
        user: AuthUser,
        payload: ProfileUpdateIn,
    ) -> ProfileMeOut:
        profile = self.repo.get_profile_by_user_id(user.id)

        if profile is None:
            profile = self.repo.create_profile(user_id=user.id)

        self._validate_payload(payload)
        self._validate_geo_consistency(payload)

        profile.first_name = payload.first_name
        profile.last_name = payload.last_name
        profile.display_name = payload.display_name

        profile.national_id = payload.national_id
        profile.birth_date = payload.birth_date
        profile.gender = payload.gender

        profile.province_id = payload.province_id
        profile.county_id = payload.county_id
        profile.district_id = payload.district_id
        profile.rural_district_id = payload.rural_district_id
        profile.city_id = payload.city_id
        profile.village_id = payload.village_id

        profile.address = payload.address
        profile.postal_code = payload.postal_code

        profile.avatar_file_id = payload.avatar_file_id
        profile.bio = payload.bio

        try:
            self.repo.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ValidationAuthError(
                message="Profile data conflicts with existing data",
                details={"field": "national_id"},
            ) from exc

        self.repo.refresh(profile)

        return self._profile_out(profile)

    def create_my_document(
        self,
        *,
        user: AuthUser,
        payload: DocumentCreateIn,
    ) -> DocumentOut:
        self._validate_document_payload(payload)

        document = self.repo.create_document(
            user_id=user.id,
            document_type=payload.document_type,
            file_path=payload.file_path,
            file_name=payload.file_name,
            mime_type=payload.mime_type,
            size_bytes=payload.size_bytes,
            status=DocumentStatus.PENDING.value,
        )

        self.repo.commit()
        self.repo.refresh(document)

        return self._document_out(document)

    def list_my_documents(self, user: AuthUser) -> list[DocumentOut]:
        documents = self.repo.list_user_documents(user_id=user.id)
        return [self._document_out(item) for item in documents]

    def get_my_document(
        self,
        *,
        user: AuthUser,
        document_id: int,
    ) -> DocumentOut:
        document = self.repo.get_user_document(
            user_id=user.id,
            document_id=document_id,
        )

        if document is None:
            raise ValidationAuthError(
                message="Document not found",
                details={"document_id": document_id},
            )

        return self._document_out(document)

    def delete_my_document(
        self,
        *,
        user: AuthUser,
        document_id: int,
    ) -> None:
        document = self.repo.get_user_document(
            user_id=user.id,
            document_id=document_id,
        )

        if document is None:
            raise ValidationAuthError(
                message="Document not found",
                details={"document_id": document_id},
            )

        document.deleted_at = datetime.utcnow()
        self.repo.commit()

    def _validate_payload(self, payload: ProfileUpdateIn) -> None:
        if payload.gender is not None:
            allowed_genders = {item.value for item in Gender}
            if payload.gender not in allowed_genders:
                raise ValidationAuthError(
                    message="Invalid gender",
                    details={"allowed": sorted(allowed_genders)},
                )

        if payload.national_id is not None:
            if not re.fullmatch(r"\d{10}", payload.national_id):
                raise ValidationAuthError(
                    message="Invalid national_id",
                    details={"format": "10 digits"},
                )

        if payload.postal_code is not None:
            if not re.fullmatch(r"\d{10}", payload.postal_code):
                raise ValidationAuthError(
                    message="Invalid postal_code",
                    details={"format": "10 digits"},
                )

    def _validate_geo_consistency(self, payload: ProfileUpdateIn) -> None:
        province = None
        county = None
        district = None
        rural_district = None
        city = None
        village = None

        if payload.province_id is not None:
            province = self.repo.get_province(payload.province_id)
            if province is None:
                raise ValidationAuthError(
                    message="Invalid province_id",
                    details={"province_id": payload.province_id},
                )

        if payload.county_id is not None:
            county = self.repo.get_county(payload.county_id)
            if county is None:
                raise ValidationAuthError(
                    message="Invalid county_id",
                    details={"county_id": payload.county_id},
                )

            if payload.province_id is not None and county.province_id != payload.province_id:
                raise ValidationAuthError(
                    message="county_id does not belong to province_id",
                    details={
                        "province_id": payload.province_id,
                        "county_id": payload.county_id,
                    },
                )

        if payload.district_id is not None:
            district = self.repo.get_district(payload.district_id)
            if district is None:
                raise ValidationAuthError(
                    message="Invalid district_id",
                    details={"district_id": payload.district_id},
                )

            if payload.province_id is not None and district.province_id != payload.province_id:
                raise ValidationAuthError(
                    message="district_id does not belong to province_id",
                    details={
                        "province_id": payload.province_id,
                        "district_id": payload.district_id,
                    },
                )

            if payload.county_id is not None and district.county_id != payload.county_id:
                raise ValidationAuthError(
                    message="district_id does not belong to county_id",
                    details={
                        "county_id": payload.county_id,
                        "district_id": payload.district_id,
                    },
                )

        if payload.rural_district_id is not None:
            rural_district = self.repo.get_rural_district(payload.rural_district_id)
            if rural_district is None:
                raise ValidationAuthError(
                    message="Invalid rural_district_id",
                    details={"rural_district_id": payload.rural_district_id},
                )

            if (
                payload.province_id is not None
                and rural_district.province_id != payload.province_id
            ):
                raise ValidationAuthError(
                    message="rural_district_id does not belong to province_id",
                    details={
                        "province_id": payload.province_id,
                        "rural_district_id": payload.rural_district_id,
                    },
                )

            if (
                payload.county_id is not None
                and rural_district.county_id != payload.county_id
            ):
                raise ValidationAuthError(
                    message="rural_district_id does not belong to county_id",
                    details={
                        "county_id": payload.county_id,
                        "rural_district_id": payload.rural_district_id,
                    },
                )

            if (
                payload.district_id is not None
                and rural_district.district_id != payload.district_id
            ):
                raise ValidationAuthError(
                    message="rural_district_id does not belong to district_id",
                    details={
                        "district_id": payload.district_id,
                        "rural_district_id": payload.rural_district_id,
                    },
                )

        if payload.city_id is not None:
            city = self.repo.get_city(payload.city_id)
            if city is None:
                raise ValidationAuthError(
                    message="Invalid city_id",
                    details={"city_id": payload.city_id},
                )

            if payload.province_id is not None and city.province_id != payload.province_id:
                raise ValidationAuthError(
                    message="city_id does not belong to province_id",
                    details={
                        "province_id": payload.province_id,
                        "city_id": payload.city_id,
                    },
                )

            if payload.county_id is not None and city.county_id != payload.county_id:
                raise ValidationAuthError(
                    message="city_id does not belong to county_id",
                    details={
                        "county_id": payload.county_id,
                        "city_id": payload.city_id,
                    },
                )

        if payload.village_id is not None:
            village = self.repo.get_village(payload.village_id)
            if village is None:
                raise ValidationAuthError(
                    message="Invalid village_id",
                    details={"village_id": payload.village_id},
                )

            if payload.province_id is not None and village.province_id != payload.province_id:
                raise ValidationAuthError(
                    message="village_id does not belong to province_id",
                    details={
                        "province_id": payload.province_id,
                        "village_id": payload.village_id,
                    },
                )

            if payload.county_id is not None and village.county_id != payload.county_id:
                raise ValidationAuthError(
                    message="village_id does not belong to county_id",
                    details={
                        "county_id": payload.county_id,
                        "village_id": payload.village_id,
                    },
                )

            if (
                payload.rural_district_id is not None
                and village.rural_district_id != payload.rural_district_id
            ):
                raise ValidationAuthError(
                    message="village_id does not belong to rural_district_id",
                    details={
                        "rural_district_id": payload.rural_district_id,
                        "village_id": payload.village_id,
                    },
                )

        _ = (province, county, district, rural_district, city, village)

    def _validate_document_payload(self, payload: DocumentCreateIn) -> None:
        allowed_document_types = {item.value for item in DocumentType}

        if payload.document_type not in allowed_document_types:
            raise ValidationAuthError(
                message="Invalid document_type",
                details={"allowed": sorted(allowed_document_types)},
            )

        if payload.mime_type is not None:
            if not (
                payload.mime_type.startswith("image/")
                or payload.mime_type == "application/pdf"
            ):
                raise ValidationAuthError(
                    message="Invalid mime_type",
                    details={"allowed": ["image/*", "application/pdf"]},
                )

        if payload.size_bytes is not None:
            max_size = 15 * 1024 * 1024

            if payload.size_bytes > max_size:
                raise ValidationAuthError(
                    message="Document file is too large",
                    details={"max_size_bytes": max_size},
                )

    def _profile_out(self, profile: UserProfile) -> ProfileMeOut:
        return ProfileMeOut(
            id=profile.id,
            user_id=profile.user_id,
            first_name=profile.first_name,
            last_name=profile.last_name,
            display_name=profile.display_name,
            national_id=profile.national_id,
            birth_date=profile.birth_date,
            gender=profile.gender,
            province_id=profile.province_id,
            county_id=profile.county_id,
            district_id=profile.district_id,
            rural_district_id=profile.rural_district_id,
            city_id=profile.city_id,
            village_id=profile.village_id,
            address=profile.address,
            postal_code=profile.postal_code,
            avatar_file_id=profile.avatar_file_id,
            bio=profile.bio,
            profile_completed=self._is_profile_completed(profile),
        )

    def _is_profile_completed(self, profile: UserProfile) -> bool:
        has_name = bool(profile.first_name and profile.last_name)
        has_location = bool(profile.province_id and profile.county_id)
        has_address = bool(profile.address)

        return has_name and has_location and has_address

    def _document_out(self, document: UserDocument) -> DocumentOut:
        return DocumentOut(
            id=document.id,
            user_id=document.user_id,
            document_type=document.document_type,
            file_path=document.file_path,
            file_name=document.file_name,
            mime_type=document.mime_type,
            size_bytes=document.size_bytes,
            status=document.status,
            uploaded_at=document.uploaded_at,
            reviewed_at=document.reviewed_at,
            reviewed_by=document.reviewed_by,
            reject_reason=document.reject_reason,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )

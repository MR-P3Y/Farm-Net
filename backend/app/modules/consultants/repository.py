from __future__ import annotations

from sqlalchemy import or_, text
from sqlalchemy.orm import Session, joinedload

from app.common.search import normalize_search_text
from app.common.search_sql import search_match_expression, search_relevance_expression
from app.modules.auth.models import AuthRole, AuthUser
from app.modules.consultants.enums import ConsultantDiscoverySort
from app.modules.consultants.models import (
    ConsultProfile,
    ConsultProfileSpecialty,
    ConsultRequest,
    ConsultRequestStatusLog,
    ConsultSpecialty,
)
from app.modules.media.models import MediaFile
from app.modules.profiles.models import UserProfile


class ConsultantRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add_specialty(self, row: ConsultSpecialty) -> ConsultSpecialty:
        self.db.add(row)
        self.db.flush()
        return row

    def get_specialty_by_id(self, specialty_id: int) -> ConsultSpecialty | None:
        return (
            self.db.query(ConsultSpecialty)
            .filter(ConsultSpecialty.id == specialty_id)
            .one_or_none()
        )

    def get_specialty_by_code(self, code: str) -> ConsultSpecialty | None:
        return (
            self.db.query(ConsultSpecialty)
            .filter(ConsultSpecialty.code == code)
            .one_or_none()
        )

    def list_specialties(
        self,
        *,
        active_only: bool = False,
        q: str | None = None,
    ) -> list[ConsultSpecialty]:
        query = self.db.query(ConsultSpecialty)

        if active_only:
            query = query.filter(ConsultSpecialty.is_active.is_(True))

        if q:
            like = f"%{q.strip()}%"
            query = query.filter(
                or_(
                    ConsultSpecialty.code.ilike(like),
                    ConsultSpecialty.title.ilike(like),
                    ConsultSpecialty.description.ilike(like),
                )
            )

        return (
            query.order_by(
                ConsultSpecialty.sort_order.asc(),
                ConsultSpecialty.title.asc(),
                ConsultSpecialty.id.asc(),
            )
            .all()
        )

    def specialty_usage_counts(self, specialty_id: int) -> tuple[int, int]:
        profiles = self.db.query(ConsultProfileSpecialty).filter(ConsultProfileSpecialty.specialty_id == specialty_id).count()
        requests = self.db.query(ConsultRequest).filter(ConsultRequest.specialty_id == specialty_id).count()
        return profiles, requests

    def add_profile(self, row: ConsultProfile) -> ConsultProfile:
        self.db.add(row)
        self.db.flush()
        return row

    def get_profile_by_id(self, profile_id: int) -> ConsultProfile | None:
        return (
            self.db.query(ConsultProfile)
            .options(
                joinedload(ConsultProfile.specialty_links).joinedload(
                    ConsultProfileSpecialty.specialty
                )
            )
            .filter(ConsultProfile.id == profile_id)
            .one_or_none()
        )

    def get_profile_by_user_id(self, user_id: int) -> ConsultProfile | None:
        return (
            self.db.query(ConsultProfile)
            .options(
                joinedload(ConsultProfile.specialty_links).joinedload(
                    ConsultProfileSpecialty.specialty
                )
            )
            .filter(
                ConsultProfile.user_id == user_id,
                ConsultProfile.deleted_at.is_(None),
            )
            .one_or_none()
        )

    def list_profiles(
        self,
        *,
        public_only: bool = False,
        status: str | None = None,
        specialty_id: int | None = None,
        q: str | None = None,
        province_id: int | None = None,
        city_id: int | None = None,
        sort: ConsultantDiscoverySort | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ConsultProfile], int]:
        query = (
            self.db.query(ConsultProfile)
            .options(
                joinedload(ConsultProfile.specialty_links).joinedload(
                    ConsultProfileSpecialty.specialty
                )
            )
            .filter(ConsultProfile.deleted_at.is_(None))
        )

        if public_only:
            query = query.filter(ConsultProfile.status == "approved")
        elif status:
            query = query.filter(ConsultProfile.status == status)

        if province_id is not None:
            query = query.filter(ConsultProfile.province_id == province_id)

        if city_id is not None:
            query = query.filter(ConsultProfile.city_id == city_id)

        if specialty_id is not None:
            query = query.join(ConsultProfileSpecialty).filter(
                ConsultProfileSpecialty.specialty_id == specialty_id
            )

        normalized_q = normalize_search_text(q) if q else None
        if normalized_q:
            query = query.filter(
                or_(
                    search_match_expression(
                        normalized_q,
                        ConsultProfile.display_name,
                        ConsultProfile.title,
                        ConsultProfile.bio,
                        ConsultProfile.province_name,
                        ConsultProfile.city_name,
                    ),
                    ConsultProfile.specialty_links.any(
                        ConsultProfileSpecialty.specialty.has(
                            search_match_expression(
                                normalized_q,
                                ConsultSpecialty.code,
                                ConsultSpecialty.title,
                                ConsultSpecialty.description,
                            )
                        )
                    ),
                )
            )

        total = query.count()

        if sort == ConsultantDiscoverySort.RELEVANCE and normalized_q:
            ordering = (
                search_relevance_expression(
                    normalized_q,
                    ConsultProfile.display_name,
                    ConsultProfile.title,
                    ConsultProfile.bio,
                    ConsultProfile.province_name,
                    ConsultProfile.city_name,
                ).desc(),
                ConsultProfile.is_featured.desc(),
                ConsultProfile.rating_average.desc(),
                ConsultProfile.id.desc(),
            )
        elif sort == ConsultantDiscoverySort.NEWEST:
            ordering = (ConsultProfile.created_at.desc(), ConsultProfile.id.desc())
        else:
            ordering = (
                ConsultProfile.is_featured.desc(),
                ConsultProfile.rating_average.desc(),
                ConsultProfile.reviews_count.desc(),
                ConsultProfile.created_at.desc(),
                ConsultProfile.id.desc(),
            )
        rows = (
            query.order_by(*ordering)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return rows, total

    def replace_profile_specialties(
        self,
        *,
        profile: ConsultProfile,
        specialty_ids: list[int],
    ) -> None:
        existing = {
            link.specialty_id: link
            for link in self.db.query(ConsultProfileSpecialty)
            .filter(ConsultProfileSpecialty.profile_id == profile.id)
            .all()
        }
        wanted = set(specialty_ids)

        for specialty_id, link in existing.items():
            if specialty_id not in wanted:
                self.db.delete(link)

        for specialty_id in wanted:
            if specialty_id not in existing:
                self.db.add(
                    ConsultProfileSpecialty(
                        profile_id=profile.id,
                        specialty_id=specialty_id,
                    )
                )

        self.db.flush()

    def add_request(self, row: ConsultRequest) -> ConsultRequest:
        self.db.add(row)
        self.db.flush()
        return row

    def get_request_by_id(self, request_id: int) -> ConsultRequest | None:
        return (
            self.db.query(ConsultRequest)
            .options(
                joinedload(ConsultRequest.consultant_profile).joinedload(
                    ConsultProfile.specialty_links
                ).joinedload(ConsultProfileSpecialty.specialty),
                joinedload(ConsultRequest.specialty),
                joinedload(ConsultRequest.status_logs),
            )
            .filter(
                ConsultRequest.id == request_id,
                ConsultRequest.deleted_at.is_(None),
            )
            .one_or_none()
        )

    def list_requests(
        self,
        *,
        requester_user_id: int | None = None,
        consultant_profile_id: int | None = None,
        specialty_id: int | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ConsultRequest], int]:
        query = (
            self.db.query(ConsultRequest)
            .options(
                joinedload(ConsultRequest.consultant_profile).joinedload(
                    ConsultProfile.specialty_links
                ).joinedload(ConsultProfileSpecialty.specialty),
                joinedload(ConsultRequest.specialty),
                joinedload(ConsultRequest.status_logs),
            )
            .filter(ConsultRequest.deleted_at.is_(None))
        )

        if requester_user_id is not None:
            query = query.filter(ConsultRequest.requester_user_id == requester_user_id)

        if consultant_profile_id is not None:
            query = query.filter(ConsultRequest.consultant_profile_id == consultant_profile_id)

        if specialty_id is not None:
            query = query.filter(ConsultRequest.specialty_id == specialty_id)

        if status:
            query = query.filter(ConsultRequest.status == status)

        total = query.count()

        rows = (
            query.order_by(ConsultRequest.created_at.desc(), ConsultRequest.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return rows, total

    def add_request_status_log(self, row: ConsultRequestStatusLog) -> ConsultRequestStatusLog:
        self.db.add(row)
        self.db.flush()
        return row

    def get_user_by_id(self, user_id: int) -> AuthUser | None:
        return self.db.query(AuthUser).filter(AuthUser.id == user_id).one_or_none()

    def get_auth_role_by_code(self, code: str) -> AuthRole | None:
        return self.db.query(AuthRole).filter(AuthRole.code == code).one_or_none()

    def get_user_profile(self, user_id: int) -> UserProfile | None:
        return (
            self.db.query(UserProfile)
            .filter(UserProfile.user_id == user_id)
            .one_or_none()
        )

    def get_media_file_by_id(self, media_file_id: int) -> MediaFile | None:
        return self.db.query(MediaFile).filter(MediaFile.id == media_file_id).one_or_none()

    def list_consultant_admin_recipient_user_ids(self) -> list[int]:
        rows = self.db.execute(
            text(
                """
                SELECT DISTINCT u.id
                FROM auth_users u
                JOIN auth_user_roles ur ON ur.user_id = u.id
                JOIN auth_roles r ON r.id = ur.role_id
                WHERE r.code IN ('admin', 'super_admin', 'verification_admin', 'content_manager')
                ORDER BY u.id
                """
            )
        ).fetchall()

        return [int(row[0]) for row in rows]

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    def refresh(self, row) -> None:
        self.db.refresh(row)

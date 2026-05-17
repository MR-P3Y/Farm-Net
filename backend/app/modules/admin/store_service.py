from datetime import datetime

from sqlalchemy.orm import Session

from app.modules.admin.schemas import (
    AdminStoreMemberOut,
    AdminStoreOut,
    AdminStoreStatusHistoryOut,
)
from app.modules.auth.exceptions import ValidationAuthError
from app.modules.auth.models import AuthUser
from app.modules.auth.repository import AuthRepository
from app.modules.stores.enums import StoreStatus
from app.modules.stores.models import Store
from app.modules.stores.repository import StoreRepository


class AdminStoreService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.store_repo = StoreRepository(db)
        self.auth_repo = AuthRepository(db)

    def list_stores(
        self,
        *,
        page: int,
        page_size: int,
        status: str | None = None,
        owner_user_id: int | None = None,
        q: str | None = None,
    ) -> tuple[list[AdminStoreOut], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        if status is not None:
            self._validate_status_filter(status)

        items, total = self.store_repo.list_stores(
            status=status,
            owner_user_id=owner_user_id,
            q=q,
            page=page,
            page_size=page_size,
        )

        return [self._store_out(item) for item in items], total

    def get_store_detail(
        self,
        *,
        store_id: int,
    ) -> AdminStoreOut:
        store = self.store_repo.get_store_by_id(store_id=store_id)

        if store is None:
            raise ValidationAuthError(
                message="Store not found",
                details={"store_id": store_id},
            )

        return self._store_out(store)

    def update_store_status(
        self,
        *,
        store_id: int,
        status: str,
        note: str | None,
        reviewer: AuthUser,
    ) -> AdminStoreOut:
        self._validate_admin_target_status(status)

        store = self.store_repo.get_store_by_id(store_id=store_id)

        if store is None:
            raise ValidationAuthError(
                message="Store not found",
                details={"store_id": store_id},
            )

        self._validate_status_transition(
            current_status=store.status,
            next_status=status,
        )

        old_status = store.status
        now = datetime.utcnow()

        store.status = status
        store.admin_note = note

        if status == StoreStatus.APPROVED.value:
            store.approved_at = now
            store.approved_by = reviewer.id

        if status == StoreStatus.REJECTED.value:
            store.rejected_at = now
            store.rejected_by = reviewer.id

        self.store_repo.create_status_history(
            store_id=store.id,
            changed_by=reviewer.id,
            from_status=old_status,
            to_status=status,
            note=note,
        )

        self.store_repo.commit()
        self.store_repo.refresh(store)

        return self._store_out(store)

    def _validate_status_filter(self, status: str) -> None:
        allowed = {item.value for item in StoreStatus}

        if status not in allowed:
            raise ValidationAuthError(
                message="Invalid store status filter",
                details={"allowed": sorted(allowed)},
            )

    def _validate_admin_target_status(self, status: str) -> None:
        allowed = {
            StoreStatus.APPROVED.value,
            StoreStatus.REJECTED.value,
            StoreStatus.SUSPENDED.value,
        }

        if status not in allowed:
            raise ValidationAuthError(
                message="Invalid admin store status",
                details={"allowed": sorted(allowed)},
            )

    def _validate_status_transition(
        self,
        *,
        current_status: str,
        next_status: str,
    ) -> None:
        allowed_transitions = {
            StoreStatus.PENDING_REVIEW.value: {
                StoreStatus.APPROVED.value,
                StoreStatus.REJECTED.value,
            },
            StoreStatus.APPROVED.value: {
                StoreStatus.SUSPENDED.value,
            },
            StoreStatus.SUSPENDED.value: {
                StoreStatus.APPROVED.value,
            },
        }

        allowed_next = allowed_transitions.get(current_status, set())

        if next_status not in allowed_next:
            raise ValidationAuthError(
                message="Invalid store status transition",
                details={
                    "current_status": current_status,
                    "next_status": next_status,
                    "allowed_next": sorted(allowed_next),
                },
            )

    def _store_out(self, store: Store) -> AdminStoreOut:
        owner = self.auth_repo.get_user_by_id(store.owner_user_id)
        history_rows = self.store_repo.list_status_history(store_id=store.id)

        return AdminStoreOut(
            id=store.id,
            owner_user_id=store.owner_user_id,
            owner_email=owner.email if owner else None,
            owner_phone=owner.phone if owner else None,
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
            latitude=str(store.latitude) if store.latitude is not None else None,
            longitude=str(store.longitude) if store.longitude is not None else None,
            logo_file_id=store.logo_file_id,
            banner_file_id=store.banner_file_id,
            admin_note=store.admin_note,
            approved_at=store.approved_at,
            approved_by=store.approved_by,
            rejected_at=store.rejected_at,
            rejected_by=store.rejected_by,
            created_at=store.created_at,
            updated_at=store.updated_at,
            members=[
                AdminStoreMemberOut(
                    id=member.id,
                    store_id=member.store_id,
                    user_id=member.user_id,
                    role=member.role,
                    status=member.status,
                    invited_by=member.invited_by,
                    joined_at=member.joined_at,
                    created_at=member.created_at,
                    updated_at=member.updated_at,
                )
                for member in store.members
            ],
            status_history=[
                AdminStoreStatusHistoryOut(
                    id=row.id,
                    store_id=row.store_id,
                    changed_by=row.changed_by,
                    from_status=row.from_status,
                    to_status=row.to_status,
                    note=row.note,
                    created_at=row.created_at,
                )
                for row in history_rows
            ],
        )

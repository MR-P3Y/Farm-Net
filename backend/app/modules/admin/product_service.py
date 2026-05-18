from datetime import datetime

from sqlalchemy.orm import Session

from app.modules.admin.schemas import (
    AdminProductImageOut,
    AdminProductOut,
    AdminProductStatusHistoryOut,
)
from app.modules.auth.exceptions import ValidationAuthError
from app.modules.auth.models import AuthUser
from app.modules.auth.repository import AuthRepository
from app.modules.products.enums import ProductStatus
from app.modules.products.models import StoreProduct
from app.modules.products.repository import ProductRepository
from app.modules.stores.repository import StoreRepository


class AdminProductService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.product_repo = ProductRepository(db)
        self.store_repo = StoreRepository(db)
        self.auth_repo = AuthRepository(db)

    def list_products(
        self,
        *,
        page: int,
        page_size: int,
        status: str | None = None,
        store_id: int | None = None,
        category_id: int | None = None,
        q: str | None = None,
    ) -> tuple[list[AdminProductOut], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        if status is not None:
            self._validate_status_filter(status)

        items, total = self.product_repo.list_products_for_admin(
            status=status,
            store_id=store_id,
            category_id=category_id,
            q=q,
            page=page,
            page_size=page_size,
        )

        return [self._product_out(item) for item in items], total

    def get_product_detail(self, *, product_id: int) -> AdminProductOut:
        product = self.product_repo.get_product_for_admin(product_id=product_id)

        if product is None:
            raise ValidationAuthError(
                message="Product not found",
                details={"product_id": product_id},
            )

        return self._product_out(product)

    def update_product_status(
        self,
        *,
        product_id: int,
        status: str,
        note: str | None,
        reviewer: AuthUser,
    ) -> AdminProductOut:
        self._validate_admin_target_status(status)

        product = self.product_repo.get_product_for_admin(product_id=product_id)

        if product is None:
            raise ValidationAuthError(
                message="Product not found",
                details={"product_id": product_id},
            )

        self._validate_status_transition(
            current_status=product.status,
            next_status=status,
        )

        old_status = product.status
        product.status = status
        product.admin_note = note

        now = datetime.utcnow()

        if status == ProductStatus.SUSPENDED.value:
            product.suspended_at = now
            product.suspended_by = reviewer.id

        if old_status == ProductStatus.SUSPENDED.value and status in {
            ProductStatus.PUBLISHED.value,
            ProductStatus.UNPUBLISHED.value,
        }:
            product.suspended_at = None
            product.suspended_by = None

        self.product_repo.create_status_history(
            product_id=product.id,
            changed_by=reviewer.id,
            from_status=old_status,
            to_status=status,
            note=note,
        )

        self.product_repo.commit()
        self.product_repo.refresh(product)

        return self._product_out(product)

    def _validate_status_filter(self, status: str) -> None:
        allowed = {item.value for item in ProductStatus}

        if status not in allowed:
            raise ValidationAuthError(
                message="Invalid product status filter",
                details={"allowed": sorted(allowed)},
            )

    def _validate_admin_target_status(self, status: str) -> None:
        allowed = {
            ProductStatus.SUSPENDED.value,
            ProductStatus.PUBLISHED.value,
            ProductStatus.UNPUBLISHED.value,
        }

        if status not in allowed:
            raise ValidationAuthError(
                message="Invalid admin product status",
                details={"allowed": sorted(allowed)},
            )

    def _validate_status_transition(
        self,
        *,
        current_status: str,
        next_status: str,
    ) -> None:
        allowed_transitions = {
            ProductStatus.PUBLISHED.value: {
                ProductStatus.SUSPENDED.value,
            },
            ProductStatus.UNPUBLISHED.value: {
                ProductStatus.SUSPENDED.value,
            },
            ProductStatus.SUSPENDED.value: {
                ProductStatus.PUBLISHED.value,
                ProductStatus.UNPUBLISHED.value,
            },
        }

        allowed_next = allowed_transitions.get(current_status, set())

        if next_status not in allowed_next:
            raise ValidationAuthError(
                message="Invalid product status transition",
                details={
                    "current_status": current_status,
                    "next_status": next_status,
                    "allowed_next": sorted(allowed_next),
                },
            )

    def _product_out(self, product: StoreProduct) -> AdminProductOut:
        store = self.store_repo.get_store_by_id(store_id=product.store_id)
        owner = None

        if store is not None:
            owner = self.auth_repo.get_user_by_id(store.owner_user_id)

        history_rows = self.product_repo.list_status_history(product_id=product.id)
        images = self.product_repo.list_product_images(product_id=product.id)

        category_name = product.category.name if product.category else None
        category_slug = product.category.slug if product.category else None

        return AdminProductOut(
            id=product.id,
            store_id=product.store_id,
            store_name=store.name if store else None,
            store_slug=store.slug if store else None,
            owner_user_id=store.owner_user_id if store else None,
            owner_email=owner.email if owner else None,
            owner_phone=owner.phone if owner else None,
            category_id=product.category_id,
            category_name=category_name,
            category_slug=category_slug,
            name=product.name,
            slug=product.slug,
            short_description=product.short_description,
            description=product.description,
            sku=product.sku,
            status=product.status,
            price=product.price,
            compare_at_price=product.compare_at_price,
            currency=product.currency,
            stock_quantity=product.stock_quantity,
            unit=product.unit,
            min_order_quantity=product.min_order_quantity,
            max_order_quantity=product.max_order_quantity,
            is_active=product.is_active,
            is_featured=product.is_featured,
            admin_note=product.admin_note,
            suspended_at=product.suspended_at,
            suspended_by=product.suspended_by,
            created_at=product.created_at,
            updated_at=product.updated_at,
            deleted_at=product.deleted_at,
            images=[
                AdminProductImageOut(
                    id=image.id,
                    product_id=image.product_id,
                    file_id=image.file_id,
                    file_path=image.file_path,
                    alt_text=image.alt_text,
                    sort_order=image.sort_order,
                    is_primary=image.is_primary,
                    created_at=image.created_at,
                    updated_at=image.updated_at,
                )
                for image in images
            ],
            status_history=[
                AdminProductStatusHistoryOut(
                    id=row.id,
                    product_id=row.product_id,
                    changed_by=row.changed_by,
                    from_status=row.from_status,
                    to_status=row.to_status,
                    note=row.note,
                    created_at=row.created_at,
                )
                for row in history_rows
            ],
        )

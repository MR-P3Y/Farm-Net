import re
from datetime import datetime
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.exceptions import ValidationAuthError
from app.modules.auth.models import AuthUser
from app.modules.products.enums import ProductStatus, ProductUnit
from app.modules.products.models import ProductStatusHistory, StoreProduct
from app.modules.products.repository import ProductRepository
from app.modules.products.schemas import (
    ProductCreateIn,
    ProductOut,
    ProductStatusHistoryOut,
    ProductUpdateIn,
)
from app.modules.stores.enums import StoreStatus


class ProductService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ProductRepository(db)

    def create_product(
        self,
        *,
        user: AuthUser,
        store_id: int,
        payload: ProductCreateIn,
    ) -> ProductOut:
        store = self._get_owned_approved_store(user=user, store_id=store_id)

        self._validate_payload_common(
            slug=payload.slug,
            unit=payload.unit,
            currency=payload.currency,
            price=payload.price,
            compare_at_price=payload.compare_at_price,
            stock_quantity=payload.stock_quantity,
            min_order_quantity=payload.min_order_quantity,
            max_order_quantity=payload.max_order_quantity,
        )
        self._validate_category(payload.category_id)

        self._ensure_slug_available(
            store_id=store.id,
            slug=payload.slug,
            current_product_id=None,
        )
        self._ensure_sku_available(
            store_id=store.id,
            sku=payload.sku,
            current_product_id=None,
        )

        product = self.repo.create_product(
            store_id=store.id,
            category_id=payload.category_id,
            name=payload.name,
            slug=payload.slug,
            short_description=payload.short_description,
            description=payload.description,
            sku=payload.sku,
            status=ProductStatus.DRAFT.value,
            price=payload.price,
            compare_at_price=payload.compare_at_price,
            currency=payload.currency,
            stock_quantity=payload.stock_quantity,
            unit=payload.unit,
            min_order_quantity=payload.min_order_quantity,
            max_order_quantity=payload.max_order_quantity,
            is_active=payload.is_active,
            is_featured=payload.is_featured,
        )

        self.repo.create_status_history(
            product_id=product.id,
            changed_by=user.id,
            from_status=None,
            to_status=ProductStatus.DRAFT.value,
            note="Product created as draft",
        )

        try:
            self.repo.commit()
        except IntegrityError as exc:
            self.repo.rollback()
            raise ValidationAuthError(
                message="Product data conflicts with existing data",
                details={"fields": ["slug", "sku"]},
            ) from exc

        self.repo.refresh(product)
        return self._product_out(product)

    def list_my_products(
        self,
        *,
        user: AuthUser,
        store_id: int,
        status: str | None,
        category_id: int | None,
        q: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[ProductOut], int]:
        store = self._get_owned_store(user=user, store_id=store_id)

        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        if status is not None:
            self._validate_status_filter(status)

        if category_id is not None:
            self._validate_category(category_id)

        items, total = self.repo.list_store_products(
            store_id=store.id,
            status=status,
            category_id=category_id,
            q=q,
            page=page,
            page_size=page_size,
        )

        return [self._product_out(item) for item in items], total

    def get_my_product(
        self,
        *,
        user: AuthUser,
        store_id: int,
        product_id: int,
    ) -> ProductOut:
        self._get_owned_store(user=user, store_id=store_id)
        product = self._get_store_product(store_id=store_id, product_id=product_id)
        return self._product_out(product)

    def update_product(
        self,
        *,
        user: AuthUser,
        store_id: int,
        product_id: int,
        payload: ProductUpdateIn,
    ) -> ProductOut:
        store = self._get_owned_approved_store(user=user, store_id=store_id)
        product = self._get_store_product(store_id=store.id, product_id=product_id)

        if product.status in {
            ProductStatus.SUSPENDED.value,
            ProductStatus.ARCHIVED.value,
        }:
            raise ValidationAuthError(
                message="Product cannot be updated in current status",
                details={"current_status": product.status},
            )

        next_slug = payload.slug if payload.slug is not None else product.slug
        next_unit = payload.unit if payload.unit is not None else product.unit
        next_currency = payload.currency if payload.currency is not None else product.currency
        next_price = payload.price if payload.price is not None else product.price
        next_compare_at_price = (
            payload.compare_at_price
            if payload.compare_at_price is not None
            else product.compare_at_price
        )
        next_stock_quantity = (
            payload.stock_quantity
            if payload.stock_quantity is not None
            else product.stock_quantity
        )
        next_min_order_quantity = (
            payload.min_order_quantity
            if payload.min_order_quantity is not None
            else product.min_order_quantity
        )
        next_max_order_quantity = (
            payload.max_order_quantity
            if payload.max_order_quantity is not None
            else product.max_order_quantity
        )

        self._validate_payload_common(
            slug=next_slug,
            unit=next_unit,
            currency=next_currency,
            price=next_price,
            compare_at_price=next_compare_at_price,
            stock_quantity=next_stock_quantity,
            min_order_quantity=next_min_order_quantity,
            max_order_quantity=next_max_order_quantity,
        )
        self._validate_category(payload.category_id)

        self._ensure_slug_available(
            store_id=store.id,
            slug=next_slug,
            current_product_id=product.id,
        )
        self._ensure_sku_available(
            store_id=store.id,
            sku=payload.sku if payload.sku is not None else product.sku,
            current_product_id=product.id,
        )

        if payload.category_id is not None:
            product.category_id = payload.category_id
        if payload.name is not None:
            product.name = payload.name
        if payload.slug is not None:
            product.slug = payload.slug
        if payload.short_description is not None:
            product.short_description = payload.short_description
        if payload.description is not None:
            product.description = payload.description
        if payload.sku is not None:
            product.sku = payload.sku
        if payload.price is not None:
            product.price = payload.price
        if payload.compare_at_price is not None:
            product.compare_at_price = payload.compare_at_price
        if payload.currency is not None:
            product.currency = payload.currency
        if payload.stock_quantity is not None:
            product.stock_quantity = payload.stock_quantity
        if payload.unit is not None:
            product.unit = payload.unit
        if payload.min_order_quantity is not None:
            product.min_order_quantity = payload.min_order_quantity
        if payload.max_order_quantity is not None:
            product.max_order_quantity = payload.max_order_quantity
        if payload.is_active is not None:
            product.is_active = payload.is_active
        if payload.is_featured is not None:
            product.is_featured = payload.is_featured

        try:
            self.repo.commit()
        except IntegrityError as exc:
            self.repo.rollback()
            raise ValidationAuthError(
                message="Product data conflicts with existing data",
                details={"fields": ["slug", "sku"]},
            ) from exc

        self.repo.refresh(product)
        return self._product_out(product)

    def publish_product(
        self,
        *,
        user: AuthUser,
        store_id: int,
        product_id: int,
    ) -> ProductOut:
        store = self._get_owned_approved_store(user=user, store_id=store_id)
        product = self._get_store_product(store_id=store.id, product_id=product_id)

        if product.status not in {
            ProductStatus.DRAFT.value,
            ProductStatus.UNPUBLISHED.value,
        }:
            raise ValidationAuthError(
                message="Product cannot be published in current status",
                details={"current_status": product.status},
            )

        self._validate_publish_ready(product)

        old_status = product.status
        product.status = ProductStatus.PUBLISHED.value

        self.repo.create_status_history(
            product_id=product.id,
            changed_by=user.id,
            from_status=old_status,
            to_status=ProductStatus.PUBLISHED.value,
            note="Product published by seller",
        )

        self.repo.commit()
        self.repo.refresh(product)

        return self._product_out(product)

    def unpublish_product(
        self,
        *,
        user: AuthUser,
        store_id: int,
        product_id: int,
    ) -> ProductOut:
        store = self._get_owned_approved_store(user=user, store_id=store_id)
        product = self._get_store_product(store_id=store.id, product_id=product_id)

        if product.status != ProductStatus.PUBLISHED.value:
            raise ValidationAuthError(
                message="Product cannot be unpublished in current status",
                details={"current_status": product.status},
            )

        old_status = product.status
        product.status = ProductStatus.UNPUBLISHED.value

        self.repo.create_status_history(
            product_id=product.id,
            changed_by=user.id,
            from_status=old_status,
            to_status=ProductStatus.UNPUBLISHED.value,
            note="Product unpublished by seller",
        )

        self.repo.commit()
        self.repo.refresh(product)

        return self._product_out(product)

    def archive_product(
        self,
        *,
        user: AuthUser,
        store_id: int,
        product_id: int,
    ) -> ProductOut:
        store = self._get_owned_approved_store(user=user, store_id=store_id)
        product = self._get_store_product(store_id=store.id, product_id=product_id)

        if product.status == ProductStatus.SUSPENDED.value:
            raise ValidationAuthError(
                message="Suspended product cannot be archived by seller",
                details={"current_status": product.status},
            )

        old_status = product.status
        product.status = ProductStatus.ARCHIVED.value
        product.deleted_at = datetime.utcnow()

        self.repo.create_status_history(
            product_id=product.id,
            changed_by=user.id,
            from_status=old_status,
            to_status=ProductStatus.ARCHIVED.value,
            note="Product archived by seller",
        )

        self.repo.commit()
        self.repo.refresh(product)

        return self._product_out(product)

    def list_product_status_history(
        self,
        *,
        user: AuthUser,
        store_id: int,
        product_id: int,
    ) -> list[ProductStatusHistoryOut]:
        self._get_owned_store(user=user, store_id=store_id)
        product = self._get_store_product(store_id=store_id, product_id=product_id)

        rows = self.repo.list_status_history(product_id=product.id)
        return [self._history_out(row) for row in rows]

    def _get_owned_store(self, *, user: AuthUser, store_id: int):
        store = self.repo.get_store_by_id(store_id=store_id)

        if store is None:
            raise ValidationAuthError(
                message="Store not found",
                details={"store_id": store_id},
            )

        if store.owner_user_id != user.id:
            raise ValidationAuthError(
                message="Store does not belong to current user",
                details={"store_id": store_id},
            )

        return store

    def _get_owned_approved_store(self, *, user: AuthUser, store_id: int):
        store = self._get_owned_store(user=user, store_id=store_id)

        if store.status != StoreStatus.APPROVED.value:
            raise ValidationAuthError(
                message="Store must be approved before managing products",
                details={"store_id": store.id, "store_status": store.status},
            )

        return store

    def _get_store_product(self, *, store_id: int, product_id: int) -> StoreProduct:
        product = self.repo.get_store_product_by_id(
            store_id=store_id,
            product_id=product_id,
        )

        if product is None:
            raise ValidationAuthError(
                message="Product not found",
                details={"product_id": product_id},
            )

        return product

    def _validate_category(self, category_id: int | None) -> None:
        if category_id is None:
            return

        category = self.repo.get_category_by_id(category_id=category_id)
        if category is None:
            raise ValidationAuthError(
                message="Invalid category_id",
                details={"category_id": category_id},
            )

    def _validate_payload_common(
        self,
        *,
        slug: str,
        unit: str,
        currency: str,
        price: Decimal,
        compare_at_price: Decimal | None,
        stock_quantity: int,
        min_order_quantity: int,
        max_order_quantity: int | None,
    ) -> None:
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,158}[a-z0-9]", slug):
            raise ValidationAuthError(
                message="Invalid product slug",
                details={
                    "format": "lowercase letters, numbers and dashes, 3-160 chars",
                },
            )

        allowed_units = {item.value for item in ProductUnit}
        if unit not in allowed_units:
            raise ValidationAuthError(
                message="Invalid product unit",
                details={"allowed": sorted(allowed_units)},
            )

        if currency != "TOMAN":
            raise ValidationAuthError(
                message="Invalid currency",
                details={"allowed": ["TOMAN"]},
            )

        if price <= 0:
            raise ValidationAuthError(
                message="Invalid product price",
                details={"price": "must be greater than zero"},
            )

        if compare_at_price is not None and compare_at_price <= price:
            raise ValidationAuthError(
                message="Invalid compare_at_price",
                details={"rule": "compare_at_price must be greater than price"},
            )

        if stock_quantity < 0:
            raise ValidationAuthError(
                message="Invalid stock_quantity",
                details={"stock_quantity": "must be zero or greater"},
            )

        if max_order_quantity is not None and max_order_quantity < min_order_quantity:
            raise ValidationAuthError(
                message="Invalid max_order_quantity",
                details={
                    "rule": "max_order_quantity must be greater than or equal to min_order_quantity",
                },
            )

    def _ensure_slug_available(
        self,
        *,
        store_id: int,
        slug: str,
        current_product_id: int | None,
    ) -> None:
        existing = self.repo.get_store_product_by_slug(store_id=store_id, slug=slug)

        if existing is not None and existing.id != current_product_id:
            raise ValidationAuthError(
                message="Product slug already exists in this store",
                details={"slug": slug},
            )

    def _ensure_sku_available(
        self,
        *,
        store_id: int,
        sku: str | None,
        current_product_id: int | None,
    ) -> None:
        if sku is None:
            return

        existing = self.repo.get_store_product_by_sku(store_id=store_id, sku=sku)

        if existing is not None and existing.id != current_product_id:
            raise ValidationAuthError(
                message="Product sku already exists in this store",
                details={"sku": sku},
            )

    def _validate_status_filter(self, status: str) -> None:
        allowed = {item.value for item in ProductStatus}

        if status not in allowed:
            raise ValidationAuthError(
                message="Invalid product status filter",
                details={"allowed": sorted(allowed)},
            )

    def _validate_publish_ready(self, product: StoreProduct) -> None:
        missing = []

        if not product.name:
            missing.append("name")
        if not product.slug:
            missing.append("slug")
        if product.price <= 0:
            missing.append("price")
        if product.stock_quantity < 0:
            missing.append("stock_quantity")

        if missing:
            raise ValidationAuthError(
                message="Product is not ready for publish",
                details={"missing": missing},
            )

    def _product_out(self, product: StoreProduct) -> ProductOut:
        return ProductOut(
            id=product.id,
            store_id=product.store_id,
            category_id=product.category_id,
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
            suspended_at=product.suspended_at.isoformat()
            if product.suspended_at
            else None,
            suspended_by=product.suspended_by,
            created_at=product.created_at.isoformat(),
            updated_at=product.updated_at.isoformat(),
        )

    def _history_out(self, row: ProductStatusHistory) -> ProductStatusHistoryOut:
        return ProductStatusHistoryOut(
            id=row.id,
            product_id=row.product_id,
            changed_by=row.changed_by,
            from_status=row.from_status,
            to_status=row.to_status,
            note=row.note,
            created_at=row.created_at.isoformat(),
        )
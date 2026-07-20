from decimal import Decimal

from sqlalchemy.orm import Session, joinedload

from app.common.money import CurrencyCode
from app.common.search import normalize_search_text
from app.common.search_sql import search_match_expression, search_relevance_expression

from app.modules.media.enums import MediaPurpose, MediaStatus, MediaVisibility
from app.modules.media.models import MediaFile
from app.modules.products.enums import ProductDiscoverySort
from app.modules.products.models import (
    ProductCategory,
    ProductImage,
    ProductStatusHistory,
    StoreProduct,
)
from app.modules.stores.models import Store


class ProductRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_store_by_id(self, *, store_id: int) -> Store | None:
        return (
            self.db.query(Store)
            .filter(
                Store.id == store_id,
                Store.deleted_at.is_(None),
            )
            .one_or_none()
        )

    def get_category_by_id(self, *, category_id: int) -> ProductCategory | None:
        return (
            self.db.query(ProductCategory)
            .filter(
                ProductCategory.id == category_id,
                ProductCategory.is_active.is_(True),
            )
            .one_or_none()
        )

    def get_category_for_admin(self, *, category_id: int) -> ProductCategory | None:
        return self.db.query(ProductCategory).filter(ProductCategory.id == category_id).one_or_none()

    def get_category_by_slug(self, *, slug: str) -> ProductCategory | None:
        return self.db.query(ProductCategory).filter(ProductCategory.slug == slug).one_or_none()

    def list_categories(self, *, active_only: bool, q: str | None = None) -> list[ProductCategory]:
        query = self.db.query(ProductCategory)
        if active_only:
            query = query.filter(ProductCategory.is_active.is_(True))
        if q:
            query = query.filter(ProductCategory.name.ilike(f"%{q}%"))
        return query.order_by(ProductCategory.parent_id.asc(), ProductCategory.sort_order.asc(), ProductCategory.name.asc()).all()

    def category_counts(self, *, category_id: int) -> tuple[int, int]:
        children = self.db.query(ProductCategory).filter(ProductCategory.parent_id == category_id).count()
        products = self.db.query(StoreProduct).filter(StoreProduct.category_id == category_id, StoreProduct.deleted_at.is_(None)).count()
        return children, products

    def create_category(self, **values) -> ProductCategory:
        row = ProductCategory(**values)
        self.db.add(row)
        self.db.flush()
        return row

    def get_product_by_id(self, *, product_id: int) -> StoreProduct | None:
        return (
            self.db.query(StoreProduct)
            .filter(
                StoreProduct.id == product_id,
                StoreProduct.deleted_at.is_(None),
            )
            .one_or_none()
        )

    def get_store_product_by_id(
        self,
        *,
        store_id: int,
        product_id: int,
    ) -> StoreProduct | None:
        return (
            self.db.query(StoreProduct)
            .filter(
                StoreProduct.id == product_id,
                StoreProduct.store_id == store_id,
                StoreProduct.deleted_at.is_(None),
            )
            .one_or_none()
        )

    def get_store_product_by_slug(
        self,
        *,
        store_id: int,
        slug: str,
    ) -> StoreProduct | None:
        return (
            self.db.query(StoreProduct)
            .filter(
                StoreProduct.store_id == store_id,
                StoreProduct.slug == slug,
                StoreProduct.deleted_at.is_(None),
            )
            .one_or_none()
        )

    def get_store_product_by_sku(
        self,
        *,
        store_id: int,
        sku: str,
    ) -> StoreProduct | None:
        return (
            self.db.query(StoreProduct)
            .filter(
                StoreProduct.store_id == store_id,
                StoreProduct.sku == sku,
                StoreProduct.deleted_at.is_(None),
            )
            .one_or_none()
        )

    def list_store_products(
        self,
        *,
        store_id: int,
        status: str | None = None,
        category_id: int | None = None,
        q: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[StoreProduct], int]:
        query = self.db.query(StoreProduct).filter(
            StoreProduct.store_id == store_id,
            StoreProduct.deleted_at.is_(None),
        )

        if status:
            query = query.filter(StoreProduct.status == status)

        if category_id:
            query = query.filter(StoreProduct.category_id == category_id)

        if q:
            pattern = f"%{q}%"
            query = query.filter(
                (StoreProduct.name.like(pattern))
                | (StoreProduct.slug.like(pattern))
                | (StoreProduct.sku.like(pattern))
            )

        total = query.count()

        items = (
            query.order_by(StoreProduct.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return items, total

    def list_products_for_admin(
        self,
        *,
        status: str | None = None,
        store_id: int | None = None,
        category_id: int | None = None,
        q: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[StoreProduct], int]:
        query = self.db.query(StoreProduct).filter(
            StoreProduct.deleted_at.is_(None),
        )

        if status:
            query = query.filter(StoreProduct.status == status)

        if store_id:
            query = query.filter(StoreProduct.store_id == store_id)

        if category_id:
            query = query.filter(StoreProduct.category_id == category_id)

        if q:
            pattern = f"%{q}%"
            query = query.filter(
                (StoreProduct.name.like(pattern))
                | (StoreProduct.slug.like(pattern))
                | (StoreProduct.sku.like(pattern))
            )

        total = query.count()

        items = (
            query.order_by(StoreProduct.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return items, total

    def get_product_for_admin(self, *, product_id: int) -> StoreProduct | None:
        return (
            self.db.query(StoreProduct)
            .filter(
                StoreProduct.id == product_id,
                StoreProduct.deleted_at.is_(None),
            )
            .one_or_none()
        )

    def list_public_products(
        self,
        *,
        q: str | None = None,
        store_id: int | None = None,
        category_id: int | None = None,
        province_id: int | None = None,
        county_id: int | None = None,
        city_id: int | None = None,
        store_type: str | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        sort: ProductDiscoverySort | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[StoreProduct], int]:
        query = (
            self.db.query(StoreProduct)
            .join(Store, Store.id == StoreProduct.store_id)
            .options(joinedload(StoreProduct.store))
            .filter(
                StoreProduct.status == "published",
                StoreProduct.deleted_at.is_(None),
                StoreProduct.is_active.is_(True),
                Store.status == "approved",
                Store.deleted_at.is_(None),
            )
        )

        normalized_q = normalize_search_text(q) if q else None
        if normalized_q:
            query = query.filter(
                search_match_expression(
                    normalized_q,
                    StoreProduct.name,
                    StoreProduct.slug,
                    StoreProduct.short_description,
                    StoreProduct.description,
                    Store.name,
                )
            )

        if store_id:
            query = query.filter(StoreProduct.store_id == store_id)

        if category_id:
            query = query.filter(StoreProduct.category_id.in_(self._category_scope(category_id)))

        if province_id:
            query = query.filter(Store.province_id == province_id)

        if county_id:
            query = query.filter(Store.county_id == county_id)

        if city_id:
            query = query.filter(Store.city_id == city_id)

        if store_type:
            query = query.filter(Store.store_type == store_type)

        if min_price is not None:
            query = query.filter(
                StoreProduct.currency == CurrencyCode.TOMAN.value,
                StoreProduct.price >= min_price,
            )

        if max_price is not None:
            query = query.filter(
                StoreProduct.currency == CurrencyCode.TOMAN.value,
                StoreProduct.price <= max_price,
            )

        total = query.count()

        if sort == ProductDiscoverySort.PRICE_ASC:
            ordering = (StoreProduct.price.asc(), StoreProduct.id.desc())
        elif sort == ProductDiscoverySort.PRICE_DESC:
            ordering = (StoreProduct.price.desc(), StoreProduct.id.desc())
        elif sort == ProductDiscoverySort.NEWEST:
            ordering = (StoreProduct.created_at.desc(), StoreProduct.id.desc())
        elif sort == ProductDiscoverySort.RELEVANCE and normalized_q:
            ordering = (
                search_relevance_expression(
                    normalized_q,
                    StoreProduct.name,
                    StoreProduct.slug,
                    StoreProduct.short_description,
                    StoreProduct.description,
                    Store.name,
                ).desc(),
                StoreProduct.is_featured.desc(),
                StoreProduct.created_at.desc(),
                StoreProduct.id.desc(),
            )
        else:
            ordering = (
                StoreProduct.is_featured.desc(),
                StoreProduct.created_at.desc(),
                StoreProduct.id.desc(),
            )

        items = (
            query.order_by(*ordering)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return items, total

    def _category_scope(self, category_id: int) -> set[int]:
        rows = self.db.query(ProductCategory.id, ProductCategory.parent_id).filter(
            ProductCategory.is_active.is_(True)
        ).all()
        children: dict[int, list[int]] = {}
        known_ids = set()
        for row_id, parent_id in rows:
            known_ids.add(row_id)
            if parent_id is not None:
                children.setdefault(parent_id, []).append(row_id)
        if category_id not in known_ids:
            return {category_id}
        scope = {category_id}
        pending = [category_id]
        while pending:
            for child_id in children.get(pending.pop(), []):
                if child_id not in scope:
                    scope.add(child_id)
                    pending.append(child_id)
        return scope

    def get_public_product_by_id(self, *, product_id: int) -> StoreProduct | None:
        return (
            self.db.query(StoreProduct)
            .join(Store, Store.id == StoreProduct.store_id)
            .filter(
                StoreProduct.id == product_id,
                StoreProduct.status == "published",
                StoreProduct.deleted_at.is_(None),
                StoreProduct.is_active.is_(True),
                Store.status == "approved",
                Store.deleted_at.is_(None),
            )
            .one_or_none()
        )

    def list_public_products_by_store_slug(
        self,
        *,
        store_slug: str,
        q: str | None = None,
        category_id: int | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[StoreProduct], int]:
        query = (
            self.db.query(StoreProduct)
            .join(Store, Store.id == StoreProduct.store_id)
            .filter(
                Store.slug == store_slug,
                Store.status == "approved",
                Store.deleted_at.is_(None),
                StoreProduct.status == "published",
                StoreProduct.deleted_at.is_(None),
                StoreProduct.is_active.is_(True),
            )
        )

        if q:
            pattern = f"%{q}%"
            query = query.filter(
                (StoreProduct.name.like(pattern))
                | (StoreProduct.slug.like(pattern))
                | (StoreProduct.short_description.like(pattern))
                | (StoreProduct.description.like(pattern))
            )

        if category_id:
            query = query.filter(StoreProduct.category_id == category_id)

        total = query.count()

        items = (
            query.order_by(
                StoreProduct.is_featured.desc(),
                StoreProduct.created_at.desc(),
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return items, total

    def get_public_product_by_store_and_slug(
        self,
        *,
        store_slug: str,
        product_slug: str,
    ) -> StoreProduct | None:
        return (
            self.db.query(StoreProduct)
            .join(Store, Store.id == StoreProduct.store_id)
            .filter(
                Store.slug == store_slug,
                Store.status == "approved",
                Store.deleted_at.is_(None),
                StoreProduct.slug == product_slug,
                StoreProduct.status == "published",
                StoreProduct.deleted_at.is_(None),
                StoreProduct.is_active.is_(True),
            )
            .one_or_none()
        )

    def create_product(
        self,
        *,
        store_id: int,
        category_id: int | None,
        name: str,
        slug: str,
        short_description: str | None,
        description: str | None,
        sku: str | None,
        status: str,
        price,
        compare_at_price,
        currency: str,
        stock_quantity: int,
        unit: str,
        min_order_quantity: int,
        max_order_quantity: int | None,
        is_active: bool,
        is_featured: bool,
    ) -> StoreProduct:
        product = StoreProduct(
            store_id=store_id,
            category_id=category_id,
            name=name,
            slug=slug,
            short_description=short_description,
            description=description,
            sku=sku,
            status=status,
            price=price,
            compare_at_price=compare_at_price,
            currency=currency,
            stock_quantity=stock_quantity,
            unit=unit,
            min_order_quantity=min_order_quantity,
            max_order_quantity=max_order_quantity,
            is_active=is_active,
            is_featured=is_featured,
        )
        self.db.add(product)
        self.db.flush()
        return product

    def create_status_history(
        self,
        *,
        product_id: int,
        changed_by: int | None,
        from_status: str | None,
        to_status: str,
        note: str | None,
    ) -> ProductStatusHistory:
        row = ProductStatusHistory(
            product_id=product_id,
            changed_by=changed_by,
            from_status=from_status,
            to_status=to_status,
            note=note,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def list_status_history(self, *, product_id: int) -> list[ProductStatusHistory]:
        return (
            self.db.query(ProductStatusHistory)
            .filter(ProductStatusHistory.product_id == product_id)
            .order_by(ProductStatusHistory.created_at.asc())
            .all()
        )

    def get_active_product_image_media(
        self,
        *,
        file_key: str,
    ) -> MediaFile | None:
        return (
            self.db.query(MediaFile)
            .filter(
                MediaFile.file_key == file_key,
                MediaFile.purpose == MediaPurpose.PRODUCT_IMAGE.value,
                MediaFile.visibility == MediaVisibility.PUBLIC.value,
                MediaFile.status == MediaStatus.ACTIVE.value,
            )
            .one_or_none()
        )

    def get_media_by_id(self, *, media_file_id: int) -> MediaFile | None:
        return (
            self.db.query(MediaFile)
            .filter(MediaFile.id == media_file_id)
            .one_or_none()
        )

    def create_product_image(
        self,
        *,
        product_id: int,
        file_id: str | None,
        media_file_id: int | None,
        file_path: str,
        alt_text: str | None,
        sort_order: int,
        is_primary: bool,
    ) -> ProductImage:
        image = ProductImage(
            product_id=product_id,
            file_id=file_id,
            media_file_id=media_file_id,
            file_path=file_path,
            alt_text=alt_text,
            sort_order=sort_order,
            is_primary=is_primary,
        )
        self.db.add(image)
        self.db.flush()
        return image

    def list_product_images(self, *, product_id: int) -> list[ProductImage]:
        return (
            self.db.query(ProductImage)
            .filter(ProductImage.product_id == product_id)
            .order_by(ProductImage.sort_order.asc(), ProductImage.id.asc())
            .all()
        )

    def get_product_image_by_id(
        self,
        *,
        product_id: int,
        image_id: int,
    ) -> ProductImage | None:
        return (
            self.db.query(ProductImage)
            .filter(
                ProductImage.product_id == product_id,
                ProductImage.id == image_id,
            )
            .one_or_none()
        )

    def clear_primary_product_images(
        self,
        *,
        product_id: int,
        except_image_id: int | None = None,
    ) -> None:
        query = self.db.query(ProductImage).filter(
            ProductImage.product_id == product_id,
            ProductImage.is_primary.is_(True),
        )

        if except_image_id is not None:
            query = query.filter(ProductImage.id != except_image_id)

        query.update(
            {ProductImage.is_primary: False},
            synchronize_session=False,
        )
        self.db.flush()

    def delete_product_image(self, *, image: ProductImage) -> None:
        self.db.delete(image)
        self.db.flush()

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    def refresh(self, instance) -> None:
        self.db.refresh(instance)

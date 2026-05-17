from sqlalchemy.orm import Session

from app.modules.products.models import (
    ProductCategory,
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

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    def refresh(self, instance) -> None:
        self.db.refresh(instance)
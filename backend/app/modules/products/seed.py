from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.modules.products.models import ProductCategory


@dataclass(frozen=True)
class ProductCategorySeed:
    name: str
    slug: str
    description: str | None = None
    sort_order: int = 0
    children: tuple["ProductCategorySeed", ...] = ()


PRODUCT_CATEGORY_TREE: tuple[ProductCategorySeed, ...] = (
    ProductCategorySeed(
        name="بذر",
        slug="seeds",
        description="انواع بذر کشاورزی",
        sort_order=10,
        children=(
            ProductCategorySeed(name="بذر گندم", slug="wheat-seeds", sort_order=10),
            ProductCategorySeed(name="بذر جو", slug="barley-seeds", sort_order=20),
            ProductCategorySeed(name="بذر ذرت", slug="corn-seeds", sort_order=30),
            ProductCategorySeed(name="بذر سبزیجات", slug="vegetable-seeds", sort_order=40),
        ),
    ),
    ProductCategorySeed(
        name="کود",
        slug="fertilizers",
        description="کودهای کشاورزی",
        sort_order=20,
        children=(
            ProductCategorySeed(name="کود شیمیایی", slug="chemical-fertilizers", sort_order=10),
            ProductCategorySeed(name="کود آلی", slug="organic-fertilizers", sort_order=20),
            ProductCategorySeed(name="کود مایع", slug="liquid-fertilizers", sort_order=30),
            ProductCategorySeed(name="کود ریزمغذی", slug="micronutrient-fertilizers", sort_order=40),
        ),
    ),
    ProductCategorySeed(
        name="سموم",
        slug="pesticides",
        description="سموم و محصولات کنترل آفات",
        sort_order=30,
        children=(
            ProductCategorySeed(name="حشره‌کش", slug="insecticides", sort_order=10),
            ProductCategorySeed(name="قارچ‌کش", slug="fungicides", sort_order=20),
            ProductCategorySeed(name="علف‌کش", slug="herbicides", sort_order=30),
            ProductCategorySeed(name="کنه‌کش", slug="acaricides", sort_order=40),
        ),
    ),
    ProductCategorySeed(
        name="تجهیزات",
        slug="equipment",
        description="ابزار و تجهیزات کشاورزی",
        sort_order=40,
        children=(
            ProductCategorySeed(name="ابزار دستی", slug="hand-tools", sort_order=10),
            ProductCategorySeed(name="تجهیزات آبیاری", slug="irrigation-equipment", sort_order=20),
            ProductCategorySeed(name="قطعات و لوازم", slug="parts-accessories", sort_order=30),
            ProductCategorySeed(name="تجهیزات گلخانه", slug="greenhouse-equipment", sort_order=40),
        ),
    ),
    ProductCategorySeed(
        name="نهاده‌ها",
        slug="agriculture-inputs",
        description="نهاده‌ها و مواد مصرفی کشاورزی",
        sort_order=50,
        children=(
            ProductCategorySeed(name="خاک و بستر کشت", slug="soil-growing-media", sort_order=10),
            ProductCategorySeed(name="مکمل‌ها", slug="supplements", sort_order=20),
            ProductCategorySeed(name="مواد اصلاح‌کننده خاک", slug="soil-conditioners", sort_order=30),
        ),
    ),
)


def seed_product_categories(db: Session) -> dict[str, int]:
    created = 0
    updated = 0

    for item in PRODUCT_CATEGORY_TREE:
        parent, parent_created, parent_updated = _upsert_category(
            db=db,
            item=item,
            parent_id=None,
        )
        created += int(parent_created)
        updated += int(parent_updated)

        for child in item.children:
            _, child_created, child_updated = _upsert_category(
                db=db,
                item=child,
                parent_id=parent.id,
            )
            created += int(child_created)
            updated += int(child_updated)

    db.commit()

    total = db.query(ProductCategory).count()
    active = db.query(ProductCategory).filter(ProductCategory.is_active.is_(True)).count()

    return {
        "total": total,
        "active": active,
        "created": created,
        "updated": updated,
    }


def _upsert_category(
    *,
    db: Session,
    item: ProductCategorySeed,
    parent_id: int | None,
) -> tuple[ProductCategory, bool, bool]:
    category = (
        db.query(ProductCategory)
        .filter(ProductCategory.slug == item.slug)
        .one_or_none()
    )

    if category is None:
        category = ProductCategory(
            parent_id=parent_id,
            name=item.name,
            slug=item.slug,
            description=item.description,
            sort_order=item.sort_order,
            is_active=True,
        )
        db.add(category)
        db.flush()
        return category, True, False

    # Once created, categories are Admin-owned. Re-running the bootstrap seed
    # must not reactivate, rename, reorder, or re-parent managed records.
    return category, False, False

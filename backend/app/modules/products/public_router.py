from math import ceil

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.exceptions import ValidationAuthError
from app.modules.products.models import ProductImage, StoreProduct
from app.modules.products.repository import ProductRepository
from app.modules.products.schemas import PublicProductImageOut, PublicProductOut
from app.modules.stores.enums import StoreType


router = APIRouter(
    tags=["Public Products"],
)


@router.get("/public/products")
def list_public_products(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    q: str | None = Query(default=None),
    store_id: int | None = Query(default=None, ge=1),
    category_id: int | None = Query(default=None, ge=1),
    province_id: int | None = Query(default=None, ge=1),
    county_id: int | None = Query(default=None, ge=1),
    city_id: int | None = Query(default=None, ge=1),
    store_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    if store_type is not None:
        _validate_store_type(store_type)

    repo = ProductRepository(db)

    items, total = repo.list_public_products(
        q=q.strip() if q else None,
        store_id=store_id,
        category_id=category_id,
        province_id=province_id,
        county_id=county_id,
        city_id=city_id,
        store_type=store_type,
        page=page,
        page_size=page_size,
    )

    return success_response(
        data=[_public_product_out(repo, item).model_dump(mode="json") for item in items],
        message="OK",
        meta={
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": ceil(total / page_size) if total else 0,
            "trace_id": request.state.trace_id,
        },
    )


@router.get("/public/products/{product_id}")
def get_public_product_by_id(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    repo = ProductRepository(db)

    product = repo.get_public_product_by_id(product_id=product_id)

    if product is None:
        raise ValidationAuthError(
            message="Product not found",
            details={"product_id": product_id},
        )

    return success_response(
        data=_public_product_out(repo, product).model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/public/stores/{store_slug}/products")
def list_public_store_products(
    store_slug: str,
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    q: str | None = Query(default=None),
    category_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
):
    repo = ProductRepository(db)

    items, total = repo.list_public_products_by_store_slug(
        store_slug=store_slug,
        q=q.strip() if q else None,
        category_id=category_id,
        page=page,
        page_size=page_size,
    )

    return success_response(
        data=[_public_product_out(repo, item).model_dump(mode="json") for item in items],
        message="OK",
        meta={
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": ceil(total / page_size) if total else 0,
            "trace_id": request.state.trace_id,
        },
    )


@router.get("/public/stores/{store_slug}/products/{product_slug}")
def get_public_store_product_by_slug(
    store_slug: str,
    product_slug: str,
    request: Request,
    db: Session = Depends(get_db),
):
    repo = ProductRepository(db)

    product = repo.get_public_product_by_store_and_slug(
        store_slug=store_slug,
        product_slug=product_slug,
    )

    if product is None:
        raise ValidationAuthError(
            message="Product not found",
            details={
                "store_slug": store_slug,
                "product_slug": product_slug,
            },
        )

    return success_response(
        data=_public_product_out(repo, product).model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


def _validate_store_type(store_type: str) -> None:
    allowed = {item.value for item in StoreType}

    if store_type not in allowed:
        raise ValidationAuthError(
            message="Invalid store_type",
            details={"allowed": sorted(allowed)},
        )


def _public_product_out(
    repo: ProductRepository,
    product: StoreProduct,
) -> PublicProductOut:
    images = repo.list_product_images(product_id=product.id)
    image_outputs = [_public_image_out(repo, image) for image in images]

    primary_image = next((item for item in image_outputs if item.is_primary), None)
    category = product.category if product.category else None

    return PublicProductOut(
        id=product.id,
        store_id=product.store_id,
        store_name=product.store.name if product.store else None,
        store_slug=product.store.slug if product.store else None,
        category_id=product.category_id,
        category_name=category.name if category else None,
        category_slug=category.slug if category else None,
        name=product.name,
        slug=product.slug,
        short_description=product.short_description,
        description=product.description,
        sku=product.sku,
        price=product.price,
        compare_at_price=product.compare_at_price,
        currency=product.currency,
        stock_quantity=product.stock_quantity,
        unit=product.unit,
        min_order_quantity=product.min_order_quantity,
        max_order_quantity=product.max_order_quantity,
        is_featured=product.is_featured,
        primary_image=primary_image,
        images=image_outputs,
        created_at=product.created_at.isoformat(),
        updated_at=product.updated_at.isoformat(),
    )


def _public_image_out(
    repo: ProductRepository,
    image: ProductImage,
) -> PublicProductImageOut:
    media = (
        repo.get_media_by_id(media_file_id=image.media_file_id)
        if image.media_file_id
        else None
    )
    file_key = media.file_key if media else None

    return PublicProductImageOut(
        id=image.id,
        file_id=image.file_id,
        media_file_id=image.media_file_id,
        file_key=file_key,
        public_url=_media_public_url(file_key=file_key),
        file_path=image.file_path,
        alt_text=image.alt_text,
        sort_order=image.sort_order,
        is_primary=image.is_primary,
    )


def _media_public_url(*, file_key: str | None) -> str | None:
    if not file_key:
        return None
    return f"/api/v1/media/public/{file_key}"

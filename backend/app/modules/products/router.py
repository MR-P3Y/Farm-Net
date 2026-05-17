from math import ceil

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.products.schemas import ProductCreateIn, ProductUpdateIn
from app.modules.products.service import ProductService


router = APIRouter(
    prefix="/stores/{store_id}/products",
    tags=["Store Products"],
)


@router.post("")
def create_product(
    store_id: int,
    payload: ProductCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("products.create")),
):
    service = ProductService(db)

    result = service.create_product(
        user=current_user,
        store_id=store_id,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Product created",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/me")
def list_my_products(
    store_id: int,
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    category_id: int | None = Query(default=None, ge=1),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("products.read")),
):
    service = ProductService(db)

    items, total = service.list_my_products(
        user=current_user,
        store_id=store_id,
        status=status,
        category_id=category_id,
        q=q.strip() if q else None,
        page=page,
        page_size=page_size,
    )

    return success_response(
        data=[item.model_dump(mode="json") for item in items],
        message="OK",
        meta={
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": ceil(total / page_size) if total else 0,
            "trace_id": request.state.trace_id,
        },
    )


@router.get("/{product_id}")
def get_product(
    store_id: int,
    product_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("products.read")),
):
    service = ProductService(db)

    result = service.get_my_product(
        user=current_user,
        store_id=store_id,
        product_id=product_id,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.put("/{product_id}")
def update_product(
    store_id: int,
    product_id: int,
    payload: ProductUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("products.update")),
):
    service = ProductService(db)

    result = service.update_product(
        user=current_user,
        store_id=store_id,
        product_id=product_id,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Product updated",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/{product_id}/publish")
def publish_product(
    store_id: int,
    product_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("products.publish")),
):
    service = ProductService(db)

    result = service.publish_product(
        user=current_user,
        store_id=store_id,
        product_id=product_id,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Product published",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/{product_id}/unpublish")
def unpublish_product(
    store_id: int,
    product_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("products.unpublish")),
):
    service = ProductService(db)

    result = service.unpublish_product(
        user=current_user,
        store_id=store_id,
        product_id=product_id,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Product unpublished",
        meta={"trace_id": request.state.trace_id},
    )


@router.delete("/{product_id}")
def archive_product(
    store_id: int,
    product_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("products.delete")),
):
    service = ProductService(db)

    result = service.archive_product(
        user=current_user,
        store_id=store_id,
        product_id=product_id,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Product archived",
        meta={"trace_id": request.state.trace_id},
    )


@router.get("/{product_id}/status-history")
def list_product_status_history(
    store_id: int,
    product_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("products.read")),
):
    service = ProductService(db)

    result = service.list_product_status_history(
        user=current_user,
        store_id=store_id,
        product_id=product_id,
    )

    return success_response(
        data=[item.model_dump(mode="json") for item in result],
        message="OK",
        meta={
            "count": len(result),
            "trace_id": request.state.trace_id,
        },
    )
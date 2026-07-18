from math import ceil

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.admin.product_service import AdminProductService
from app.modules.admin.schemas import AdminUpdateProductStatusIn
from app.modules.auth.dependencies import get_current_active_user, require_permission
from app.modules.auth.exceptions import PermissionDeniedError
from app.modules.auth.models import AuthUser
from app.modules.auth.repository import AuthRepository
from app.modules.products.category_service import ProductCategoryService
from app.modules.products.schemas import ProductCategoryCreateIn, ProductCategoryUpdateIn


router = APIRouter(
    prefix="/products",
    tags=["Admin Products"],
)


def _permission_for_status(status: str) -> str:
    if status == "suspended":
        return "products.suspend"

    if status in {"published", "unpublished"}:
        return "products.restore"

    return "products.admin_read"


@router.get("/categories")
def list_product_categories(
    request: Request,
    active_only: bool = Query(default=False),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("product_categories.admin_read")),
):
    items = ProductCategoryService(db).list_categories(
        active_only=active_only, q=q.strip() if q else None
    )
    return success_response(data=[item.model_dump() for item in items], message="OK", meta={"trace_id": request.state.trace_id})


@router.post("/categories")
def create_product_category(
    payload: ProductCategoryCreateIn,
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("product_categories.create")),
):
    item = ProductCategoryService(db).create(payload)
    return success_response(data=item.model_dump(), message="Product category created", meta={"trace_id": request.state.trace_id})


@router.patch("/categories/{category_id}")
def update_product_category(
    category_id: int,
    payload: ProductCategoryUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("product_categories.update")),
):
    item = ProductCategoryService(db).update(category_id=category_id, payload=payload)
    return success_response(data=item.model_dump(), message="Product category updated", meta={"trace_id": request.state.trace_id})


@router.get("")
def list_products(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    store_id: int | None = Query(default=None, ge=1),
    category_id: int | None = Query(default=None, ge=1),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("products.admin_read")),
):
    service = AdminProductService(db)

    items, total = service.list_products(
        page=page,
        page_size=page_size,
        status=status,
        store_id=store_id,
        category_id=category_id,
        q=q.strip() if q else None,
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
def get_product_detail(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _: AuthUser = Depends(require_permission("products.admin_read")),
):
    service = AdminProductService(db)

    result = service.get_product_detail(product_id=product_id)

    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.patch("/{product_id}/status")
def update_product_status(
    product_id: int,
    payload: AdminUpdateProductStatusIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    required_permission = _permission_for_status(payload.status)

    repo = AuthRepository(db)
    permissions = set(repo.get_user_permission_codes(current_user.id))

    if required_permission not in permissions:
        raise PermissionDeniedError()

    service = AdminProductService(db)

    result = service.update_product_status(
        product_id=product_id,
        status=payload.status,
        note=payload.note,
        reviewer=current_user,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Product status updated",
        meta={"trace_id": request.state.trace_id},
    )

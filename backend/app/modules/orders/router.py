from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_permission
from app.modules.auth.models import AuthUser
from app.modules.orders.schemas import CartItemAddIn, CartItemUpdateIn
from app.modules.orders.service import CartService


router = APIRouter(
    prefix="/cart",
    tags=["Cart"],
)


@router.get("/me")
def get_my_cart(
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("cart.read")),
):
    service = CartService(db)

    result = service.get_my_cart(user=current_user)

    return success_response(
        data=result.model_dump(mode="json"),
        message="OK",
        meta={"trace_id": request.state.trace_id},
    )


@router.post("/items")
def add_cart_item(
    payload: CartItemAddIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("cart.update")),
):
    service = CartService(db)

    result = service.add_item(
        user=current_user,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Cart item added",
        meta={"trace_id": request.state.trace_id},
    )


@router.patch("/items/{item_id}")
def update_cart_item(
    item_id: int,
    payload: CartItemUpdateIn,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("cart.update")),
):
    service = CartService(db)

    result = service.update_item(
        user=current_user,
        item_id=item_id,
        payload=payload,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Cart item updated",
        meta={"trace_id": request.state.trace_id},
    )


@router.delete("/items/{item_id}")
def delete_cart_item(
    item_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("cart.update")),
):
    service = CartService(db)

    result = service.delete_item(
        user=current_user,
        item_id=item_id,
    )

    return success_response(
        data=result.model_dump(mode="json"),
        message="Cart item deleted",
        meta={"trace_id": request.state.trace_id},
    )


@router.delete("/clear")
def clear_cart(
    request: Request,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(require_permission("cart.update")),
):
    service = CartService(db)

    result = service.clear_cart(user=current_user)

    return success_response(
        data=result.model_dump(mode="json"),
        message="Cart cleared",
        meta={"trace_id": request.state.trace_id},
    )

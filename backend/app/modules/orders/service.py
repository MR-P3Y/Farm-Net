from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.exceptions import ValidationAuthError
from app.modules.auth.models import AuthUser
from app.modules.orders.models import Cart, CartItem
from app.modules.orders.repository import OrderRepository
from app.modules.orders.schemas import (
    CartItemAddIn,
    CartItemOut,
    CartItemUpdateIn,
    CartOut,
)
from app.modules.products.models import StoreProduct


class CartService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = OrderRepository(db)

    def get_my_cart(self, *, user: AuthUser) -> CartOut:
        cart = self.repo.get_or_create_active_cart(user_id=user.id)
        self.repo.commit()
        self.repo.refresh(cart)

        return self._cart_out(cart)

    def add_item(
        self,
        *,
        user: AuthUser,
        payload: CartItemAddIn,
    ) -> CartOut:
        cart = self.repo.get_or_create_active_cart(user_id=user.id)

        product = self.repo.get_product_for_cart(product_id=payload.product_id)
        if product is None:
            raise ValidationAuthError(
                message="Product is not available for cart",
                details={"product_id": payload.product_id},
            )

        existing = self.repo.get_cart_item_by_product(
            cart_id=cart.id,
            product_id=product.id,
        )

        next_quantity = payload.quantity
        if existing is not None:
            next_quantity = existing.quantity + payload.quantity

        self._validate_quantity(product=product, quantity=next_quantity)

        if existing is None:
            self.repo.create_cart_item(
                cart_id=cart.id,
                product=product,
                quantity=payload.quantity,
            )
        else:
            self._update_item_snapshot(
                item=existing,
                product=product,
                quantity=next_quantity,
            )

        try:
            self.repo.commit()
        except IntegrityError as exc:
            self.repo.rollback()
            raise ValidationAuthError(
                message="Cart item already exists",
                details={"product_id": product.id},
            ) from exc

        self.repo.refresh(cart)
        return self._cart_out(cart)

    def update_item(
        self,
        *,
        user: AuthUser,
        item_id: int,
        payload: CartItemUpdateIn,
    ) -> CartOut:
        cart = self.repo.get_or_create_active_cart(user_id=user.id)

        item = self.repo.get_cart_item_by_id(cart_id=cart.id, item_id=item_id)
        if item is None:
            raise ValidationAuthError(
                message="Cart item not found",
                details={"item_id": item_id},
            )

        product = self.repo.get_product_for_cart(product_id=item.product_id)
        if product is None:
            raise ValidationAuthError(
                message="Product is no longer available",
                details={"product_id": item.product_id},
            )

        self._validate_quantity(product=product, quantity=payload.quantity)

        self._update_item_snapshot(
            item=item,
            product=product,
            quantity=payload.quantity,
        )

        self.repo.commit()
        self.repo.refresh(cart)

        return self._cart_out(cart)

    def delete_item(
        self,
        *,
        user: AuthUser,
        item_id: int,
    ) -> CartOut:
        cart = self.repo.get_or_create_active_cart(user_id=user.id)

        item = self.repo.get_cart_item_by_id(cart_id=cart.id, item_id=item_id)
        if item is None:
            raise ValidationAuthError(
                message="Cart item not found",
                details={"item_id": item_id},
            )

        self.repo.delete_cart_item(item=item)
        self.repo.commit()
        self.repo.refresh(cart)

        return self._cart_out(cart)

    def clear_cart(self, *, user: AuthUser) -> CartOut:
        cart = self.repo.get_or_create_active_cart(user_id=user.id)

        self.repo.clear_cart(cart_id=cart.id)
        self.repo.commit()
        self.repo.refresh(cart)

        return self._cart_out(cart)

    def _validate_quantity(
        self,
        *,
        product: StoreProduct,
        quantity: int,
    ) -> None:
        if quantity <= 0:
            raise ValidationAuthError(
                message="Invalid cart item quantity",
                details={"quantity": "must be greater than zero"},
            )

        if quantity < product.min_order_quantity:
            raise ValidationAuthError(
                message="Quantity is less than product minimum order quantity",
                details={
                    "quantity": quantity,
                    "min_order_quantity": product.min_order_quantity,
                },
            )

        if (
            product.max_order_quantity is not None
            and quantity > product.max_order_quantity
        ):
            raise ValidationAuthError(
                message="Quantity is greater than product maximum order quantity",
                details={
                    "quantity": quantity,
                    "max_order_quantity": product.max_order_quantity,
                },
            )

        if quantity > product.stock_quantity:
            raise ValidationAuthError(
                message="Quantity is greater than available stock",
                details={
                    "quantity": quantity,
                    "stock_quantity": product.stock_quantity,
                },
            )

    def _update_item_snapshot(
        self,
        *,
        item: CartItem,
        product: StoreProduct,
        quantity: int,
    ) -> None:
        item.quantity = quantity
        item.unit_price = product.price
        item.line_total = product.price * quantity
        item.product_name_snapshot = product.name
        item.product_slug_snapshot = product.slug
        item.product_sku_snapshot = product.sku
        item.unit_snapshot = product.unit

    def _cart_out(self, cart: Cart) -> CartOut:
        items = self.repo.list_cart_items(cart_id=cart.id)
        subtotal = sum((item.line_total for item in items), Decimal("0.00"))

        return CartOut(
            id=cart.id,
            user_id=cart.user_id,
            status=cart.status,
            currency=cart.currency,
            items=[self._cart_item_out(item) for item in items],
            items_count=len(items),
            subtotal_amount=subtotal,
            created_at=cart.created_at.isoformat(),
            updated_at=cart.updated_at.isoformat(),
            checked_out_at=cart.checked_out_at.isoformat()
            if cart.checked_out_at
            else None,
        )

    def _cart_item_out(self, item: CartItem) -> CartItemOut:
        return CartItemOut(
            id=item.id,
            cart_id=item.cart_id,
            product_id=item.product_id,
            store_id=item.store_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            line_total=item.line_total,
            product_name_snapshot=item.product_name_snapshot,
            product_slug_snapshot=item.product_slug_snapshot,
            product_sku_snapshot=item.product_sku_snapshot,
            unit_snapshot=item.unit_snapshot,
            created_at=item.created_at.isoformat(),
            updated_at=item.updated_at.isoformat(),
        )

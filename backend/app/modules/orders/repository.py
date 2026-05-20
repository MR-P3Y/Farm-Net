from sqlalchemy.orm import Session

from app.modules.orders.enums import CartStatus
from app.modules.orders.models import Cart, CartItem
from app.modules.products.models import StoreProduct
from app.modules.stores.models import Store


class OrderRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_active_cart_by_user(self, *, user_id: int) -> Cart | None:
        return (
            self.db.query(Cart)
            .filter(
                Cart.user_id == user_id,
                Cart.status == CartStatus.ACTIVE.value,
            )
            .one_or_none()
        )

    def create_cart(self, *, user_id: int, currency: str = "TOMAN") -> Cart:
        cart = Cart(
            user_id=user_id,
            status=CartStatus.ACTIVE.value,
            currency=currency,
        )
        self.db.add(cart)
        self.db.flush()
        return cart

    def get_or_create_active_cart(self, *, user_id: int) -> Cart:
        cart = self.get_active_cart_by_user(user_id=user_id)

        if cart is not None:
            return cart

        return self.create_cart(user_id=user_id)

    def get_cart_item_by_id(
        self,
        *,
        cart_id: int,
        item_id: int,
    ) -> CartItem | None:
        return (
            self.db.query(CartItem)
            .filter(
                CartItem.cart_id == cart_id,
                CartItem.id == item_id,
            )
            .one_or_none()
        )

    def get_cart_item_by_product(
        self,
        *,
        cart_id: int,
        product_id: int,
    ) -> CartItem | None:
        return (
            self.db.query(CartItem)
            .filter(
                CartItem.cart_id == cart_id,
                CartItem.product_id == product_id,
            )
            .one_or_none()
        )

    def list_cart_items(self, *, cart_id: int) -> list[CartItem]:
        return (
            self.db.query(CartItem)
            .filter(CartItem.cart_id == cart_id)
            .order_by(CartItem.created_at.asc(), CartItem.id.asc())
            .all()
        )

    def get_product_for_cart(self, *, product_id: int) -> StoreProduct | None:
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

    def create_cart_item(
        self,
        *,
        cart_id: int,
        product: StoreProduct,
        quantity: int,
    ) -> CartItem:
        item = CartItem(
            cart_id=cart_id,
            product_id=product.id,
            store_id=product.store_id,
            quantity=quantity,
            unit_price=product.price,
            line_total=product.price * quantity,
            product_name_snapshot=product.name,
            product_slug_snapshot=product.slug,
            product_sku_snapshot=product.sku,
            unit_snapshot=product.unit,
        )
        self.db.add(item)
        self.db.flush()
        return item

    def delete_cart_item(self, *, item: CartItem) -> None:
        self.db.delete(item)
        self.db.flush()

    def clear_cart(self, *, cart_id: int) -> int:
        count = (
            self.db.query(CartItem)
            .filter(CartItem.cart_id == cart_id)
            .delete(synchronize_session=False)
        )
        self.db.flush()
        return count

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    def refresh(self, instance) -> None:
        self.db.refresh(instance)

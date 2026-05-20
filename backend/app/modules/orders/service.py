from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.exceptions import ValidationAuthError
from app.modules.auth.models import AuthUser
from app.modules.orders.enums import CartStatus, OrderStatus
from app.modules.orders.models import (
    Cart,
    CartItem,
    Order,
    OrderItem,
    OrderStatusHistory,
    Payment,
)
from app.modules.orders.repository import OrderRepository
from app.modules.orders.schemas import (
    CartItemAddIn,
    CartItemOut,
    CartItemUpdateIn,
    CartOut,
    CheckoutIn,
    CheckoutOut,
    OrderItemOut,
    OrderOut,
    OrderStatusHistoryOut,
    PaymentOut,
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


class CheckoutService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = OrderRepository(db)

    def checkout(
        self,
        *,
        user: AuthUser,
        payload: CheckoutIn,
    ) -> CheckoutOut:
        cart = self.repo.get_active_cart_by_user(user_id=user.id)

        if cart is None:
            raise ValidationAuthError(
                message="Active cart not found",
                details={"user_id": user.id},
            )

        cart_items = self.repo.list_cart_items(cart_id=cart.id)

        if not cart_items:
            raise ValidationAuthError(
                message="Cart is empty",
                details={"cart_id": cart.id},
            )

        validated_items = []
        for item in cart_items:
            product = self.repo.get_product_for_cart(product_id=item.product_id)

            if product is None:
                raise ValidationAuthError(
                    message="Product is no longer available for checkout",
                    details={"product_id": item.product_id},
                )

            self._validate_cart_item_against_product(item=item, product=product)

            item.unit_price = product.price
            item.line_total = product.price * item.quantity
            item.product_name_snapshot = product.name
            item.product_slug_snapshot = product.slug
            item.product_sku_snapshot = product.sku
            item.unit_snapshot = product.unit

            validated_items.append(item)

        commission = self.repo.get_active_default_commission()
        if commission is None:
            raise ValidationAuthError(
                message="Active default commission setting not found",
                details={"commission": "missing"},
            )

        grouped: dict[int, list[CartItem]] = defaultdict(list)
        for item in validated_items:
            grouped[item.store_id].append(item)

        orders: list[Order] = []

        for store_id, items in grouped.items():
            subtotal = sum((item.line_total for item in items), Decimal("0.00"))
            discount = Decimal("0.00")
            shipping = Decimal("0.00")
            total = subtotal - discount + shipping

            commission_percent = commission.percent
            commission_amount = (total * commission_percent / Decimal("100")).quantize(
                Decimal("0.01"),
            )
            seller_amount = total - commission_amount

            order = self.repo.create_order(
                order_number=self._generate_order_number(),
                buyer_user_id=user.id,
                store_id=store_id,
                currency=cart.currency,
                subtotal_amount=subtotal,
                discount_amount=discount,
                shipping_amount=shipping,
                total_amount=total,
                commission_percent=commission_percent,
                commission_amount=commission_amount,
                seller_amount=seller_amount,
                buyer_note=payload.buyer_note,
                shipping_province_id=payload.shipping_province_id,
                shipping_county_id=payload.shipping_county_id,
                shipping_city_id=payload.shipping_city_id,
                shipping_address=payload.shipping_address,
                shipping_postal_code=payload.shipping_postal_code,
                shipping_phone=payload.shipping_phone,
            )

            for item in items:
                self.repo.create_order_item(
                    order_id=order.id,
                    cart_item=item,
                )

            self.repo.create_payment(
                order_id=order.id,
                user_id=user.id,
                amount=total,
                currency=cart.currency,
            )

            self.repo.create_order_status_history(
                order_id=order.id,
                changed_by=user.id,
                from_status=None,
                to_status=OrderStatus.PENDING_PAYMENT.value,
                note="Order created from cart checkout",
            )

            orders.append(order)

        cart.status = CartStatus.CHECKED_OUT.value
        cart.checked_out_at = datetime.utcnow()

        self.repo.commit()

        for order in orders:
            self.repo.refresh(order)

        total_amount = sum((order.total_amount for order in orders), Decimal("0.00"))

        return CheckoutOut(
            orders=[self._order_out(order) for order in orders],
            orders_count=len(orders),
            total_amount=total_amount,
        )

    def list_my_orders(
        self,
        *,
        user: AuthUser,
        status: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[OrderOut], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        if status is not None:
            self._validate_order_status(status)

        items, total = self.repo.list_my_orders(
            buyer_user_id=user.id,
            status=status,
            page=page,
            page_size=page_size,
        )

        return [self._order_out(item) for item in items], total

    def get_my_order(
        self,
        *,
        user: AuthUser,
        order_id: int,
    ) -> OrderOut:
        order = self.repo.get_my_order_by_id(
            buyer_user_id=user.id,
            order_id=order_id,
        )

        if order is None:
            raise ValidationAuthError(
                message="Order not found",
                details={"order_id": order_id},
            )

        return self._order_out(order)

    def _validate_cart_item_against_product(
        self,
        *,
        item: CartItem,
        product: StoreProduct,
    ) -> None:
        if item.quantity < product.min_order_quantity:
            raise ValidationAuthError(
                message="Cart item quantity is less than product minimum",
                details={
                    "product_id": product.id,
                    "quantity": item.quantity,
                    "min_order_quantity": product.min_order_quantity,
                },
            )

        if (
            product.max_order_quantity is not None
            and item.quantity > product.max_order_quantity
        ):
            raise ValidationAuthError(
                message="Cart item quantity is greater than product maximum",
                details={
                    "product_id": product.id,
                    "quantity": item.quantity,
                    "max_order_quantity": product.max_order_quantity,
                },
            )

        if item.quantity > product.stock_quantity:
            raise ValidationAuthError(
                message="Cart item quantity is greater than available stock",
                details={
                    "product_id": product.id,
                    "quantity": item.quantity,
                    "stock_quantity": product.stock_quantity,
                },
            )

    def _validate_order_status(self, status: str) -> None:
        allowed = {item.value for item in OrderStatus}

        if status not in allowed:
            raise ValidationAuthError(
                message="Invalid order status filter",
                details={"allowed": sorted(allowed)},
            )

    def _generate_order_number(self) -> str:
        stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        suffix = uuid4().hex[:8].upper()
        return f"FN-{stamp}-{suffix}"

    def _order_out(self, order: Order) -> OrderOut:
        items = self.repo.list_order_items(order_id=order.id)
        payments = self.repo.list_order_payments(order_id=order.id)
        history = self.repo.list_order_status_history(order_id=order.id)

        return OrderOut(
            id=order.id,
            order_number=order.order_number,
            buyer_user_id=order.buyer_user_id,
            store_id=order.store_id,
            status=order.status,
            payment_status=order.payment_status,
            currency=order.currency,
            subtotal_amount=order.subtotal_amount,
            discount_amount=order.discount_amount,
            shipping_amount=order.shipping_amount,
            total_amount=order.total_amount,
            commission_percent=order.commission_percent,
            commission_amount=order.commission_amount,
            seller_amount=order.seller_amount,
            buyer_note=order.buyer_note,
            seller_note=order.seller_note,
            admin_note=order.admin_note,
            shipping_province_id=order.shipping_province_id,
            shipping_county_id=order.shipping_county_id,
            shipping_city_id=order.shipping_city_id,
            shipping_address=order.shipping_address,
            shipping_postal_code=order.shipping_postal_code,
            shipping_phone=order.shipping_phone,
            paid_at=order.paid_at.isoformat() if order.paid_at else None,
            confirmed_at=order.confirmed_at.isoformat()
            if order.confirmed_at
            else None,
            cancelled_at=order.cancelled_at.isoformat()
            if order.cancelled_at
            else None,
            delivered_at=order.delivered_at.isoformat()
            if order.delivered_at
            else None,
            created_at=order.created_at.isoformat(),
            updated_at=order.updated_at.isoformat(),
            items=[self._order_item_out(item) for item in items],
            payments=[self._payment_out(payment) for payment in payments],
            status_history=[self._history_out(row) for row in history],
        )

    def _order_item_out(self, item: OrderItem) -> OrderItemOut:
        return OrderItemOut(
            id=item.id,
            order_id=item.order_id,
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
        )

    def _payment_out(self, payment: Payment) -> PaymentOut:
        return PaymentOut(
            id=payment.id,
            order_id=payment.order_id,
            user_id=payment.user_id,
            method=payment.method,
            status=payment.status,
            amount=payment.amount,
            currency=payment.currency,
            provider=payment.provider,
            provider_payment_id=payment.provider_payment_id,
            provider_reference=payment.provider_reference,
            paid_at=payment.paid_at.isoformat() if payment.paid_at else None,
            failed_at=payment.failed_at.isoformat() if payment.failed_at else None,
            cancelled_at=payment.cancelled_at.isoformat()
            if payment.cancelled_at
            else None,
            created_at=payment.created_at.isoformat(),
            updated_at=payment.updated_at.isoformat(),
        )

    def _history_out(self, row: OrderStatusHistory) -> OrderStatusHistoryOut:
        return OrderStatusHistoryOut(
            id=row.id,
            order_id=row.order_id,
            changed_by=row.changed_by,
            from_status=row.from_status,
            to_status=row.to_status,
            note=row.note,
            created_at=row.created_at.isoformat(),
        )

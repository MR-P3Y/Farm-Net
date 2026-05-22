from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.exceptions import ValidationAuthError
from app.modules.auth.models import AuthUser
from app.modules.orders.enums import CartStatus, OrderStatus, PaymentStatus
from app.modules.orders.models import (
    Cart,
    CartItem,
    CommissionSetting,
    Order,
    OrderItem,
    OrderStatusHistory,
    Payment,
)
from app.modules.orders.repository import OrderRepository
from app.modules.orders.schemas import (
    AdminOrderStatusUpdateIn,
    CartItemAddIn,
    CartItemOut,
    CartItemUpdateIn,
    CartOut,
    CheckoutIn,
    CheckoutOut,
    CommissionSettingOut,
    CommissionSettingUpdateIn,
    MockPaymentFailIn,
    OrderItemOut,
    OrderOut,
    OrderStatusHistoryOut,
    PaymentOut,
    SellerOrderStatusUpdateIn,
)
from app.modules.notifications.enums import NotificationEventType
from app.modules.notifications.service import NotificationService
from app.modules.products.models import StoreProduct


def _notify_order_created(
    *,
    db: Session,
    order: Order,
) -> None:
    NotificationService(db).create_event_and_notify_user(
        event_type=NotificationEventType.ORDER_CREATED.value,
        recipient_user_id=order.buyer_user_id,
        title="Order created",
        body=f"Order #{order.id} was created successfully.",
        actor_user_id=order.buyer_user_id,
        source_type="order",
        source_id=str(order.id),
        payload_json={
            "order_id": order.id,
            "status": order.status,
            "total_amount": str(order.total_amount),
        },
        action_url=f"/orders/{order.id}",
        priority="normal",
        commit=False,
    )


def _notify_order_status_changed(
    *,
    db: Session,
    order: Order,
    old_status: str,
    new_status: str,
    actor_user_id: int | None,
) -> None:
    NotificationService(db).create_event_and_notify_user(
        event_type=NotificationEventType.ORDER_STATUS_CHANGED.value,
        recipient_user_id=order.buyer_user_id,
        title="Order status changed",
        body=f"Order #{order.id} status changed from {old_status} to {new_status}.",
        actor_user_id=actor_user_id,
        source_type="order",
        source_id=str(order.id),
        payload_json={
            "order_id": order.id,
            "old_status": old_status,
            "new_status": new_status,
        },
        action_url=f"/orders/{order.id}",
        priority="normal",
        commit=False,
    )


def _notify_payment_created(
    *,
    db: Session,
    payment: Payment,
    order: Order,
) -> None:
    NotificationService(db).create_event_and_notify_user(
        event_type=NotificationEventType.PAYMENT_CREATED.value,
        recipient_user_id=order.buyer_user_id,
        title="Payment created",
        body=f"Payment for order #{order.id} was created.",
        actor_user_id=order.buyer_user_id,
        source_type="payment",
        source_id=str(payment.id),
        payload_json={
            "payment_id": payment.id,
            "order_id": order.id,
            "status": payment.status,
            "amount": str(payment.amount),
        },
        action_url=f"/orders/{order.id}",
        priority="normal",
        commit=False,
    )


def _notify_payment_status_changed(
    *,
    db: Session,
    payment: Payment,
    order: Order,
    old_status: str,
    new_status: str,
    actor_user_id: int | None,
) -> None:
    succeeded = new_status == PaymentStatus.PAID.value
    event_type = (
        NotificationEventType.PAYMENT_SUCCEEDED.value
        if succeeded
        else NotificationEventType.PAYMENT_FAILED.value
    )

    NotificationService(db).create_event_and_notify_user(
        event_type=event_type,
        recipient_user_id=order.buyer_user_id,
        title="Payment succeeded" if succeeded else "Payment failed",
        body=(
            f"Payment for order #{order.id} was completed successfully."
            if succeeded
            else f"Payment for order #{order.id} failed."
        ),
        actor_user_id=actor_user_id,
        source_type="payment",
        source_id=str(payment.id),
        payload_json={
            "payment_id": payment.id,
            "order_id": order.id,
            "old_status": old_status,
            "new_status": new_status,
        },
        action_url=f"/orders/{order.id}",
        priority="normal" if succeeded else "high",
        commit=False,
    )


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

            payment = self.repo.create_payment(
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

            _notify_order_created(db=self.db, order=order)
            _notify_payment_created(db=self.db, payment=payment, order=order)

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


class SellerOrderService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = OrderRepository(db)

    def list_seller_orders(
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

        items, total = self.repo.list_seller_orders(
            seller_user_id=user.id,
            status=status,
            page=page,
            page_size=page_size,
        )

        return [self._order_out(item) for item in items], total

    def get_seller_order(
        self,
        *,
        user: AuthUser,
        order_id: int,
    ) -> OrderOut:
        order = self.repo.get_seller_order_by_id(
            seller_user_id=user.id,
            order_id=order_id,
        )

        if order is None:
            raise ValidationAuthError(
                message="Order not found",
                details={"order_id": order_id},
            )

        return self._order_out(order)

    def update_seller_order_status(
        self,
        *,
        user: AuthUser,
        order_id: int,
        payload: SellerOrderStatusUpdateIn,
    ) -> OrderOut:
        order = self.repo.get_seller_order_by_id(
            seller_user_id=user.id,
            order_id=order_id,
        )

        if order is None:
            raise ValidationAuthError(
                message="Order not found",
                details={"order_id": order_id},
            )

        self._validate_seller_target_status(payload.status)

        if order.payment_status != PaymentStatus.PAID.value:
            raise ValidationAuthError(
                message="Order must be paid before seller can update it",
                details={
                    "order_id": order.id,
                    "payment_status": order.payment_status,
                },
            )

        self._validate_seller_transition(
            current_status=order.status,
            next_status=payload.status,
        )

        old_status = order.status
        order.status = payload.status
        order.seller_note = payload.seller_note

        now = datetime.utcnow()

        if payload.status == OrderStatus.CONFIRMED.value:
            order.confirmed_at = now

        if payload.status == OrderStatus.DELIVERED.value:
            order.delivered_at = now

        self.repo.create_order_status_history(
            order_id=order.id,
            changed_by=user.id,
            from_status=old_status,
            to_status=payload.status,
            note=payload.seller_note
            or f"Seller changed order status to {payload.status}",
        )

        _notify_order_status_changed(
            db=self.db,
            order=order,
            old_status=old_status,
            new_status=payload.status,
            actor_user_id=user.id,
        )

        self.repo.commit()
        self.repo.refresh(order)

        return self._order_out(order)

    def _validate_order_status(self, status: str) -> None:
        allowed = {item.value for item in OrderStatus}

        if status not in allowed:
            raise ValidationAuthError(
                message="Invalid order status filter",
                details={"allowed": sorted(allowed)},
            )

    def _validate_seller_target_status(self, status: str) -> None:
        allowed = {
            OrderStatus.CONFIRMED.value,
            OrderStatus.PROCESSING.value,
            OrderStatus.SHIPPED.value,
            OrderStatus.DELIVERED.value,
        }

        if status not in allowed:
            raise ValidationAuthError(
                message="Invalid seller order status",
                details={"allowed": sorted(allowed)},
            )

    def _validate_seller_transition(
        self,
        *,
        current_status: str,
        next_status: str,
    ) -> None:
        allowed_transitions = {
            OrderStatus.PAID.value: {OrderStatus.CONFIRMED.value},
            OrderStatus.CONFIRMED.value: {OrderStatus.PROCESSING.value},
            OrderStatus.PROCESSING.value: {OrderStatus.SHIPPED.value},
            OrderStatus.SHIPPED.value: {OrderStatus.DELIVERED.value},
        }

        allowed_next = allowed_transitions.get(current_status, set())

        if next_status not in allowed_next:
            raise ValidationAuthError(
                message="Invalid seller order status transition",
                details={
                    "current_status": current_status,
                    "next_status": next_status,
                    "allowed_next": sorted(allowed_next),
                },
            )

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


class AdminOrderService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = OrderRepository(db)

    def list_admin_orders(
        self,
        *,
        status: str | None,
        payment_status: str | None,
        store_id: int | None,
        buyer_user_id: int | None,
        page: int,
        page_size: int,
    ) -> tuple[list[OrderOut], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        if status is not None:
            self._validate_order_status(status)

        if payment_status is not None:
            self._validate_payment_status(payment_status)

        items, total = self.repo.list_admin_orders(
            status=status,
            payment_status=payment_status,
            store_id=store_id,
            buyer_user_id=buyer_user_id,
            page=page,
            page_size=page_size,
        )

        return [self._order_out(item) for item in items], total

    def get_admin_order(
        self,
        *,
        order_id: int,
    ) -> OrderOut:
        order = self.repo.get_admin_order_by_id(order_id=order_id)

        if order is None:
            raise ValidationAuthError(
                message="Order not found",
                details={"order_id": order_id},
            )

        return self._order_out(order)

    def update_admin_order_status(
        self,
        *,
        user: AuthUser,
        order_id: int,
        payload: AdminOrderStatusUpdateIn,
    ) -> OrderOut:
        order = self.repo.get_admin_order_by_id(order_id=order_id)

        if order is None:
            raise ValidationAuthError(
                message="Order not found",
                details={"order_id": order_id},
            )

        self._validate_admin_target_status(payload.status)
        self._validate_admin_transition(
            current_status=order.status,
            next_status=payload.status,
        )

        old_status = order.status
        now = datetime.utcnow()

        order.status = payload.status
        order.admin_note = payload.admin_note

        if payload.status == OrderStatus.CANCELLED.value:
            order.cancelled_at = now

        if payload.status == OrderStatus.REFUNDED.value:
            order.payment_status = PaymentStatus.REFUNDED.value

        self.repo.create_order_status_history(
            order_id=order.id,
            changed_by=user.id,
            from_status=old_status,
            to_status=payload.status,
            note=payload.admin_note
            or f"Admin changed order status to {payload.status}",
        )

        _notify_order_status_changed(
            db=self.db,
            order=order,
            old_status=old_status,
            new_status=payload.status,
            actor_user_id=user.id,
        )

        self.repo.commit()
        self.repo.refresh(order)

        return self._order_out(order)

    def _validate_order_status(self, status: str) -> None:
        allowed = {item.value for item in OrderStatus}

        if status not in allowed:
            raise ValidationAuthError(
                message="Invalid order status filter",
                details={"allowed": sorted(allowed)},
            )

    def _validate_payment_status(self, status: str) -> None:
        allowed = {item.value for item in PaymentStatus}

        if status not in allowed:
            raise ValidationAuthError(
                message="Invalid payment status filter",
                details={"allowed": sorted(allowed)},
            )

    def _validate_admin_target_status(self, status: str) -> None:
        allowed = {
            OrderStatus.CANCELLED.value,
            OrderStatus.REFUNDED.value,
        }

        if status not in allowed:
            raise ValidationAuthError(
                message="Invalid admin order status",
                details={"allowed": sorted(allowed)},
            )

    def _validate_admin_transition(
        self,
        *,
        current_status: str,
        next_status: str,
    ) -> None:
        allowed_transitions = {
            OrderStatus.PENDING_PAYMENT.value: {OrderStatus.CANCELLED.value},
            OrderStatus.PAID.value: {OrderStatus.CANCELLED.value},
            OrderStatus.CONFIRMED.value: {OrderStatus.CANCELLED.value},
            OrderStatus.PROCESSING.value: {OrderStatus.CANCELLED.value},
            OrderStatus.DELIVERED.value: {OrderStatus.REFUNDED.value},
        }

        allowed_next = allowed_transitions.get(current_status, set())

        if next_status not in allowed_next:
            raise ValidationAuthError(
                message="Invalid admin order status transition",
                details={
                    "current_status": current_status,
                    "next_status": next_status,
                    "allowed_next": sorted(allowed_next),
                },
            )

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


class CommissionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = OrderRepository(db)

    def list_settings(self) -> list[CommissionSettingOut]:
        rows = self.repo.list_commission_settings()
        return [self._commission_out(row) for row in rows]

    def get_default_setting(self) -> CommissionSettingOut:
        setting = self.repo.get_default_commission_setting()

        if setting is None:
            raise ValidationAuthError(
                message="Default commission setting not found",
                details={"commission": "missing"},
            )

        return self._commission_out(setting)

    def update_default_setting(
        self,
        *,
        user: AuthUser,
        payload: CommissionSettingUpdateIn,
    ) -> CommissionSettingOut:
        setting = self.repo.get_default_commission_setting()

        if setting is None:
            raise ValidationAuthError(
                message="Default commission setting not found",
                details={"commission": "missing"},
            )

        if payload.percent < 0 or payload.percent > 100:
            raise ValidationAuthError(
                message="Invalid commission percent",
                details={"percent": str(payload.percent)},
            )

        setting.percent = payload.percent
        setting.description = payload.description
        setting.updated_by = user.id

        self.repo.commit()
        self.repo.refresh(setting)

        return self._commission_out(setting)

    def _commission_out(self, setting: CommissionSetting) -> CommissionSettingOut:
        return CommissionSettingOut(
            id=setting.id,
            title=setting.title,
            percent=setting.percent,
            status=setting.status,
            is_default=setting.is_default,
            description=setting.description,
            created_by=setting.created_by,
            updated_by=setting.updated_by,
            created_at=setting.created_at.isoformat(),
            updated_at=setting.updated_at.isoformat(),
        )


class PaymentService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = OrderRepository(db)

    def list_my_payments(
        self,
        *,
        user: AuthUser,
        status: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[PaymentOut], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        if status is not None:
            self._validate_payment_status(status)

        items, total = self.repo.list_my_payments(
            user_id=user.id,
            status=status,
            page=page,
            page_size=page_size,
        )

        return [self._payment_out(item) for item in items], total

    def get_my_payment(
        self,
        *,
        user: AuthUser,
        payment_id: int,
    ) -> PaymentOut:
        payment = self.repo.get_my_payment_by_id(
            user_id=user.id,
            payment_id=payment_id,
        )

        if payment is None:
            raise ValidationAuthError(
                message="Payment not found",
                details={"payment_id": payment_id},
            )

        return self._payment_out(payment)

    def mock_pay(
        self,
        *,
        user: AuthUser,
        payment_id: int,
    ) -> PaymentOut:
        payment = self.repo.get_my_payment_by_id(
            user_id=user.id,
            payment_id=payment_id,
        )

        if payment is None:
            raise ValidationAuthError(
                message="Payment not found",
                details={"payment_id": payment_id},
            )

        if payment.status != PaymentStatus.PENDING.value:
            raise ValidationAuthError(
                message="Payment cannot be paid in current status",
                details={"current_status": payment.status},
            )

        order = self.repo.get_order_by_id(order_id=payment.order_id)
        if order is None:
            raise ValidationAuthError(
                message="Order not found",
                details={"order_id": payment.order_id},
            )

        now = datetime.utcnow()

        old_payment_status = payment.status
        payment.status = PaymentStatus.PAID.value
        payment.paid_at = now
        payment.provider_reference = f"MOCK-PAID-{payment.id}"

        old_order_status = order.status
        order.payment_status = PaymentStatus.PAID.value
        order.status = OrderStatus.PAID.value
        order.paid_at = now

        self.repo.create_order_status_history(
            order_id=order.id,
            changed_by=user.id,
            from_status=old_order_status,
            to_status=OrderStatus.PAID.value,
            note="Mock payment paid",
        )

        _notify_payment_status_changed(
            db=self.db,
            payment=payment,
            order=order,
            old_status=old_payment_status,
            new_status=PaymentStatus.PAID.value,
            actor_user_id=user.id,
        )
        _notify_order_status_changed(
            db=self.db,
            order=order,
            old_status=old_order_status,
            new_status=OrderStatus.PAID.value,
            actor_user_id=user.id,
        )

        self.repo.commit()
        self.repo.refresh(payment)

        return self._payment_out(payment)

    def mock_fail(
        self,
        *,
        user: AuthUser,
        payment_id: int,
        payload: MockPaymentFailIn,
    ) -> PaymentOut:
        payment = self.repo.get_my_payment_by_id(
            user_id=user.id,
            payment_id=payment_id,
        )

        if payment is None:
            raise ValidationAuthError(
                message="Payment not found",
                details={"payment_id": payment_id},
            )

        if payment.status != PaymentStatus.PENDING.value:
            raise ValidationAuthError(
                message="Payment cannot be failed in current status",
                details={"current_status": payment.status},
            )

        order = self.repo.get_order_by_id(order_id=payment.order_id)
        if order is None:
            raise ValidationAuthError(
                message="Order not found",
                details={"order_id": payment.order_id},
            )

        now = datetime.utcnow()

        old_payment_status = payment.status
        payment.status = PaymentStatus.FAILED.value
        payment.failed_at = now
        payment.failure_reason = payload.reason or "Mock payment failed"

        order.payment_status = PaymentStatus.FAILED.value

        _notify_payment_status_changed(
            db=self.db,
            payment=payment,
            order=order,
            old_status=old_payment_status,
            new_status=PaymentStatus.FAILED.value,
            actor_user_id=user.id,
        )

        self.repo.commit()
        self.repo.refresh(payment)

        return self._payment_out(payment)

    def _validate_payment_status(self, status: str) -> None:
        allowed = {item.value for item in PaymentStatus}

        if status not in allowed:
            raise ValidationAuthError(
                message="Invalid payment status filter",
                details={"allowed": sorted(allowed)},
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

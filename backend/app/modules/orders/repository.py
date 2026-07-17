from datetime import datetime

from sqlalchemy.orm import Session

from app.modules.orders.enums import (
    CartStatus,
    CommissionSettingStatus,
    FinancialTransactionStatus,
    FinancialTransactionType,
    InventoryReservationStatus,
    InvoiceStatus,
    OrderStatus,
    PaymentAttemptStatus,
    PaymentMethod,
    PaymentStatus,
)
from app.modules.orders.models import (
    Cart,
    CartItem,
    CommissionSnapshot,
    CommissionSetting,
    FinancialInvoice,
    FinancialInvoiceItem,
    FinancialTransaction,
    InventoryReservation,
    Order,
    OrderItem,
    OrderStatusHistory,
    Payment,
    PaymentAttempt,
)
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

    def get_active_cart_for_checkout(self, *, user_id: int) -> Cart | None:
        return (
            self.db.query(Cart)
            .filter(Cart.user_id == user_id, Cart.status == CartStatus.ACTIVE.value)
            .with_for_update()
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

    def lock_products_for_checkout(self, *, product_ids: list[int]) -> dict[int, StoreProduct]:
        rows = (
            self.db.query(StoreProduct)
            .join(Store, Store.id == StoreProduct.store_id)
            .filter(
                StoreProduct.id.in_(sorted(set(product_ids))),
                StoreProduct.status == "published",
                StoreProduct.deleted_at.is_(None),
                StoreProduct.is_active.is_(True),
                Store.status == "approved",
                Store.deleted_at.is_(None),
            )
            .order_by(StoreProduct.id.asc())
            .with_for_update()
            .all()
        )
        return {row.id: row for row in rows}

    def lock_products_by_ids(self, *, product_ids: list[int]) -> dict[int, StoreProduct]:
        rows = (
            self.db.query(StoreProduct)
            .filter(StoreProduct.id.in_(sorted(set(product_ids))))
            .order_by(StoreProduct.id.asc())
            .with_for_update()
            .all()
        )
        return {row.id: row for row in rows}

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

    def get_active_default_commission(self) -> CommissionSetting | None:
        return (
            self.db.query(CommissionSetting)
            .filter(
                CommissionSetting.status == CommissionSettingStatus.ACTIVE.value,
                CommissionSetting.is_default.is_(True),
            )
            .one_or_none()
        )

    def create_order(
        self,
        *,
        order_number: str,
        buyer_user_id: int,
        store_id: int,
        currency: str,
        subtotal_amount,
        discount_amount,
        shipping_amount,
        total_amount,
        commission_percent,
        commission_amount,
        seller_amount,
        buyer_note: str | None,
        shipping_province_id: int | None,
        shipping_county_id: int | None,
        shipping_city_id: int | None,
        shipping_address: str | None,
        shipping_postal_code: str | None,
        shipping_phone: str | None,
    ) -> Order:
        order = Order(
            order_number=order_number,
            buyer_user_id=buyer_user_id,
            store_id=store_id,
            status=OrderStatus.PENDING_PAYMENT.value,
            payment_status=PaymentStatus.PENDING.value,
            currency=currency,
            subtotal_amount=subtotal_amount,
            discount_amount=discount_amount,
            shipping_amount=shipping_amount,
            total_amount=total_amount,
            commission_percent=commission_percent,
            commission_amount=commission_amount,
            seller_amount=seller_amount,
            buyer_note=buyer_note,
            shipping_province_id=shipping_province_id,
            shipping_county_id=shipping_county_id,
            shipping_city_id=shipping_city_id,
            shipping_address=shipping_address,
            shipping_postal_code=shipping_postal_code,
            shipping_phone=shipping_phone,
        )
        self.db.add(order)
        self.db.flush()
        return order

    def create_order_item(
        self,
        *,
        order_id: int,
        cart_item: CartItem,
    ) -> OrderItem:
        item = OrderItem(
            order_id=order_id,
            product_id=cart_item.product_id,
            store_id=cart_item.store_id,
            quantity=cart_item.quantity,
            unit_price=cart_item.unit_price,
            line_total=cart_item.line_total,
            product_name_snapshot=cart_item.product_name_snapshot,
            product_slug_snapshot=cart_item.product_slug_snapshot,
            product_sku_snapshot=cart_item.product_sku_snapshot,
            unit_snapshot=cart_item.unit_snapshot,
        )
        self.db.add(item)
        self.db.flush()
        return item

    def create_payment(
        self,
        *,
        order_id: int,
        user_id: int,
        amount,
        currency: str,
        method: str = PaymentMethod.MOCK.value,
        status: str = PaymentStatus.PENDING.value,
    ) -> Payment:
        payment = Payment(
            order_id=order_id,
            user_id=user_id,
            method=method,
            status=status,
            amount=amount,
            currency=currency,
            provider="mock",
        )
        self.db.add(payment)
        self.db.flush()
        return payment

    def create_order_status_history(
        self,
        *,
        order_id: int,
        changed_by: int | None,
        from_status: str | None,
        to_status: str,
        note: str | None,
    ) -> OrderStatusHistory:
        row = OrderStatusHistory(
            order_id=order_id,
            changed_by=changed_by,
            from_status=from_status,
            to_status=to_status,
            note=note,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def create_financial_invoice(
        self,
        *,
        invoice_number: str,
        order: Order,
    ) -> FinancialInvoice:
        invoice = FinancialInvoice(
            invoice_number=invoice_number,
            order_id=order.id,
            buyer_user_id=order.buyer_user_id,
            store_id=order.store_id,
            status=InvoiceStatus.PAYMENT_PENDING.value,
            currency=order.currency,
            subtotal_amount=order.subtotal_amount,
            discount_amount=order.discount_amount,
            shipping_amount=order.shipping_amount,
            total_amount=order.total_amount,
            platform_amount=order.commission_amount,
            provider_amount=order.seller_amount,
        )
        self.db.add(invoice)
        self.db.flush()
        return invoice

    def create_financial_invoice_item(
        self, *, invoice_id: int, order_item: OrderItem
    ) -> FinancialInvoiceItem:
        row = FinancialInvoiceItem(
            invoice_id=invoice_id,
            order_item_id=order_item.id,
            product_id=order_item.product_id,
            title_snapshot=order_item.product_name_snapshot,
            sku_snapshot=order_item.product_sku_snapshot,
            unit_snapshot=order_item.unit_snapshot,
            quantity=order_item.quantity,
            unit_price=order_item.unit_price,
            line_total=order_item.line_total,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def create_commission_snapshot(
        self,
        *,
        order: Order,
        invoice_id: int,
        commission_setting_id: int,
    ) -> CommissionSnapshot:
        row = CommissionSnapshot(
            order_id=order.id,
            invoice_id=invoice_id,
            commission_setting_id=commission_setting_id,
            calculation_type="percent",
            percent=order.commission_percent,
            base_amount=order.total_amount,
            platform_amount=order.commission_amount,
            provider_amount=order.seller_amount,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def create_inventory_reservation(
        self,
        *,
        order_item: OrderItem,
        expires_at: datetime,
    ) -> InventoryReservation:
        row = InventoryReservation(
            order_id=order_item.order_id,
            order_item_id=order_item.id,
            product_id=order_item.product_id,
            quantity=order_item.quantity,
            status=InventoryReservationStatus.RESERVED.value,
            expires_at=expires_at,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def create_payment_attempt(
        self,
        *,
        invoice: FinancialInvoice,
        payment: Payment,
        idempotency_key: str,
        expires_at: datetime,
    ) -> PaymentAttempt:
        row = PaymentAttempt(
            invoice_id=invoice.id,
            order_id=invoice.order_id,
            user_id=invoice.buyer_user_id,
            legacy_payment_id=payment.id,
            provider="mock",
            status=PaymentAttemptStatus.CREATED.value,
            amount=invoice.total_amount,
            currency=invoice.currency,
            idempotency_key=idempotency_key,
            expires_at=expires_at,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def get_invoice_by_order(self, *, order_id: int) -> FinancialInvoice | None:
        return (
            self.db.query(FinancialInvoice)
            .filter(FinancialInvoice.order_id == order_id)
            .one_or_none()
        )

    def get_payment_attempt_by_legacy_payment(self, *, payment_id: int) -> PaymentAttempt | None:
        return (
            self.db.query(PaymentAttempt)
            .filter(PaymentAttempt.legacy_payment_id == payment_id)
            .with_for_update()
            .one_or_none()
        )

    def consume_order_reservations(self, *, order_id: int, now: datetime) -> int:
        rows = (
            self.db.query(InventoryReservation)
            .filter(
                InventoryReservation.order_id == order_id,
                InventoryReservation.status == InventoryReservationStatus.RESERVED.value,
            )
            .order_by(InventoryReservation.product_id.asc())
            .with_for_update()
            .all()
        )
        for row in rows:
            row.status = InventoryReservationStatus.CONSUMED.value
            row.consumed_at = now
        self.db.flush()
        return len(rows)

    def release_order_inventory(
        self,
        *,
        order_id: int,
        now: datetime,
        reason: str,
        include_consumed: bool = False,
    ) -> int:
        statuses = [InventoryReservationStatus.RESERVED.value]
        if include_consumed:
            statuses.append(InventoryReservationStatus.CONSUMED.value)
        rows = (
            self.db.query(InventoryReservation)
            .filter(
                InventoryReservation.order_id == order_id,
                InventoryReservation.status.in_(statuses),
            )
            .order_by(InventoryReservation.product_id.asc())
            .with_for_update()
            .all()
        )
        products = self.lock_products_by_ids(product_ids=[row.product_id for row in rows])
        for row in rows:
            product = products.get(row.product_id)
            if product is not None:
                product.stock_quantity += row.quantity
            row.status = InventoryReservationStatus.RELEASED.value
            row.released_at = now
            row.release_reason = reason
        self.db.flush()
        return len(rows)

    def create_payment_transaction(
        self,
        *,
        invoice: FinancialInvoice,
        attempt: PaymentAttempt,
        provider_reference: str,
    ) -> FinancialTransaction:
        row = FinancialTransaction(
            invoice_id=invoice.id,
            order_id=invoice.order_id,
            payment_attempt_id=attempt.id,
            transaction_type=FinancialTransactionType.PAYMENT.value,
            status=FinancialTransactionStatus.SUCCEEDED.value,
            amount=invoice.total_amount,
            currency=invoice.currency,
            provider=attempt.provider,
            provider_reference=provider_reference,
            idempotency_key=f"payment-attempt:{attempt.id}:succeeded",
            description="Mock payment transaction",
        )
        self.db.add(row)
        self.db.flush()
        return row

    def list_my_orders(
        self,
        *,
        buyer_user_id: int,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Order], int]:
        query = self.db.query(Order).filter(
            Order.buyer_user_id == buyer_user_id,
            Order.deleted_at.is_(None),
        )

        if status:
            query = query.filter(Order.status == status)

        total = query.count()

        items = (
            query.order_by(Order.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return items, total

    def get_my_order_by_id(
        self,
        *,
        buyer_user_id: int,
        order_id: int,
    ) -> Order | None:
        return (
            self.db.query(Order)
            .filter(
                Order.id == order_id,
                Order.buyer_user_id == buyer_user_id,
                Order.deleted_at.is_(None),
            )
            .one_or_none()
        )

    def list_order_items(self, *, order_id: int) -> list[OrderItem]:
        return (
            self.db.query(OrderItem)
            .filter(OrderItem.order_id == order_id)
            .order_by(OrderItem.id.asc())
            .all()
        )

    def list_order_payments(self, *, order_id: int) -> list[Payment]:
        return (
            self.db.query(Payment)
            .filter(Payment.order_id == order_id)
            .order_by(Payment.created_at.asc(), Payment.id.asc())
            .all()
        )

    def list_order_status_history(
        self,
        *,
        order_id: int,
    ) -> list[OrderStatusHistory]:
        return (
            self.db.query(OrderStatusHistory)
            .filter(OrderStatusHistory.order_id == order_id)
            .order_by(OrderStatusHistory.created_at.asc(), OrderStatusHistory.id.asc())
            .all()
        )

    def list_my_payments(
        self,
        *,
        user_id: int,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Payment], int]:
        query = self.db.query(Payment).filter(Payment.user_id == user_id)

        if status:
            query = query.filter(Payment.status == status)

        total = query.count()

        items = (
            query.order_by(Payment.created_at.desc(), Payment.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return items, total

    def get_my_payment_by_id(
        self,
        *,
        user_id: int,
        payment_id: int,
    ) -> Payment | None:
        return (
            self.db.query(Payment)
            .filter(
                Payment.id == payment_id,
                Payment.user_id == user_id,
            )
            .one_or_none()
        )

    def get_order_by_id(self, *, order_id: int) -> Order | None:
        return (
            self.db.query(Order)
            .filter(
                Order.id == order_id,
                Order.deleted_at.is_(None),
            )
            .one_or_none()
        )

    def list_seller_orders(
        self,
        *,
        seller_user_id: int,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Order], int]:
        query = (
            self.db.query(Order)
            .join(Store, Store.id == Order.store_id)
            .filter(
                Store.owner_user_id == seller_user_id,
                Store.deleted_at.is_(None),
                Order.deleted_at.is_(None),
            )
        )

        if status:
            query = query.filter(Order.status == status)

        total = query.count()

        items = (
            query.order_by(Order.created_at.desc(), Order.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return items, total

    def get_seller_order_by_id(
        self,
        *,
        seller_user_id: int,
        order_id: int,
    ) -> Order | None:
        return (
            self.db.query(Order)
            .join(Store, Store.id == Order.store_id)
            .filter(
                Order.id == order_id,
                Store.owner_user_id == seller_user_id,
                Store.deleted_at.is_(None),
                Order.deleted_at.is_(None),
            )
            .one_or_none()
        )

    def list_admin_orders(
        self,
        *,
        status: str | None = None,
        payment_status: str | None = None,
        store_id: int | None = None,
        buyer_user_id: int | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Order], int]:
        query = self.db.query(Order).filter(
            Order.deleted_at.is_(None),
        )

        if status:
            query = query.filter(Order.status == status)

        if payment_status:
            query = query.filter(Order.payment_status == payment_status)

        if store_id:
            query = query.filter(Order.store_id == store_id)

        if buyer_user_id:
            query = query.filter(Order.buyer_user_id == buyer_user_id)

        total = query.count()

        items = (
            query.order_by(Order.created_at.desc(), Order.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return items, total

    def get_admin_order_by_id(self, *, order_id: int) -> Order | None:
        return (
            self.db.query(Order)
            .filter(
                Order.id == order_id,
                Order.deleted_at.is_(None),
            )
            .one_or_none()
        )

    def list_commission_settings(self) -> list[CommissionSetting]:
        return (
            self.db.query(CommissionSetting)
            .order_by(
                CommissionSetting.is_default.desc(),
                CommissionSetting.created_at.desc(),
                CommissionSetting.id.desc(),
            )
            .all()
        )

    def get_default_commission_setting(self) -> CommissionSetting | None:
        return (
            self.db.query(CommissionSetting)
            .filter(
                CommissionSetting.status == CommissionSettingStatus.ACTIVE.value,
                CommissionSetting.is_default.is_(True),
            )
            .one_or_none()
        )

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    def refresh(self, instance) -> None:
        self.db.refresh(instance)

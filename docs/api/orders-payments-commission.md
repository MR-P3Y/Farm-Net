# Farm Net API - Orders / Payments / Commission Foundation

This document describes Phase 9 APIs.

Base path:

```text
/api/v1
```

Phase 9 provides the first marketplace transaction foundation.

Implemented:

```text
Cart APIs
Checkout / Order Creation APIs
Mock Payment APIs
Seller Order APIs
Admin Order APIs
Commission Settings Admin APIs
Flutter Mobile Cart / Orders Foundation
Admin Panel Orders / Commission Foundation
```

Not implemented yet:

```text
Real online payment gateway
Card-to-card receipt flow
Wallet / settlement
Refund money transfer
Invoice PDF
Shipping provider integration
Advanced stock reservation
Discount/coupon integration
```

---

## Business Rules

Farm Net is a marketplace. A cart can contain products from multiple stores.

At checkout:

```text
Cart items are grouped by store_id.
One order is created per store.
Each order has its own items, payment, status history, commission snapshot.
```

Commission settings are editable by admin, but existing orders are not recalculated.

```text
commission_percent
commission_amount
seller_amount
```

are snapshotted inside each order at checkout time.

---

# Cart APIs

Cart permissions:

```text
cart.read
cart.update
```

## Get my cart

```http
GET /api/v1/cart/me
```

Creates an active empty cart if the user does not have one.

Response includes:

```text
items
items_count
subtotal_amount
```

---

## Add item to cart

```http
POST /api/v1/cart/items
```

Request:

```json
{
  "product_id": 1,
  "quantity": 1
}
```

Rules:

```text
Product must be published.
Product must be active.
Product must not be deleted.
Store must be approved.
Quantity must respect stock/min/max order limits.
If the product already exists in cart, quantity is increased.
```

---

## Update cart item

```http
PATCH /api/v1/cart/items/{item_id}
```

Request:

```json
{
  "quantity": 3
}
```

---

## Delete cart item

```http
DELETE /api/v1/cart/items/{item_id}
```

---

## Clear cart

```http
DELETE /api/v1/cart/clear
```

---

# Checkout / Buyer Orders

Buyer order permissions:

```text
orders.read
orders.create
orders.cancel
```

## Checkout

```http
POST /api/v1/checkout
```

Request:

```json
{
  "buyer_note": "Please call before delivery",
  "shipping_address": "Test address",
  "shipping_postal_code": "1234567890",
  "shipping_phone": "09120000000"
}
```

Rules:

```text
Active cart must exist.
Cart must not be empty.
Products are revalidated before checkout.
Cart items are grouped by store_id.
One order is created per store.
One pending mock payment is created per order.
Order starts as pending_payment.
Payment starts as pending.
Cart becomes checked_out.
A new empty active cart is created next time /cart/me is called.
```

Response:

```json
{
  "orders": [],
  "orders_count": 1,
  "total_amount": "260000.00"
}
```

---

## List my orders

```http
GET /api/v1/orders/me
```

Filters:

```text
status
page
page_size
```

---

## Get my order

```http
GET /api/v1/orders/{order_id}
```

Response includes:

```text
items
payments
status_history
commission_percent
commission_amount
seller_amount
```

---

# Payment APIs

Payment permissions:

```text
payments.read
payments.create
```

## List my payments

```http
GET /api/v1/payments/me
```

Filters:

```text
status
page
page_size
```

---

## Get my payment

```http
GET /api/v1/payments/{payment_id}
```

---

## Mock pay

```http
POST /api/v1/payments/{payment_id}/mock/pay
```

Allowed only when:

```text
payment.status = pending
```

Effects:

```text
payment.status = paid
payment.paid_at = now
payment.provider_reference = MOCK-PAID-{id}

order.payment_status = paid
order.status = paid
order.paid_at = now

order_status_history is created
```

---

## Mock fail

```http
POST /api/v1/payments/{payment_id}/mock/fail
```

Request:

```json
{
  "reason": "Mock failure smoke test"
}
```

Effects:

```text
payment.status = failed
payment.failed_at = now
payment.failure_reason = reason

order.payment_status = failed
order.status remains pending_payment
```

Reason:

```text
The buyer may retry payment later.
```

---

# Seller Order APIs

Seller permissions:

```text
orders.seller_read
orders.seller_update
```

## List seller orders

```http
GET /api/v1/seller/orders
```

Filters:

```text
status
page
page_size
```

Current MVP seller access rule:

```text
store.owner_user_id == current_user.id
```

Future extension:

```text
store_members manager/staff permissions
```

---

## Get seller order

```http
GET /api/v1/seller/orders/{order_id}
```

---

## Update seller order status

```http
PATCH /api/v1/seller/orders/{order_id}/status
```

Request:

```json
{
  "status": "confirmed",
  "seller_note": "Seller confirmed order"
}
```

Allowed transitions:

| From       | To         |
| ---------- | ---------- |
| paid       | confirmed  |
| confirmed  | processing |
| processing | shipped    |
| shipped    | delivered  |

Seller cannot change payment status.

Seller cannot update unpaid orders.

---

# Admin Order APIs

Admin permissions:

```text
orders.admin_read
orders.admin_update
```

## List admin orders

```http
GET /api/v1/admin/orders
```

Filters:

```text
status
payment_status
store_id
buyer_user_id
page
page_size
```

---

## Get admin order

```http
GET /api/v1/admin/orders/{order_id}
```

Response includes:

```text
items
payments
status_history
buyer/store/order financial fields
```

---

## Update admin order status

```http
PATCH /api/v1/admin/orders/{order_id}/status
```

Request:

```json
{
  "status": "cancelled",
  "admin_note": "Admin cancelled order"
}
```

Allowed transitions:

| From            | To        |
| --------------- | --------- |
| pending_payment | cancelled |
| paid            | cancelled |
| confirmed       | cancelled |
| processing      | cancelled |
| delivered       | refunded  |

Refund in Phase 9:

```text
order.status = refunded
order.payment_status = refunded
```

Actual money movement is not implemented yet.

---

# Commission Settings APIs

Commission permissions:

```text
commission.read
commission.update
```

## List commission settings

```http
GET /api/v1/admin/commission/settings
```

---

## Get default commission setting

```http
GET /api/v1/admin/commission/settings/default
```

---

## Update default commission setting

```http
PATCH /api/v1/admin/commission/settings/default
```

Request:

```json
{
  "percent": 5.00,
  "description": "Default commission used for new orders"
}
```

Rules:

```text
percent must be between 0 and 100.
Only new orders use the new percent.
Existing orders keep their snapshot.
seed_orders must not reset admin-managed percent.
```

---

# Order Statuses

```text
pending_payment
paid
confirmed
processing
shipped
delivered
cancelled
refunded
```

---

# Payment Statuses

```text
pending
paid
failed
cancelled
refunded
```

---

# Phase 9 UI Foundations

## Flutter Mobile

Implemented:

```text
Cart screen
Add product to cart from product detail
Update quantity
Delete item
Clear cart
Checkout
My orders
Order detail
Mock payment
```

## Admin Panel

Implemented:

```text
Orders page
Order detail dialog
Status/payment filters
Cancel/refund foundation
Commission page
Update default commission percent
```

Note:

```text
Full browser UI smoke may depend on Flutter Web renderer reliability.
Build, route, and API smoke are the primary verification for this foundation phase.
```

---

# Known Limitations

```text
No real payment gateway yet
No wallet/settlement yet
No stock reservation yet
No shipment provider integration yet
No invoice generation yet
No card-to-card receipt flow yet
No retry payment API yet
No seller staff/manager order management yet
```

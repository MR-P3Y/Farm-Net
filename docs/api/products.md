# Farm Net API - Product / Catalog Foundation

This document describes Phase 8 Product / Catalog Foundation APIs.

Base path:

```text
/api/v1
```

Phase 8 provides product catalog infrastructure only.

Implemented in this phase:

```text
Product categories
Seller product APIs
Product image metadata APIs
Admin product moderation APIs
Public product lookup APIs
Flutter Mobile Product Foundation
Admin Panel Product Foundation
```

Not implemented in this phase:

```text
Cart
Orders
Payments
Commission calculation
Shipment/delivery
Real file upload
Product comments/reviews
Discounts/coupons
Advanced inventory
```

---

## Product Responsibility Model

Products do not require admin approval.

The legal/business model is:

```text
Seller submits legal documents.
Seller signs/accepts legal agreement.
Store gets approved by admin.
After store approval, seller is legally responsible for listed products.
Admin only moderates violations.
```

So the admin does not approve/reject each product.

Admin can only:

```text
suspend product
restore suspended product
inspect product details
```

---

## Product Statuses

```text
draft
published
unpublished
suspended
archived
```

Meaning:

```text
draft        Seller is preparing the product.
published    Product is public.
unpublished  Seller temporarily hides product.
suspended    Admin disabled product due to violation.
archived     Seller soft-deleted/archived product.
```

Allowed seller transitions:

```text
draft -> published
unpublished -> published
published -> unpublished
draft/published/unpublished -> archived
```

Allowed admin moderation transitions:

```text
published -> suspended
unpublished -> suspended
suspended -> published
suspended -> unpublished
```

Admin cannot use:

```text
approved
rejected
```

because product approval is not part of this business model.

---

## Public Visibility Rules

A product is visible publicly only when:

```text
product.status = published
product.deleted_at IS NULL
product.is_active = true
store.status = approved
store.deleted_at IS NULL
```

Hidden from public:

```text
draft
unpublished
suspended
archived
deleted
products of non-approved stores
```

Public responses must not expose:

```text
admin_note
suspended_by
suspended_at
status_history
owner private data
```

---

## Product Permissions

Seller permissions:

```text
products.read
products.create
products.update
products.delete
products.publish
products.unpublish
products.manage_images
```

Admin permissions:

```text
products.admin_read
products.suspend
products.restore
```

Public permission:

```text
products.public_read
```

Role mapping:

```text
shop_owner: seller product permissions
admin: admin moderation permissions
super_admin: all permissions
support: no product permissions in Phase 8
```

---

# Product Categories

Seeded category tree includes:

```text
بذر
کود
سموم
تجهیزات
نهاده‌ها
```

Categories are currently seeded by backend script.

Manual category management from Admin Panel is not part of Phase 8.

Future step:

```text
Admin Category Management Foundation
```

---

# Seller Product APIs

Seller product APIs require authentication and seller product permissions.

## Create product

```http
POST /api/v1/stores/{store_id}/products
```

Required permission:

```text
products.create
```

Rules:

```text
Store must belong to current user.
Store must be approved.
Initial product status is draft.
Slug is unique per store.
SKU is unique per store when provided.
```

Request:

```json
{
  "category_id": 1,
  "name": "Farm Net Test Product",
  "slug": "farmnet-test-product",
  "short_description": "Short product description",
  "description": "Full product description",
  "sku": "SKU-001",
  "price": 250000,
  "compare_at_price": 300000,
  "currency": "TOMAN",
  "stock_quantity": 100,
  "unit": "kg",
  "min_order_quantity": 1,
  "max_order_quantity": 50,
  "is_active": true,
  "is_featured": false
}
```

Response:

```json
{
  "success": true,
  "data": {
    "id": 1,
    "store_id": 1,
    "category_id": 1,
    "name": "Farm Net Test Product",
    "slug": "farmnet-test-product",
    "status": "draft",
    "price": "250000.00",
    "currency": "TOMAN"
  },
  "message": "Product created",
  "meta": {
    "trace_id": "..."
  }
}
```

---

## List my products

```http
GET /api/v1/stores/{store_id}/products/me
```

Required permission:

```text
products.read
```

Filters:

```text
status
category_id
q
page
page_size
```

---

## Get my product detail

```http
GET /api/v1/stores/{store_id}/products/{product_id}
```

Required permission:

```text
products.read
```

---

## Update product

```http
PUT /api/v1/stores/{store_id}/products/{product_id}
```

Required permission:

```text
products.update
```

Rules:

```text
Suspended products cannot be updated by seller.
Archived products cannot be updated.
Slug/SKU conflicts are rejected.
```

---

## Publish product

```http
POST /api/v1/stores/{store_id}/products/{product_id}/publish
```

Required permission:

```text
products.publish
```

Allowed from:

```text
draft
unpublished
```

Result:

```text
status = published
```

---

## Unpublish product

```http
POST /api/v1/stores/{store_id}/products/{product_id}/unpublish
```

Required permission:

```text
products.unpublish
```

Allowed from:

```text
published
```

Result:

```text
status = unpublished
```

---

## Archive product

```http
DELETE /api/v1/stores/{store_id}/products/{product_id}
```

Required permission:

```text
products.delete
```

This is a soft delete:

```text
status = archived
deleted_at != null
```

Suspended products cannot be archived by seller.

---

## Product status history

```http
GET /api/v1/stores/{store_id}/products/{product_id}/status-history
```

Required permission:

```text
products.read
```

---

# Product Image Metadata APIs

These APIs manage image metadata only. They do not upload real files.

## Add product image

```http
POST /api/v1/stores/{store_id}/products/{product_id}/images
```

Required permission:

```text
products.manage_images
```

Request:

```json
{
  "file_id": "test-file-001",
  "file_path": "products/1/main.jpg",
  "alt_text": "Main product image",
  "sort_order": 10,
  "is_primary": true
}
```

Rule:

```text
If is_primary=true, all other images of the same product become is_primary=false.
```

---

## List product images

```http
GET /api/v1/stores/{store_id}/products/{product_id}/images
```

Required permission:

```text
products.read
```

---

## Update product image

```http
PATCH /api/v1/stores/{store_id}/products/{product_id}/images/{image_id}
```

Required permission:

```text
products.manage_images
```

---

## Delete product image

```http
DELETE /api/v1/stores/{store_id}/products/{product_id}/images/{image_id}
```

Required permission:

```text
products.manage_images
```

---

# Admin Product Moderation APIs

Admin product APIs require admin product permissions.

## List products

```http
GET /api/v1/admin/products?page=1&page_size=20
```

Required permission:

```text
products.admin_read
```

Filters:

```text
status
store_id
category_id
q
page
page_size
```

---

## Get product detail

```http
GET /api/v1/admin/products/{product_id}
```

Required permission:

```text
products.admin_read
```

The detail response includes:

```text
store info
owner info
category info
images
status_history
admin_note
suspended metadata
```

---

## Update product status

```http
PATCH /api/v1/admin/products/{product_id}/status
```

Request:

```json
{
  "status": "suspended",
  "note": "Policy violation"
}
```

Permission by target status:

| Target Status | Required Permission |
| ------------- | ------------------- |
| suspended     | products.suspend    |
| published     | products.restore    |
| unpublished   | products.restore    |

Allowed transitions:

| From        | To          |
| ----------- | ----------- |
| published   | suspended   |
| unpublished | suspended   |
| suspended   | published   |
| suspended   | unpublished |

Invalid:

```text
approved
rejected
draft -> suspended
archived -> suspended
```

---

# Public Product APIs

Public product APIs require no authentication.

## List public products

```http
GET /api/v1/public/products
```

Filters:

```text
q
store_id
category_id
province_id
county_id
city_id
store_type
page
page_size
```

---

## Get public product by ID

```http
GET /api/v1/public/products/{product_id}
```

Only published products of approved stores are visible.

---

## List products of public store

```http
GET /api/v1/public/stores/{store_slug}/products
```

Filters:

```text
q
category_id
page
page_size
```

---

## Get product by store slug and product slug

```http
GET /api/v1/public/stores/{store_slug}/products/{product_slug}
```

This route exists because product slug is unique only inside a store:

```text
UNIQUE(store_id, slug)
```

So this is correct:

```text
/store-slug/product-slug
```

and this is not globally reliable:

```text
/products/{slug}
```

---

# Phase 8 UI Foundations

## Flutter Mobile

Implemented:

```text
Public products list
Public product detail
Store products list
My products
Create/edit product
Publish/unpublish product
Primary image display foundation
```

## Admin Panel

Implemented:

```text
Admin products list
Status filter
Product detail dialog
Images display
Status history display
Suspend/restore actions
```

Note:

```text
Admin Panel full browser smoke may depend on Flutter Web renderer reliability.
Build, routes, and API smoke are the source of truth for this phase.
```

---

# Known Limitations

```text
No real file upload yet
No cart/order/payment yet
No commission calculation yet
No manual category management UI yet
No advanced inventory management yet
No product reviews/comments yet
No discount/coupon support yet
```

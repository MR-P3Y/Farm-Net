# Farm Net API - Store Foundation

This document describes Phase 7 Store Foundation APIs.

Base path:

```text
/api/v1
```

Phase 7 provides store infrastructure only. Product catalog, product categories, cart, orders, payment, and commission are not part of this phase.

---

## Store Foundation Scope

Implemented in Phase 7:

```text
Store database models
Store owner/member structure
Store status lifecycle
Seller store APIs
Store member management APIs
Admin store review APIs
Public approved store lookup APIs
Mobile Store foundation
Admin Panel Store foundation
```

Not implemented in Phase 7:

```text
Store products
Product categories
Store/product category tree
Cart
Orders
Payments
Commission calculation
Real logo/banner upload
Private media serving
```

---

## Store Statuses

Allowed store statuses:

```text
draft
pending_review
approved
rejected
suspended
closed
```

### Seller status flow

```text
draft -> pending_review
rejected -> pending_review
```

Seller creates a store as `draft`, completes required data, then submits it for admin review.

### Admin status flow

```text
pending_review -> approved
pending_review -> rejected
approved -> suspended
suspended -> approved
```

Rejected stores must be fixed by the seller and submitted again. Admin should not directly move `rejected` to `approved`.

---

## Store Types

Current simple `store_type` values:

```text
agriculture_inputs
equipment
seeds
fertilizer
pesticide
mixed
other
```

Important: this is not the final category system. Real categories will be implemented later.

---

## Store Permissions

### Seller permissions

```text
stores.read
stores.create
stores.update
stores.submit
stores.manage_members
```

### Admin permissions

```text
stores.admin_read
stores.admin_review
stores.approve
stores.reject
stores.suspend
```

### Super admin

Super admin receives all store permissions.

---

# Seller Store APIs

Seller APIs require authentication.

## Create store

```http
POST /api/v1/stores
```

Required permission:

```text
stores.create
```

Rules:

```text
Only users with stores.create can create a store.
Each user can have only one non-deleted store.
Initial status is draft.
Slug must be unique.
```

Request:

```json
{
  "name": "Farm Net Test Store",
  "slug": "farmnet-test-store",
  "description": "Test store",
  "store_type": "mixed",
  "phone": "989120000000",
  "email": "store@example.com",
  "province_id": 1,
  "county_id": 5,
  "district_id": 222,
  "city_id": 10,
  "village_id": null,
  "address": "Test address",
  "postal_code": "1234567890",
  "latitude": 35.6892,
  "longitude": 51.389
}
```

Response:

```json
{
  "success": true,
  "data": {
    "id": 1,
    "owner_user_id": 1,
    "name": "Farm Net Test Store",
    "slug": "farmnet-test-store",
    "status": "draft",
    "store_type": "mixed"
  },
  "message": "Store created",
  "meta": {
    "trace_id": "..."
  }
}
```

---

## Get my store

```http
GET /api/v1/stores/me
```

Required permission:

```text
stores.read
```

Returns current user store or `null`.

---

## Get own store by ID

```http
GET /api/v1/stores/{store_id}
```

Required permission:

```text
stores.read
```

Users can only access their own store through this endpoint.

---

## Update own store

```http
PUT /api/v1/stores/{store_id}
```

Required permission:

```text
stores.update
```

Allowed current statuses:

```text
draft
rejected
approved
```

Geo validation rules:

```text
county_id must belong to province_id
district_id must belong to county_id/province_id
city_id must belong to county_id/province_id
village_id must belong to county_id/province_id
```

---

## Submit store for review

```http
POST /api/v1/stores/{store_id}/submit
```

Required permission:

```text
stores.submit
```

Allowed current statuses:

```text
draft
rejected
```

Required fields before submit:

```text
name
slug
province_id
county_id
address
```

Result:

```text
status = pending_review
```

A row is inserted in `store_status_history`.

---

## Get store status history

```http
GET /api/v1/stores/{store_id}/status-history
```

Only the owner can see their store status history.

---

# Store Member APIs

Store member APIs require:

```text
stores.manage_members
```

Only the store owner can manage members.

## List members

```http
GET /api/v1/stores/{store_id}/members
```

---

## Add member

```http
POST /api/v1/stores/{store_id}/members
```

Request:

```json
{
  "user_id": 2,
  "role": "staff"
}
```

Allowed roles for added members:

```text
manager
staff
viewer
```

Rules:

```text
owner role cannot be assigned manually.
target user must exist.
same user cannot be active twice in one store.
removed member can be reactivated.
```

---

## Update member

```http
PATCH /api/v1/stores/{store_id}/members/{member_id}
```

Request:

```json
{
  "role": "manager",
  "status": "active"
}
```

Allowed statuses:

```text
active
suspended
removed
```

Rules:

```text
owner member cannot be modified.
```

---

## Remove member

```http
DELETE /api/v1/stores/{store_id}/members/{member_id}
```

This is soft removal:

```text
status = removed
```

Owner member cannot be removed.

---

# Admin Store APIs

Admin APIs require authentication and admin store permissions.

## List stores

```http
GET /api/v1/admin/stores?page=1&page_size=20
```

Required permission:

```text
stores.admin_read
```

Filters:

```text
status
owner_user_id
q
page
page_size
```

Example:

```http
GET /api/v1/admin/stores?status=pending_review
```

---

## Get store detail

```http
GET /api/v1/admin/stores/{store_id}
```

Required permission:

```text
stores.admin_read
```

The detail response includes:

```text
owner email/phone
members
status_history
admin_note
approved/rejected metadata
```

---

## Update store status

```http
PATCH /api/v1/admin/stores/{store_id}/status
```

Request:

```json
{
  "status": "approved",
  "note": "Approved by admin"
}
```

Permission by target status:

| Status    | Required Permission |
| --------- | ------------------- |
| approved  | stores.approve      |
| rejected  | stores.reject       |
| suspended | stores.suspend      |

Allowed transitions:

| From           | To        |
| -------------- | --------- |
| pending_review | approved  |
| pending_review | rejected  |
| approved       | suspended |
| suspended      | approved  |

Every status change creates a row in:

```text
store_status_history
```

---

# Public Store APIs

Public endpoints require no authentication.

Only stores with the following conditions are visible:

```text
status = approved
deleted_at IS NULL
```

Hidden from public:

```text
draft
pending_review
rejected
suspended
closed
deleted
```

---

## List public stores

```http
GET /api/v1/public/stores
```

Filters:

```text
q
province_id
county_id
city_id
store_type
sort = relevance | newest
page
page_size
```

Search text uses the shared Persian normalizer. Relevance is title-first and
never weakens the approved/non-deleted public visibility boundary.

Examples:

```http
GET /api/v1/public/stores
GET /api/v1/public/stores?store_type=mixed
GET /api/v1/public/stores?province_id=1
GET /api/v1/public/stores?q=بذر
```

Public response does not expose sensitive fields:

```text
status
admin_note
approved_by
rejected_by
members
status_history
```

---

## Get public store by slug

```http
GET /api/v1/public/stores/{slug}
```

Returns approved public store detail.

Non-approved stores are not visible through this endpoint.

---

# Phase 7 UI Foundations

## Mobile

Implemented:

```text
Public store list
Public store detail
My store page
Create/edit store foundation
Submit store foundation
```

## Admin Panel

Implemented:

```text
Admin store list
Status filter
Store detail dialog
Members display
Status history display
Approve/reject/suspend actions
```

---

# Known Test Data Note

Some early test store records may contain mojibake or `???` in Persian fields because they were inserted with a bad console/encoding path.

This is test data only. The UI and API support UTF-8 correctly when data is inserted properly.

# Farm Net API - Profile / Documents / Verification

This document describes Phase 6 APIs for user profile, document metadata, verification requests, and admin verification review.

Base path:

```text
/api/v1
```

Authentication:

```http
Authorization: Bearer <access_token>
```

---

## Profile APIs

### Get my profile

```http
GET /api/v1/profile/me
```

If the user has no profile yet, the API returns an empty profile payload with `profile_completed=false` instead of 404.

Response:

```json
{
  "success": true,
  "data": {
    "id": null,
    "user_id": 1,
    "first_name": null,
    "last_name": null,
    "display_name": null,
    "national_id": null,
    "birth_date": null,
    "gender": null,
    "province_id": null,
    "county_id": null,
    "district_id": null,
    "rural_district_id": null,
    "city_id": null,
    "village_id": null,
    "address": null,
    "postal_code": null,
    "avatar_file_id": null,
    "avatar_url": null,
    "bio": null,
    "profile_completed": false
  },
  "message": "OK",
  "meta": {
    "trace_id": "..."
  }
}
```

### Replace my profile

```http
PUT /api/v1/profile/me
```

`PUT` keeps the original full-replacement contract. Clients editing only part
of a profile should use the non-destructive operation below so fields they do
not manage (for example lower-level Geo data or an avatar reference) remain
unchanged.

### Partially update my profile

```http
PATCH /api/v1/profile/me
```

`PATCH` only changes fields explicitly included in the request. A National ID
already linked to another account returns HTTP `409` with error code
`PROFILE_NATIONAL_ID_CONFLICT`; every account, including test accounts, must
use a distinct National ID.

Only keys explicitly present in the request are changed. An explicit `null`
clears a nullable field; an omitted key preserves its current value.

Request:

```json
{
  "first_name": "Peyman",
  "last_name": "FarmNet",
  "display_name": "Peyman FarmNet",
  "national_id": "1234567890",
  "birth_date": "1995-01-01",
  "gender": "male",
  "province_id": 1,
  "county_id": 5,
  "district_id": 222,
  "city_id": 10,
  "address": "Test address",
  "postal_code": "1234567890",
  "avatar_file_id": "owned-profile-image-file-key",
  "bio": "Farm Net test profile"
}
```

Validation rules:

* `gender`: `male`, `female`, `other`
* `national_id`: 10 digits if provided
* `postal_code`: 10 digits if provided
* `birth_date`: cannot be in the future
* `avatar_file_id` is a Media `file_key`, not a path or numeric Media ID.
* An avatar must be active, public, uploaded with `purpose=profile_image`, and
  owned by the current user. Any other user's file is rejected.
* The response exposes `avatar_url` only while the referenced Media remains
  active and publicly accessible.
* Geo IDs must exist.
* Geo IDs must be consistent:
  * county must belong to province
  * district must belong to county/province
  * city must belong to county/province
  * village must belong to county/province/rural district when provided

`profile_completed=true` requires:

```text
first_name
last_name
national_id
province_id
county_id
address
```

---

## Document Metadata APIs

Actual file upload is not part of Phase 6. Phase 6 stores document metadata only.

### Create document metadata

```http
POST /api/v1/documents
```

Request:

```json
{
  "document_type": "national_card",
  "file_path": "storage/documents/users/1/national-card.jpg",
  "file_name": "national-card.jpg",
  "mime_type": "image/jpeg",
  "size_bytes": 345000
}
```

Allowed document types:

```text
national_card
business_license
agriculture_certificate
consultant_certificate
equipment_ownership
driver_license
contract_signed_pdf
other
```

Validation rules:

* `mime_type` must be `image/*` or `application/pdf`
* max file size metadata: 15 MB
* created documents start with `status=pending`

### List my documents

```http
GET /api/v1/documents/me
```

Deleted documents are not returned.

### Get my document

```http
GET /api/v1/documents/{document_id}
```

Users can only access their own documents.

### Delete my document

```http
DELETE /api/v1/documents/{document_id}
```

Deletion is soft delete using `deleted_at`.

---

## Verification Request APIs

### Create verification request

```http
POST /api/v1/verifications
```

Request:

```json
{
  "target_role": "consultant",
  "request_note": "درخواست تأیید مشاور کشاورزی"
}
```

Allowed target roles:

```text
shop_owner
lessor
consultant
service_provider
data_client
```

Initial status:

```text
draft
```

Active statuses:

```text
draft
submitted
under_review
needs_revision
```

A user cannot have more than one active request for the same `target_role`.

### List my verification requests

```http
GET /api/v1/verifications/me
```

### Get verification request detail

```http
GET /api/v1/verifications/{request_id}
```

Users can only access their own requests.

### Attach document to verification request

```http
POST /api/v1/verifications/{request_id}/documents
```

Request:

```json
{
  "document_id": 1
}
```

Rules:

* Request must belong to current user.
* Document must belong to current user.
* Document must not be soft-deleted.
* Request status must be `draft` or `needs_revision`.
* Rejected documents cannot be attached.

### Submit verification request

```http
POST /api/v1/verifications/{request_id}/submit
```

Rules:

* Request must belong to current user.
* Status must be `draft` or `needs_revision`.
* Profile must be completed.
* `national_id` must exist.
* At least one active document must be attached.

Submitted status:

```text
submitted
```

### Cancel verification request

```http
POST /api/v1/verifications/{request_id}/cancel
```

Request:

```json
{
  "note": "User cancelled the request"
}
```

Allowed statuses for cancel:

```text
draft
submitted
needs_revision
```

---

## Admin Verification APIs

Admin base path:

```text
/api/v1/admin/verifications
```

### List verification requests

```http
GET /api/v1/admin/verifications?page=1&page_size=20
```

Filters:

```text
status
target_role
user_id
```

Permission:

```text
verification.read
```

### Get verification detail

```http
GET /api/v1/admin/verifications/{request_id}
```

Permission:

```text
verification.read
```

### Update verification status

```http
PATCH /api/v1/admin/verifications/{request_id}/status
```

Request:

```json
{
  "status": "approved",
  "note": "Approved by admin"
}
```

Allowed admin statuses:

```text
under_review
needs_revision
approved
rejected
```

Permissions:

| Status         | Required Permission         |
| -------------- | --------------------------- |
| under_review   | verification.review         |
| needs_revision | verification.needs_revision |
| approved       | verification.approve        |
| rejected       | verification.reject         |

Rules:

* `approved`, `rejected`, and `cancelled` requests are locked.
* Approved requests cannot be changed again.
* Approval requires at least one active document.
* Every status change creates a verification review record.
* On approval, target role is automatically assigned to the user.

Role assignment mapping:

| target_role      | assigned role    |
| ---------------- | ---------------- |
| shop_owner       | shop_owner       |
| lessor           | lessor           |
| consultant       | consultant       |
| service_provider | service_provider |
| data_client      | data_client      |

---

## Phase 6 UI Foundations

Mobile:

```text
Geo lookup
Profile view/update
Document metadata creation
Verification request creation
Attach document
Submit request
List my verification requests
```

Admin Panel:

```text
List verification requests
Filter by status/target role
Open request detail
Review documents
Update status
Approve/reject requests
```

---

## Not Included in Phase 6

```text
Real file upload
Private file serving
Storage/S3 driver
Document download permission
Advanced admin document review UI
Geo admin management
```

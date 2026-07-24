# Marketplace Reviews API

Phase 19.4 exposes authenticated owner CRUD, public active Reviews, and the
canonical rating aggregate. Review reports, Admin moderation, and notifications
are not active in this contract.

Base path:

```text
/api/v1/reviews
```

## Permissions

| Permission | Use |
| --- | --- |
| `reviews.create` | Create an eligible Review |
| `reviews.read_own` | List/read own Reviews |
| `reviews.manage_own` | Update/delete own Reviews |

## Eligibility

The API accepts `source_type`, `source_id`, `subject_type`, and `subject_id` as
selectors. The Backend locks and reads the real source row, verifies the signed-
in user is its Buyer/Requester, verifies its terminal status, and compares the
selected subject with authoritative domain fields.

| Source | Required status | Allowed subjects |
| --- | --- | --- |
| `order` | `delivered` | purchased `product`; order `store` |
| `service_request` | `completed` | request `service_offer`; `service_provider` |
| `rental_request` | `completed` | request `rental_equipment`; `rental_lessor` |
| `consult_request` | `completed` | request `consultant` |

Self-review, wrong ownership, missing/incomplete source, unrelated target, and
duplicate source/subject Review are rejected. Client identity never overrides
the domain source.

## Create

```http
POST /api/v1/reviews
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{
  "source_type": "service_request",
  "source_id": 10,
  "subject_type": "service_provider",
  "subject_id": 4,
  "score": 5,
  "body": "خدمت دقیق و به‌موقع بود"
}
```

Score is an integer from 1 through 5. Body is optional, trimmed, empty-to-null,
and limited to 2000 characters. Success returns HTTP 201.

Creating a Review updates `rating_sum`, `reviews_count`, and two-decimal
`rating_average` in the same database transaction. Updating a score applies
only its delta; deleting an active Review removes its contribution. The legacy
Service Provider and Consultant rating columns are synchronized projections,
while the shared aggregate remains authoritative.

## List public Reviews and rating summary

```http
GET /api/v1/reviews/subjects/{subject_type}/{subject_id}?page=1&page_size=20
```

No authentication is required. The subject must currently be public/approved.
Only `active` Reviews are returned. Each item exposes score, optional body,
safe author display name, and timestamps; reviewer user ID, source identity,
contacts, reports, and moderation data are never public.

Pagination is returned in `meta`; `meta.rating` contains:

```json
{
  "subject_type": "product",
  "subject_id": 21,
  "rating_average": "4.50",
  "reviews_count": 2
}
```

Public Product, Store, Service Offer, and Rental Equipment discovery/detail
contracts expose the same canonical average/count. Rental Equipment also
includes its Lessor aggregate. Service Provider and Consultant discovery use
their atomically synchronized projections.

## List own

```http
GET /api/v1/reviews/me?page=1&page_size=20
GET /api/v1/reviews/me?status=active
Authorization: Bearer <token>
```

Owner history may filter by `active`, `hidden`, or `deleted`. Pagination metadata
contains `page`, `page_size`, `total`, and `total_pages`.

## Get own detail

```http
GET /api/v1/reviews/me/{review_id}
Authorization: Bearer <token>
```

Cross-user reads return `REVIEW_NOT_FOUND` instead of revealing existence.

## Update own

```http
PATCH /api/v1/reviews/me/{review_id}
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{
  "score": 4,
  "body": null
}
```

At least one field must be supplied. Only `active` Reviews are editable.
Explicit `body: null` clears the text. Source, subject, and reviewer identity
are immutable.

## Delete own

```http
DELETE /api/v1/reviews/me/{review_id}
Authorization: Bearer <token>
```

Delete is soft and idempotent. Owners may delete `active` or Admin-`hidden`
Reviews. A deleted Review cannot be recreated for the same source and subject.

## Error contracts

| Code | HTTP | Meaning |
| --- | --- | --- |
| `REVIEW_NOT_FOUND` | 404 | Own Review does not exist |
| `REVIEW_NOT_ELIGIBLE` | 422 | Source/status/subject/self-review is invalid |
| `REVIEW_ALREADY_EXISTS` | 409 | Review already exists |
| `REVIEW_INVALID_STATE` | 409 | Lifecycle disallows the change |
| `PERMISSION_DENIED` | 403 | Source is owned by another user or permission absent |

## Report a Review

```http
POST /api/v1/reviews/{review_id}/reports
Authorization: Bearer <token>
```

Reasons are `spam`, `abuse`, `harassment`, `privacy`, `fraud`, or `other`.
Description is optional and limited to 2000 characters. Only active public
Reviews are reportable. A reviewer cannot report their own Review, and each
user may report a Review only once. The owner response does not expose Admin
identity, resolution notes, or other reporters.

## Admin moderation

Dedicated permissions protect these contracts:

- `GET /api/v1/admin/reviews`
- `PATCH /api/v1/admin/reviews/{review_id}/status`
- `GET /api/v1/admin/reviews/{review_id}/moderation-logs`
- `GET /api/v1/admin/reviews/reports`
- `PATCH /api/v1/admin/reviews/reports/{report_id}/status`

All five Admin route groups publish explicit typed OpenAPI response envelopes
for Review/report lists and details plus moderation-log lists. These contracts
match the typed Admin client and do not expose raw persistence objects.

Review transitions are `active`, `hidden`, and terminal `deleted`. A required
note and durable audit event accompany each real transition. Hide/delete remove
an active Review from the canonical aggregate; restore adds it back atomically.
Reports move from `open` to `reviewed`, `resolved`, or `dismissed`, recording
Admin, resolution note, timestamp, and an audit event.

Additional errors:

| Code | HTTP | Meaning |
| --- | --- | --- |
| `REVIEW_REPORT_ALREADY_EXISTS` | 409 | Reporter already reported this Review |
| `REVIEW_REPORT_NOT_FOUND` | 404 | Admin report target does not exist |

## Notification and concurrency hardening

Step 19.6 emits exact-once notification events for a new Review report to
active users holding `review_reports.admin_read`, Review moderation to its
author, and report resolution to its reporter. Stable event keys derive from
the persisted report or moderation-log ID. Recipient/channel uniqueness
prevents duplicate delivery and the shared Notification service suppresses
self-notification.

Notification payloads exclude report descriptions, resolution notes, Review
body, contacts, source/order/request identity, and other reporter identities.

The first concurrent rating contribution uses a database savepoint and the
unique subject aggregate constraint. A competing insert reuses and locks the
winning aggregate row before applying its delta.

Unified Search reads the same canonical aggregate for Product, Store, and
Rental Equipment results. Service and Consultant Search results use their
synchronized canonical projections. A subject without an aggregate returns
`rating_average = 0.00` and `reviews_count = 0`; no placeholder row is created.

## Owner privacy

Owner responses contain generic source/subject identities, score/body/status,
capability flags, and timestamps. They do not expose Store/provider/lessor/
consultant owner user IDs, contact data, request notes, commercial snapshots,
Admin notes, reports, or moderation actor details.

## Runtime regression

With the Backend running locally:

```powershell
py -3 backend\scripts\reviews_runtime_regression.py --base-url http://localhost:8000
```

The command is read-only. It verifies app/database/Redis health, all ten Review
OpenAPI path groups, typed response references, seven subject and four source
types, public-schema privacy, unauthenticated owner/Admin boundaries, and the
public missing-subject contract. Authentication failures stop write requests
before any mutation.

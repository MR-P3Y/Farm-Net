# Equipment Rental API

Base prefix: `/api/v1`

Equipment Rental is independent from Product sale inventory and Services work.
All responses use the standard Farm-Net success/error envelope.

## Categories and lessor profiles (Phase 16.3)

| Method | Path | Access |
|---|---|---|
| GET | `/rentals/categories` | Public, active only |
| GET | `/rentals/me/lessor-profile` | `rental_lessors.profile_manage` |
| PUT | `/rentals/me/lessor-profile` | `rental_lessors.profile_manage` |
| POST | `/rentals/me/lessor-profile/submit` | `rental_lessors.profile_manage` |
| GET | `/admin/rentals/categories` | `rental_categories.admin_read` |
| POST | `/admin/rentals/categories` | `rental_categories.create` |
| PATCH | `/admin/rentals/categories/{category_id}` | `rental_categories.update` |
| GET | `/admin/rentals/lessor-profiles` | `rental_lessors.admin_read` |
| PATCH | `/admin/rentals/lessor-profiles/{profile_id}/status` | `rental_lessors.admin_moderate` |

Profile editing is limited to `draft` and `rejected`. Submission requires
display name, phone, province, city, and address. Approval is allowed only from
`pending_review` and requires an approved Verification Request for target role
`lessor`. Rejection and suspension require an Admin note.

Category codes are stable lowercase identifiers. Parent clearing is explicit,
self-parenting and hierarchy cycles are rejected, and seeds create only missing
rows without overwriting Admin-owned values.

## Equipment listings and media (Phase 16.4)

| Method | Path | Access |
|---|---|---|
| GET | `/rentals/equipment` | Public approved listings |
| GET | `/rentals/equipment/{equipment_id}` | Public approved detail |
| GET | `/rentals/me/equipment` | Owner listing |
| POST | `/rentals/me/equipment` | Approved lessor |
| PUT | `/rentals/me/equipment/{equipment_id}` | Owning approved lessor |
| POST | `/rentals/me/equipment/{equipment_id}/submit` | Owning approved lessor |
| GET | `/admin/rentals/equipment` | `rental_equipment.admin_read` |
| PATCH | `/admin/rentals/equipment/{equipment_id}/status` | Status-specific moderation permission |

Owner media must be active, public, and owned by the same user. At most one
primary item is accepted and the first item becomes primary when omitted.
Public output excludes exact address, moderation notes, actor IDs, and internal
lifecycle timestamps. Public discovery requires both approved equipment and an
approved, non-deleted lessor profile.

## Pricing and availability (Phase 16.5)

| Method | Path | Access |
|---|---|---|
| GET | `/rentals/equipment/{equipment_id}/pricing` | Public active rules |
| GET | `/rentals/equipment/{equipment_id}/availability` | Public range check |
| GET/PUT | `/rentals/me/equipment/{equipment_id}/pricing` | Owning lessor |
| GET/POST | `/rentals/me/equipment/{equipment_id}/availability` | Owning lessor |
| PUT/DELETE | `/rentals/me/equipment/{equipment_id}/availability/{block_id}` | Owning lessor |

Pricing units are `hour`, `day`, `week`, `hectare`, and `project`. Operator
inclusion must match equipment operator mode. Replacing pricing is atomic,
requires at least one rule, and rejects duplicate unit/operator pairs.

Availability blocks are `unavailable`, `maintenance`, or `owner_reserved`.
Ranges use overlap semantics `existing.start < requested.end` and
`existing.end > requested.start`; adjacent ranges do not conflict. Blocks may
not overlap another block or an accepted/in-progress booking. Public checks do
not expose owner notes. Equipment approval now requires public media and at
least one active pricing rule.

## Rental requests and booking workflow (Phase 16.6)

| Method | Path | Access |
|---|---|---|
| POST | `/rentals/requests` | `rental_requests.create` |
| GET | `/rentals/requests/me` | Requester owner |
| GET | `/rentals/requests/me/{request_id}` | Requester owner |
| POST | `/rentals/requests/me/{request_id}/cancel` | Requester owner |
| GET | `/rentals/requests/assigned` | Approved assigned lessor |
| GET | `/rentals/requests/assigned/{request_id}` | Approved assigned lessor |
| PATCH | `/rentals/requests/assigned/{request_id}/status` | Approved assigned lessor |
| GET | `/admin/rentals/requests` | `rental_requests.admin_read` |
| GET | `/admin/rentals/requests/{request_id}` | `rental_requests.admin_read` |
| PATCH | `/admin/rentals/requests/{request_id}/status` | `rental_requests.admin_manage` |

Requests begin at `pending`. Lessors may accept/reject, start an accepted
booking, and complete an in-progress booking. Requesters may cancel only
`pending` or `accepted`. Acceptance locks the equipment row, rechecks active
pricing, blocks, and accepted/in-progress overlap, then snapshots price per
unit, rental amount, deposit, total, and currency. No payment is claimed.

Each transition writes a unique deterministic status-log event. Requester and
lessor contracts omit `admin_note`; only the Admin detail contract exposes it.

## Notifications and concurrency (Phase 16.7)

Request creation notifies the assigned lessor. Accepted, rejected,
`in_progress`, completed, and cancelled transitions notify the opposite booking
party; Admin actions notify both parties while suppressing the acting user.
Events use deterministic `rental_request:{id}:...` keys, unique recipients, and
the shared Notification exact-once constraints.

Acceptance, pricing replacement, and availability mutations serialize through
the same equipment row lock. Acceptance revalidates active pricing, minimum
units, operator compatibility, availability blocks, and accepted/in-progress
overlaps before writing immutable commercial snapshots.

## Mobile discovery and detail (Phase 16.8)

The Mobile client consumes public categories, equipment list/detail, and active
pricing through typed models. Search plus category, province/city, and operator
mode filters map directly to Backend query parameters. Equipment detail renders
public media, lessor display name, delivery/deposit facts, and pricing rules.

Backend currently exposes no price-range filter, so the Mobile client does not
pretend to provide one. Availability date selection and request creation are
reserved for the next Mobile request-flow step.

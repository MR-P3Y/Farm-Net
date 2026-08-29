# Services API

The Services module implements the operational-services marketplace request
workflow. Phase 26 connects the final-price agreement to universal invoice
checkout, verified payment, ledger posting, the paid-before-start gate, full
refund policy, and requester-confirmed provider-balance release. Disputes,
chat, and real-gateway refund execution remain outside this contract.

## Request roles and privacy

All paths use the `/api/v1` prefix and the standard
`success/data/message/meta` response envelope.

## Endpoint inventory

| Scope | Method and path | Purpose |
|---|---|---|
| Public | `GET /services/categories` | Active category discovery |
| Public | `GET /services/offers` | Approved offer discovery and filters |
| Public | `GET /services/offers/{offer_id}` | Public offer detail |
| Provider owner | `GET/POST/PUT /services/me/provider-profile` | Read or save owned profile |
| Provider owner | `POST /services/me/provider-profile/submit` | Submit profile for moderation |
| Provider owner | `GET/POST /services/me/offers` | List or create owned offers |
| Provider owner | `PUT /services/me/offers/{offer_id}` | Update owned offer |
| Provider owner | `POST /services/me/offers/{offer_id}/submit` | Submit offer for moderation |
| Requester | `POST /services/requests` | Create request in `open` state |
| Requester | `GET /services/requests/me` | Paginated owned list |
| Requester | `GET /services/requests/{request_id}` | Owned operational detail |
| Requester | `PATCH /services/requests/{request_id}/cancel` | Cancel with `{reason}` |
| Provider | `GET /services/requests/assigned` | Paginated assigned list |
| Provider | `GET /services/requests/assigned/{request_id}` | Assigned operational detail |
| Provider | `PATCH /services/requests/{request_id}/status` | Controlled assigned transition |
| Provider | `POST/GET /services/requests/assigned/{request_id}/final-price` | Propose/read final price |
| Requester | `GET/PATCH /services/requests/{request_id}/final-price` | Read and accept/reject final price |
| Requester | `POST /services/requests/{request_id}/refund` | Request an idempotent full refund |
| Requester | `POST /services/requests/{request_id}/confirm-completion` | Confirm completed work and release provider balance |
| Invoice payer | `POST /finance/invoices/{invoice_id}/checkout` | Create/replay a payment attempt |
| Invoice payer | `POST /finance/payments/verify` | Verify payment and post the ledger movement |
| Gateway | `GET /finance/payments/callback/zarinpal` | Complete a Zarinpal payment callback |
| Admin | `GET/POST /admin/services/categories` | List or create categories |
| Admin | `PATCH /admin/services/categories/{category_id}` | Update category |
| Admin | `POST /admin/services/requests/{request_id}/confirm-completion` | Explicit completion/release override |
| Admin | `GET /admin/commission/policies` | List default domain commission policies |
| Admin | `GET/PATCH /admin/commission/policies/{source_type}/default` | Read/update domain commission |
| Admin | `GET /admin/finance/billing-refunds` | List service billing refunds |
| Admin | `PATCH /admin/finance/billing-refunds/{refund_id}/decision` | Approve/reject a reviewed refund |
| Admin | `POST /admin/finance/billing-refunds/{refund_id}/complete-mock` | Complete a Mock full refund |

## Final-price billing gate

`budget_amount` is never billable. Final price requires an accepted operational
request, an explicit provider proposal, and requester acceptance. Acceptance
fails closed without an active default `service_request` commission policy and
creates one exact-once universal Invoice. `in_progress` is blocked until that
Invoice is paid. An unpaid cancellation cancels its pending Invoice.

Checkout is owner-scoped and idempotent. Verification locks the attempt and
Invoice, marks the Invoice paid, and posts one balanced ledger transaction:
platform cash is debited while provider pending balance and platform revenue
are credited. The provider share is deliberately pending; it is not available
for settlement until the requester confirms a completed request or an Admin
uses the explicit override. There is no automatic timeout release.

## Commission, cancellation, refund, and release policy

- The seeded default commission for `service_request` is `10.00%`. Admin may
  change the active default for future invoices. Every accepted final price
  stores an immutable commission snapshot, so later edits never rewrite an
  existing Invoice.
- A paid request cancelled before work enters `in_progress` receives a full
  refund without review. The refund is created as `approved`, but money is not
  claimed returned until Provider processing succeeds.
- After work starts, a cancellation and full-refund request is created as
  `requested` and requires an explicit Admin approval or rejection.
- The current executable refund adapter is Mock-only and disabled in
  production. Real Zarinpal refund execution is not claimed by this contract.
- On successful refund, the original provider-pending and platform-commission
  postings are reversed exactly once. If the provider share was already
  released, its release is reversed first; processing fails closed when those
  funds have already been reserved or settled.
- Provider funds move from pending to available only after the request reaches
  `completed` and the requester confirms completion. Admin may override this
  confirmation explicitly; there is no automatic or time-based release.

Category management preserves Admin-owned seed rows, rejects direct and
indirect hierarchy cycles, and accepts `parent_id: null` to move a category to
the root. Admin responses expose direct-child, provider-link, offer, and request
usage counters. Deactivation remains the non-destructive lifecycle.
| Admin | `GET /admin/services/provider-profiles[/{profile_id}]` | List or inspect providers |
| Admin | `PATCH /admin/services/provider-profiles/{profile_id}/status` | Moderate provider |
| Admin | `GET /admin/services/offers[/{offer_id}]` | List or inspect offers |
| Admin | `PATCH /admin/services/offers/{offer_id}/status` | Moderate offer |
| Admin | `GET /admin/services/requests[/{request_id}]` | List or inspect requests |
| Admin | `PATCH /admin/services/requests/{request_id}/status` | Controlled admin transition |

| Role | List | Detail and mutation | Ownership |
|---|---|---|---|
| Requester | `GET /services/requests/me` | `POST /services/requests`, `GET /services/requests/{id}`, `PATCH /services/requests/{id}/cancel` | Own requests only |
| Approved provider | `GET /services/requests/assigned` | `GET /services/requests/assigned/{id}`, `PATCH /services/requests/{id}/status` | Assigned provider profile only |
| Admin | `GET /admin/services/requests` | `GET /admin/services/requests/{id}`, `PATCH /admin/services/requests/{id}/status` | Permission-controlled platform scope |

Requester list items intentionally omit description, contact method, address,
coordinates, notes, cancel reason, and status logs. Provider list items add the
requester ID and coarse province/city names. Admin list items additionally
include contact method. Full operational fields are returned only by authorized
detail endpoints. `admin_note` is exclusive to the admin detail contract.

Status logs are ordered oldest-first and expose exactly:
`id`, `request_id`, `changed_by_user_id`, `old_status`, `new_status`, `note`,
and `created_at`.

## Workflow

- Initial status: `open`.
- Provider: `open -> accepted|rejected`, `accepted -> in_progress`,
  `in_progress -> completed`. Entering `in_progress` additionally requires a
  requester-accepted and paid final-price Invoice.
- Requester cancel: only from `open` or `accepted`.
- A paid accepted request uses the refund endpoint instead of the legacy
  cancellation endpoint; after `in_progress`, cancellation/refund needs Admin
  review.
- Provider completion does not release funds. Requester completion confirmation
  (or the explicit Admin override) performs one exact-once pending-to-available
  ledger movement.
- Admin: the explicit transition table enforced by the service layer.
- Same-status, invalid, and terminal transitions are rejected before a status
  log or notification is written.

## Notifications

In-app events are emitted atomically with request changes:

- `service_request.created`
- `service_request.accepted`
- `service_request.rejected`
- `service_request.in_progress`
- `service_request.completed`
- `service_request.cancelled`
- `service_request.final_price_proposed`
- `service_request.final_price_accepted`
- `service_request.final_price_rejected`
- `finance.invoice_paid`
- `finance.refund_requested`
- `finance.refund_approved`
- `finance.refund_rejected`
- `finance.refund_completed`
- `service_request.completion_confirmed`

Stable event keys make each request transition idempotent. A recipient receives
at most one in-app notification for an event, duplicate recipient IDs are
collapsed, and the actor is excluded. Payloads contain identifiers, titles, and
old/new status only; contact, address, coordinates, and notes are excluded.

## Mobile discovery

The Step 17.6 mobile feature consumes `GET /services/categories`,
`GET /services/offers`, and `GET /services/offers/{id}`. The list supports `q`,
`category_id`, `province_id`, `city_id`, `pricing_type`, `min_price`,
`max_price`, and allow-listed `sort` (`relevance`, `newest`, `price_asc`,
`price_desc`, `rating`, `distance`). Distance sorting requires a validated
`latitude`/`longitude` pair; optional `radius_km` is bounded to 500 km. Price
range is canonical `TOMAN`; negotiable offers
without a price are excluded by a price range and remain last in price sorting.
Category selection includes active descendants. Search uses the shared Persian
normalizer across offer, provider, category, service-area, and geo names.

## Mobile requester flow

Step 17.7 consumes `POST /services/requests`,
`GET /services/requests/me`, `GET /services/requests/{id}`, and
`PATCH /services/requests/{id}/cancel`. The mobile client sends `reason` for
cancellation, permits cancellation only from `open` or `accepted`, and parses
the hardened `old_status`/`new_status` status-log contract.

## Mobile provider management

Step 17.8 consumes the owner profile endpoints under
`/services/me/provider-profile` and owner offer endpoints under
`/services/me/offers`. It uses the exact `pending_review` status and backend
pricing modes (`fixed`, `hourly`, `daily`, `hectare`, `project`, `negotiable`).
The existing public media uploader supplies `avatar_media_file_id` and offer
`media_items[].media_file_id`; no parallel upload protocol was introduced.
Profiles also expose `accepting_requests`, `availability_status`
(`available|busy|unavailable`), and bounded `typical_response_minutes`.
Offer media may set `portfolio_stage` to `before` or `after` so public detail
can render real before/after portfolio labels.

The Mobile discovery UI provides list/map modes, shared street/satellite map
layers, location-permission-based nearest sorting, distance labels, price and
rating sorting, an active-request badge, provider trust/availability summary,
and a bottom primary request action consistent with consultation requests.

## Mobile provider workbench

Step 17.9 consumes `GET /services/requests/assigned`,
`GET /services/requests/assigned/{id}`, and
`PATCH /services/requests/{id}/status`. Provider actions strictly follow the
backend transition table; provider cancellation is not exposed.

## Admin panel

Step 17.10 exposes `/services` in the admin panel with typed category,
provider-profile, offer, request, and status-log models. The four tabs use only
the admin endpoints above, surface backend permission failures, paginate list
contracts, and limit request actions to the backend transition matrix. No raw
JSON is rendered and no separate Services contract is maintained in the UI.

## Postman and regression

The canonical collection is
`postman/collections/services.postman_collection.json`. Its tokens and record
IDs are environment variables and never contain secrets. Runtime verification
must include collection JSON parsing, OpenAPI path/schema checks, backend
Services tests, mobile/admin analysis and tests, web builds, and application,
database, and Redis health.

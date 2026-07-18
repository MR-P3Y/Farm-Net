# Farm-Net Project Progress

Last verified: 2026-07-17
Branch at verification: `develop`
Verified HEAD before Phase 9.2 commit: `f2b96be`

## Current Position

The Services foundation is released as `v0.17.0-services-foundation`. Phase 9
completion has resumed; Steps 9.1 through 9.4 are complete.

## Completed Foundations

| Area | Status | Reference |
|---|---|---|
| Product scope and governance | Done | `v0.1.0-foundation-docs` |
| Backend foundation | Done | `v0.2.0-backend-foundation` |
| Flutter foundation | Done | `v0.3.0-flutter-foundation` |
| Admin foundation | Done | `v0.4.0-admin-foundation` |
| Auth foundation | Done | `v0.5.0-auth-foundation` |
| Geo, profile, verification | Done at foundation level | `v0.6.0-geo-profile-verification-foundation` |
| Store foundation | Done | `v0.7.0-store-foundation` |
| Products foundation | Done | `v0.8.0-store-products-foundation` |
| Orders, mock payment, commission | Done at foundation level | `v0.9.0-orders-payments-commission-foundation` |
| Media foundation | Done | `v0.10.0-media-storage-foundation` |
| Notifications foundation | Done for in-app foundation | `v0.11.0-notifications-foundation` |
| Weather foundation | Done | `v0.12.0-weather-foundation` |
| Social/community foundation | Done | `v0.13.0-social-community-foundation` |
| Expert answers and consultants | Done at foundation level | `v0.14.0-expert-consultants-foundation` |
| Windows environment recovery | Done | Owner-confirmed 2026-07-15 |

## Services Execution Progress

| Step | Status | Evidence |
|---|---|---|
| 17.1 DB + Permission Foundation | Done | `3b8af10` |
| 17.2 Category + Provider Profile Foundation | Done | `0f3a07d` |
| 17.3 Service Offers Foundation | Done for backend | `c247d9d` |
| 17.4 Service Request Flow | Done | APIs, transitions, status logs, tests, runtime smoke |
| 17.5 Request Notifications + Contract Hardening | Done | Six events, exact-once guards, role contracts, tests and runtime checks |
| 17.6 Mobile Service Discovery + Detail | Done | List/detail UI, filters, gallery, navigation and model tests |
| 17.7 Mobile Service Request Flow | Done | Create/list/detail/cancel, timeline, routing and tests |
| 17.8 Provider Profile + Offer Management Mobile | Done | Profile/offers CRUD-submit, media, navigation and tests |
| 17.9 Provider Request Workbench | Done | Assigned list/detail, transitions, timeline and tests |
| 17.10 Admin Panel Services | Done | `bda9699` |
| 17.11 Docs/Postman + Runtime Regression | Done | `f2b96be` |
| Services mobile UI | Done at foundation level | Discovery, requester and provider workflows |
| Services admin UI | Done at foundation level | Four typed management tabs |
| Services API docs/Postman | Done | Complete Services docs and 30-request collection |
| Services automated tests | Done at focused level | 13 request workflow/contract tests |
| Services release/tag | Done | `v0.17.0-services-foundation` |

## Phase 9 Completion Progress

| Step | Status | Evidence |
|---|---|---|
| 9.1 Existing Orders/Payments Audit | Done | Read-only contract and gap audit |
| 9.2 Financial Contracts + DB Hardening | Done | Seven financial tables, explicit enums, idempotency/amount constraints and tests |
| 9.3 Atomic Checkout + Inventory Reservation | Done | Row locks, atomic stock decrement and reservation lifecycle |
| 9.4 Checkout Idempotency + Contract Hardening | Done | Persistent replay keys, role privacy contracts and reservation expiry |
| 9.5 Payment Orchestration + Idempotent Verify | Done | Mock provider initiation, exact-once verify and atomic financial state changes |
| 9.6 Refund Request + Idempotent Processing | Done | Full-refund policy, Mock completion and exact-once transaction |
| 9.7 Admin Finance Read Models + Audit | Done | Typed finance APIs, pagination, permissions and immutable admin audit trail |
| 9.8 Admin Finance UI | Done | Five typed finance tabs, pagination, guarded navigation and responsive states |
| 9.9 Mobile Payment UX + Contract Migration | Done | Buyer invoice contract, idempotent initiate/verify UX and privacy cleanup |
| 9.10 Docs/Postman + Release Regression | Done | 29 OpenAPI paths, 34 Postman requests and full three-surface regression |
| 9.11 Release Gate + Tag | Done | `v0.18.0-orders-finance-foundation` |

### Step 9.2 Completion Evidence

- Added invoice/item, commission snapshot, payment-attempt, transaction, refund,
  and inventory-reservation database contracts without changing current API,
  Mobile, Admin, or Mock payment behavior.
- Added explicit lifecycle enums and typed input/output contracts for future
  checkout, verify, transaction, and refund operations.
- Enforced positive amounts/quantities, one invoice and commission snapshot per
  order, one reservation per order item, and unique idempotency/provider keys.
- Added four focused contract tests; the full Backend suite has 17 passing tests.
- Alembic upgraded to `a7c9f2e14b30`; all seven new tables and critical unique
  constraints were verified in MySQL. Application, database, and Redis health
  remained `ok`.

### Step 9.3 Completion Evidence

- Checkout locks the active cart and products in stable ID order before
  revalidation, snapshot refresh, and stock decrement.
- Order, invoice/items, commission snapshot, Mock payment/attempt, inventory
  reservations, status history, and notifications commit in one transaction;
  any error explicitly rolls back.
- Successful Mock payment marks its attempt and invoice successful, records a
  financial transaction, and consumes reservations.
- Admin cancellation releases reserved or consumed inventory exactly once;
  paid cancellations move the invoice to `refund_pending` without claiming a
  completed financial refund.
- Added atomic checkout, rollback, consume, and cancellation-release tests. All
  21 Backend tests pass and runtime database/Redis health remains `ok`.

### Step 9.4 Completion Evidence

- Checkout now requires a client idempotency key and persists its user, cart,
  canonical request fingerprint, resulting order IDs, and completion time.
- An exact replay returns the original orders without a second stock decrement;
  reuse with a different payload is rejected with a stable conflict code.
- Expired `reserved` inventory is locked, restored, and marked `expired` exactly
  once before a new checkout proceeds.
- Buyer responses hide commission/seller/admin internals. Seller list responses
  hide buyer delivery/contact data, notes, payments, and history; seller details
  retain operational delivery data while hiding admin and commission internals.
- Mobile checkout generates and submits the new idempotency key.
- Migration head is `b84d1c7e29f0`; 22 focused Backend tests, Ruff, compileall,
  Mobile analyze, and runtime database/Redis health pass. Mobile has no test
  directory, so `flutter test --no-pub` remains unavailable for that exact reason.

### Step 9.5 Completion Evidence

- Added authenticated `POST /api/v1/payments/checkout` for buyer-owned invoices.
- Payment initiation replays an existing attempt for the same idempotency key
  and rejects cross-user, invoice, or provider conflicts.
- Added authenticated `POST /api/v1/payments/verify`; successful Mock verify
  updates the attempt, legacy payment, invoice, order, transaction, inventory
  reservation, history, and notifications in one unit of work.
- Repeated successful verify returns the existing attempt without creating a
  second transaction or consuming inventory again.
- Only the non-secret Mock provider is enabled. Real gateway credentials,
  callback handling, and external money movement remain explicitly deferred.
- 25 focused Backend tests, Ruff, compileall, OpenAPI route checks, and runtime
  application/database/Redis health pass.

### Step 9.6 Completion Evidence

- Added permission-protected Admin refund request and Mock completion APIs.
- Refund creation is idempotent, requires a paid/refund-pending invoice, and
  currently permits only a full refund to prevent ambiguous partial accounting.
- Completion locks the refund and updates refund, transaction, invoice, order,
  legacy payment, status history, and notification exactly once.
- Repeated completion returns the existing successful refund without a second
  financial transaction. Real provider money movement remains deferred.

### Step 9.7 Completion Evidence

- Added typed, paginated Admin APIs for invoices/detail, payment attempts,
  transactions, refunds, and finance audit logs.
- Added `admin_audit_logs` with actor, action, target, old/new values, IP,
  user-agent, trace ID, and timestamp; refund request/completion now write audit
  records in the same transaction as their financial change.
- Connected finance read/refund permissions to `finance_admin` and Admin roles;
  auth seed remains idempotent at 12 roles and 215 permissions.
- Alembic head is `c91e4a8d52b7`; all six routes are registered and runtime
  application/database/Redis health remains `ok`.

### Step 9.8 Completion Evidence

- Added the guarded `/finance` Admin route and connected the existing Finance
  sidebar entry.
- Added typed tabs for invoices, payment attempts, transactions, refunds, and
  audit logs with pagination plus loading, empty, error, and retry states.
- No raw JSON is rendered; finance and audit model parsing has focused tests.
- Admin analyze, tests, and Web build pass.

### Step 9.9 Completion Evidence

- Buyer order responses now include the non-secret `invoice_id` required by the
  payment initiation contract.
- Mobile payment uses idempotent `payments/checkout` followed by exact-once
  `payments/verify`; the legacy Mock Pay endpoint is no longer called by UI.
- Retry uses a stable per-invoice key, loading/error states remain controlled,
  and internal commission/seller amounts are no longer rendered for buyers.
- Typed Payment Attempt and Checkout replay-key model tests were added.

### Step 9.10 Completion Evidence

- Completed Phase 9 API documentation and expanded the Postman collection to
  34 valid requests with payment/refund/finance variables and replay keys.
- OpenAPI exposes 29 Phase 9 paths; collection JSON parsing succeeds.
- Backend Ruff/compileall and 28 focused regressions pass; Alembic remains at
  `c91e4a8d52b7`, auth seed is idempotent, and DB/Redis health is `ok`.
- Mobile analyze, 26 tests, and Web build pass.
- Admin analyze, 5 tests, and Web build pass.

### Step 9.11 Release Gate

- Final Backend, Mobile, Admin, OpenAPI, Postman, migration, seed, and health
  checks passed on clean, pushed `develop`.
- Release tag: `v0.18.0-orders-finance-foundation`.

## Step 17.4 Completion Evidence

- Used exact model fields: `provider_profile_id`, initial status `open`, and
  `changed_by/from_status/to_status/note` status logs.
- Added requester create/list/detail/cancel operations.
- Added approved-provider assigned list/detail and controlled transitions.
- Added admin list/detail and controlled status management.
- Enforced permission, ownership, provider approval, and terminal-state rules.
- Allowed requester cancellation only from `open` and `accepted`.
- Registered 10 OpenAPI request paths.
- Local compile and Ruff passed; 4 focused pytest tests passed.
- Alembic upgraded through `d62e2f6b7c11`; auth seed completed.
- Health returned application, database, and Redis as `ok`.
- Runtime smoke covered authentication, offer validation, ownership, provider
  approval, transitions, ordered logs, cancellation, and admin access.

Request notifications were intentionally deferred to Step 17.5.

## Step 17.5 Completion Evidence

- Added created, accepted, rejected, in-progress, completed, and cancelled
  in-app event contracts with stable event keys.
- Prevented duplicate recipient notifications and actor self-notifications.
- Kept notification writes and status logs in the request transaction.
- Added requester, assigned-provider, and admin list/detail response models and
  registered them explicitly in OpenAPI.
- Hardened list privacy, ownership boundaries, admin-only notes, safe event
  payloads, and exact public status-log field names.
- Added Services API documentation and a parse-validated Postman collection.
- Ruff, compileall, and all 13 backend tests passed.
- Runtime OpenAPI exposed all 10 request paths with named response schemas.
- Runtime health returned application, database, and Redis as `ok`.

## Step 17.6 Completion Evidence

- Added a Services mobile feature using the real public contracts:
  `/services/categories`, `/services/offers`, and `/services/offers/{id}`.
- Added service search and category, province, city, and pricing-mode filters.
  Price-range filtering remains deferred because the backend does not expose
  minimum/maximum price parameters.
- Added list cards, loading/error/empty states, detail view, provider public
  summary, media gallery, responsive layout, routing, and Home navigation.
- Added safe parsing tests for public offers, nested category/provider/media,
  decimal price strings, optional fields, and fallbacks.
- Flutter analyze completed with no issues and all 14 mobile tests passed.

## Step 17.7 Completion Evidence

- Added authenticated request creation from service detail with title,
  description, contact method, optional budget, schedule, province/city, and
  address fields matching the backend create contract.
- Added requester-owned list and detail screens, refresh/loading/error/empty
  states, status labels, operational detail, and exact status-log timeline.
- Added cancellation only for `open` and `accepted` requests and sends the
  backend `reason` contract.
- Added Home and service-detail navigation for request creation and requester
  request management.
- Added model/input tests for decimal parsing, hardened status-log field names,
  cancellation rules, and omission of unpopulated optional fields.
- Flutter analyze completed with no issues and all 17 mobile tests passed.

## Step 17.8 Completion Evidence

- Added provider owner-profile GET/create/update/submit integration, nullable
  no-profile state, status helpers, category selection, admin-note rendering,
  duplicate-submit protection, and Persian management UI.
- Added approved-provider offer list/create/update/submit integration with real
  backend status and pricing enums, moderation notes, and eligibility helpers.
- Reused the existing authenticated media uploader. Public uploads map to
  `avatar_media_file_id` and `media_items[].media_file_id`; existing offer
  media retain their underlying media-file IDs during editing.
- Added Home entries and non-conflicting provider profile/offer routes.
- Backend envelope errors, including 401, 403, and validation messages, flow
  through the existing `ApiError` mapping into retryable UI states.
- Flutter analyze passed with no issues, all 21 tests passed, and Flutter Web
  build completed successfully.
- OpenAPI exposed all eight owner profile/offer methods; runtime database and
  Redis health returned `ok`.

## Step 17.9 Completion Evidence

- Added assigned-request API integration, supported filters, assigned detail,
  and the exact `{status, note}` update payload.
- Added the provider workbench list/detail, pull-to-refresh, operational fields,
  safe requester ID, status timeline, confirmation dialogs, and Home routing.
- Exposed only `open -> accepted|rejected`, `accepted -> in_progress`, and
  `in_progress -> completed`; provider cancellation is not allowed by backend.
- Added explicit Persian handling for unapproved-provider 403 responses,
  duplicate-tap prevention, and list/detail refresh after updates.
- Flutter analyze passed with no issues, all 24 tests passed, and Flutter Web
  build completed successfully.
- OpenAPI exposed all three assigned operations; database and Redis were `ok`.

## Step 17.10 Completion Evidence

- Added the admin Services route and sidebar entry with four management tabs:
  categories, provider profiles, offers, and service requests.
- Added typed Dart models and API integration for category create/edit,
  provider and offer moderation, paginated request lists, request detail,
  exact status logs, and admin request status updates.
- Limited request actions to the backend transition matrix and used the real
  provider and offer status values; moderation notes are sent with status
  updates and backend permission errors are shown to the operator.
- Added loading, empty, error, refresh, and pagination states without rendering
  raw JSON in the interface.
- Flutter analyze passed with no issues, all admin tests passed, and Flutter Web
  build completed successfully.
- Runtime OpenAPI exposed all four admin Services resource groups; application,
  database, and Redis health returned `ok`.
- Step 17.11 (Docs/Postman and runtime regression) is the next planned step.

## Step 17.11 Completion Evidence

- Expanded the canonical Services Postman collection from request-only coverage
  to 30 requests spanning public discovery, provider profile/offer ownership,
  category/provider/offer moderation, and requester/provider/admin workflows.
- Added the complete 25-path Services endpoint inventory, admin-panel contract,
  privacy/workflow guidance, and regression procedure to the API documentation.
- Postman JSON parsed successfully and every required Services resource path was
  present in the runtime OpenAPI document.
- Backend Ruff and compileall passed; all 13 focused and full-suite backend tests
  passed. Four existing `datetime.utcnow()` deprecation warnings remain noted.
- Mobile analyze passed, all 24 tests passed, and the Web build succeeded.
- Admin analyze passed, all 3 tests passed, and the Web build succeeded.
- Runtime health returned application, database, and Redis as `ok`; all three
  Docker services were running.
- Services Steps 17.1 through 17.11 are complete. The next roadmap step requires
  explicit selection rather than being inferred from this sequence.

## Important Existing Gaps

The following are not considered complete merely because related permissions or
model fields exist:

- production payment gateway and verification;
- SMS, email, and push delivery providers;
- general contracts/versioned agreements;
- subscriptions and Pro plans;
- promotions/ladder;
- equipment rental;
- search/discovery across the platform;
- reviews and ratings workflows;
- wallet, settlement, refund, and accounting;
- AI/RAG assistant;
- BI, reports, analytics, and controlled data access;
- production Nginx/SSL, CI/CD, monitoring, backup automation, and deployment
  hardening;
- broad backend, Flutter, and integration test coverage.

## Phase 11 - Notifications

### Step 11.1 Real-State Audit

- Audited the three notification tables, service/repository behavior, user and
  Admin APIs, producer integrations, Mobile/Admin clients, and provider config.
- Confirmed the in-app inbox foundation is implemented and ownership protected.
- Confirmed external channels have no dispatcher/provider/retry implementation.
- Identified missing DB exact-once enforcement, inconsistent deterministic
  event keys, producer-specific self-notification behavior, and the absence of
  preferences, device tokens, and a focused notification test suite.
- Defined Step 11.2 as provider-neutral DB/delivery contract hardening; real
  channel adapters remain later steps.
- Evidence: `docs/notifications/phase-11-real-state-audit.md`.

### Step 11.2 Delivery Contracts + DB Hardening

- Added database exact-once constraints for event/recipient/channel and one
  durable delivery state per notification/channel, with legacy deduplication.
- Added savepoint-based race handling, deterministic source event keys, and an
  explicit suppress-by-default self-notification policy with confirmation-flow
  opt-ins.
- Added provider-neutral processing/retry counters, scheduling timestamps, and
  worker lease state without connecting an external provider.
- Alembic upgraded MySQL to `e72b9f4c31a6`; runtime inspection confirmed the
  constraints and columns, and database/Redis health returned `ok`.
- Backend application/migration Ruff and compileall passed; all 33 Backend tests
  passed with 16 existing UTC deprecation warnings. Eight unrelated seed-script
  E402 findings remain outside this step.
- Evidence: `docs/notifications/phase-11-delivery-contracts.md`.

### Step 11.3 User Preferences + Channel Routing

- Added owner-scoped global and event-specific preferences with deterministic
  precedence and an idempotent GET/PUT API.
- Preserved in-app as the default; Email/SMS are opt-in and require verified
  AuthUser destinations. Push/Telegram remain unroutable until destination
  registries exist, and system messages remain mandatory in-app.
- Alembic upgraded MySQL to `f84c2a1d9037`; health remained `ok` and OpenAPI
  exposes 9 notification paths including both preference methods.
- Backend Ruff passed and all 36 tests passed with 16 existing UTC warnings.
- Evidence: `docs/notifications/phase-11-preferences-routing.md`.

### Step 11.4 Retry Queue + Failure/Delivery Logs

- Added durable monotonic attempt history and atomic external-channel claims
  using row locks, skip-locked concurrency, and worker leases.
- Added expired-lease recovery, capped exponential backoff, terminal failure,
  provider-neutral success/failure recording, and controlled Admin requeue.
- Added permission-protected Admin delivery list/detail/history/retry APIs.
- Alembic upgraded MySQL to `a16d7c4e52b9`; health remained `ok` and all three
  Admin delivery paths are present in runtime OpenAPI.
- Backend Ruff/compileall passed and all 40 tests passed with 16 existing UTC
  warnings. No provider network call is implemented in this step.
- Evidence: `docs/notifications/phase-11-retry-queue.md`.

### Step 11.5 Email Provider Foundation

- Added escaped text/HTML Email envelopes, SMTP STARTTLS/SSL transport, and an
  Email-only dispatcher integrated with claim, attempt, success, and failure.
- Added dispatch-time verified-recipient checks, terminal recipient rejection,
  provider message IDs, and a one-batch CLI worker.
- Activation is fail-closed: incomplete/disabled configuration claims no work.
- Backend Ruff/compileall passed and all 43 tests passed with 16 existing UTC
  warnings. Docker runtime confirmed disabled configuration claimed/sent zero;
  application/database/Redis health remained `ok`.
- No live credential was used and no real Email was sent.
- Evidence: `docs/notifications/phase-11-email-provider.md`.

### Step 11.6 SMS Provider Foundation

- Added provider-neutral SMS contracts and a fail-closed HTTPS JSON adapter
  with Bearer authentication, verified-phone checks, safe URL filtering, and
  bounded message length.
- Integrated SMS claim/success/failure with retry history and added a one-batch
  CLI worker; retryable network/timeout/429 and terminal 4xx are distinguished.
- Backend Ruff/compileall passed and all 46 tests passed with 16 existing UTC
  warnings. Docker disabled runtime claimed/sent zero; no real SMS was sent.
- Evidence: `docs/notifications/phase-11-sms-provider.md`.

### Step 11.7 Push Notification Foundation

- Added owner-scoped Android/iOS/Web device registration and deactivation;
  tokens are unique and never exposed by output contracts.
- Enabled Push routing only for active devices and added a fail-closed HTTPS
  JSON batch dispatcher integrated with queue results and a one-batch CLI.
- Alembic upgraded MySQL to `b27e8d5f64c1`; OpenAPI exposes both device paths,
  health is `ok`, and all 49 Backend tests passed with 16 existing warnings.
- Docker disabled runtime claimed/sent zero; no real Push was sent.
- Evidence: `docs/notifications/phase-11-push-provider.md`.

### Step 11.8 Mobile Notification Center Hardening

- Added typed preferences/device contracts and a global channel settings screen
  with optimistic update rollback and backend error handling.
- Expanded action routing for Social, Services, and Consultants while preserving
  the existing inbox/loading/empty/error/filter/read/delete/badge behavior.
- Flutter analyze passed, all 28 tests passed, and Web build/Wasm dry run passed.
- Exact gap: no vendor Push SDK/credential exists, so real token acquisition and
  refresh are not wired; no fake device token is registered.
- Evidence: `docs/notifications/phase-11-mobile-hardening.md`.

### Step 11.9 Admin Notification Operations

- Added typed paginated delivery log and attempt models plus list/detail/retry
  repository contracts; no raw JSON reaches the UI.
- Added a permission-protected operations page with status/channel filters,
  pagination, delivery failure details, attempt timeline, and controlled retry.
- Retry visibility matches Backend rules, while Backend permissions and
  validation remain authoritative.
- Admin analyze passed, all 7 tests passed, and Web build/Wasm dry run passed.
- No Backend API behavior, Mobile behavior, schema, or provider was changed.
- Evidence: `docs/notifications/phase-11-admin-operations.md`.

### Step 11.10 Docs/Postman + Runtime Regression

- Reconciled API/event/foundation documentation with the implemented Email,
  SMS, Push, device, queue, retry, and Admin operations contracts.
- Validated the canonical collection: 20 requests cover all 14 runtime
  Notifications paths, including preferences, devices, and delivery operations.
- Backend focused lint/compile and 21 notification tests passed; the full suite
  passed 49 tests with 16 existing UTC deprecation warnings.
- Alembic, permission seed, disabled-mode workers, OpenAPI, and app/database/
  Redis health passed without using any live provider credential.
- Mobile passed analyze, 28 tests, Web build, and Wasm dry run; Admin passed
  analyze, 7 tests, Web build, and Wasm dry run.
- Evidence: `docs/notifications/phase-11-runtime-regression.md`.

### Step 11.11 Notifications Release Gate + Tag

- Reverified the complete Phase 11 commit chain on clean, pushed `develop`.
- Backend Ruff/compileall passed; all 49 tests passed with 16 existing UTC
  deprecation warnings. Alembic remained at `b27e8d5f64c1` and seed passed.
- Email, SMS, and Push disabled-mode workers safely claimed/sent zero messages;
  application, database, and Redis health remained `ok`.
- Runtime OpenAPI exposes 14 Notifications paths and the valid Postman
  collection contains 20 requests.
- Mobile passed analyze, 28 tests, and Web/Wasm build checks; Admin passed
  analyze, 7 tests, and Web/Wasm build checks.
- Release tag: `v0.19.0-notifications-delivery-foundation`.

## Phase 12 — Category Management

### Step 12.1 Product Category Management

- Preserved the existing product category tree and added safe manual management.
- Added public discovery plus permission-protected Admin list/create/update APIs.
- Added hierarchy cycle prevention, stable slug validation, usage counters,
  search, ordering, and non-destructive activation controls.
- Added typed Admin UI and complete four-request Postman coverage.
- Backend Ruff/compileall passed and all 51 tests passed; Admin analyze, all 8
  tests, and Web/Wasm build passed.
- Evidence: `docs/products/phase-12-product-category-management.md`.

### Step 12.2 Category Governance Alignment Audit

- Verified Product, Services, Consultant, and Social taxonomy models, relations,
  permissions, APIs, Admin clients, seeds, OpenAPI, and runtime reference data.
- Kept domain tables independent and defined a shared governance/UX contract.
- Identified Services cycle/parent-clear/seed/count gaps, Social's missing Admin
  management, and Consultant usage-count/Admin-search gaps.
- Confirmed runtime has no active Services, Consultant, or Social reference rows;
  future hardening must include explicit idempotent seed readiness.
- Defined Steps 12.3 through 12.8 without changing runtime behavior.
- Evidence: `docs/categories/phase-12-category-governance-audit.md`.

## Progress Update Rule

After every completed step:

1. update this document with the commit and verification evidence;
2. update relevant API, notification, and database docs;
3. add or update the Postman collection;
4. report tracked and untracked Git status separately;
5. do not mark a step done until its required tests and smoke checks pass.

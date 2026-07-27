# Farm-Net Project Progress

Last verified: 2026-07-25
Branch at verification: `develop`
Verified HEAD before Phase 9.2 commit: `f2b96be`

## Current Position

The latest completed development foundation is
`v0.25.0-reviews-foundation`. Phase 22 Step 22.10 remains blocked on external
provider credentials. By owner decision, Phase 24 Farm Management / Digital
Farm Profiles is the active product track and prerequisite for farmer-focused
Phase 21 AI/RAG.

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

### Step 12.3 Services Category Contract Hardening

- Added full hierarchy cycle prevention and explicit parent clearing.
- Made default seeding non-destructive and added a repeatable Services seed CLI.
- Added typed child/provider/offer/request usage counters to Admin contracts/UI.
- Backend Ruff/compileall and 55 tests passed; Admin analyze, 9 tests, and
  Web/Wasm build passed. Runtime seed produced 8 active categories twice and
  app/database/Redis health remained `ok`.
- Evidence: `docs/categories/phase-12-services-category-hardening.md`.

### Step 12.4 Social Category Management

- Added category-specific permissions and public/Admin typed category contracts.
- Added search, create/update, activation/order controls, and post usage counts.
- Added a typed Admin management page and non-destructive six-category seed CLI.
- Backend Ruff/compileall and 58 tests passed; Admin analyze, 10 tests, and
  Web/Wasm build passed. Runtime OpenAPI, Postman, seed, and health passed.
- Evidence: `docs/categories/phase-12-social-category-management.md`.

### Step 12.5 Consultant Specialty Usage + Admin Search Hardening

- Added profile/request usage counts to Backend and typed Admin contracts.
- Connected the existing Backend code/title/description search to Admin UI.
- Backend Ruff/compileall and 59 tests passed; Admin analyze, 11 tests, and
  Web/Wasm build passed. OpenAPI, Postman, and runtime health passed.
- Runtime remains at zero specialties because no authoritative default taxonomy
  has been approved; no synthetic business data was introduced.
- Evidence: `docs/categories/phase-12-consultant-specialty-hardening.md`.

### Step 12.6 Unified Admin Taxonomy Navigation + UX Consistency

- Added a central, permission-aware taxonomy hub and Admin sidebar entry.
- Linked Product, Services, Consultant, and Social management without merging
  their independent models or lifecycle rules.
- Added a direct Consultant specialties route that opens the correct Admin tab.
- Admin analyze, all 12 tests, and Web/Wasm build passed.
- Evidence: `docs/categories/phase-12-admin-taxonomy-navigation.md`.

### Step 12.7 Docs/Postman + Runtime Regression

- Reconciled Product, Services, Social, and Consultant taxonomy documentation
  while preserving their independent domain models and lifecycle rules.
- Validated the four canonical Postman collections: Products 23 requests,
  Services 30, Social + Expert 22, and Consultants 31.
- Backend Ruff/compileall passed and all 59 tests passed with 16 existing UTC
  deprecation warnings. Alembic remained at `b27e8d5f64c1` and auth seed
  confirmed 12 roles and 221 permissions.
- Product, Services, and Social seeds passed twice without duplication; runtime
  public counts are 24, 8, and 6 respectively.
- Consultant specialties remain at zero because no authoritative default
  taxonomy is approved; no synthetic reference data was introduced.
- Runtime OpenAPI exposed all 12 taxonomy paths and application/database/Redis
  health returned `ok`.
- Mobile passed analyze, 28 tests, and Web/Wasm build checks; Admin passed
  analyze, 12 tests, and Web/Wasm build checks.
- Evidence: `docs/categories/phase-12-runtime-regression.md`.

### Step 12.8 Category Management Release Gate + Tag

- Reverified the complete Phase 12 commit chain on clean, pushed `develop`.
- Backend Ruff/compileall passed; all 59 tests passed with 16 existing UTC
  deprecation warnings. Alembic remained at `b27e8d5f64c1` and auth seed
  confirmed 12 roles and 221 permissions.
- Product, Services, and Social seeds remained idempotent at 24, 8, and 6 rows;
  Consultant specialties intentionally remained empty pending approved data.
- Runtime OpenAPI exposed all 12 taxonomy paths and application/database/Redis
  health returned `ok`.
- All four Postman collections parsed with 23 Product, 30 Services, 22 Social +
  Expert, and 31 Consultant requests.
- Mobile passed analyze, 28 tests, and Web/Wasm build checks; Admin passed
  analyze, 12 tests, and Web/Wasm build checks.
- Release tag: `v0.20.0-category-management-foundation`.

## Phase 16 — Equipment Rental

### Step 16.1 Real-State Audit + Contract Boundary

- Confirmed that Rental has no module, tables, migrations, APIs, Mobile/Admin
  feature, tests, documentation, or Postman collection yet.
- Identified only the existing `lessor` role, four moderation permission
  placeholders, equipment classifications, and ownership verification type.
- Separated rentable equipment from Product sale inventory and Services work.
- Defined lessor/listing moderation, availability/pricing, date-bound booking,
  overlap protection, role privacy, status-log, and notification boundaries.
- Kept order-only invoices/payments outside the foundation until explicit
  Rental finance contracts are implemented; no payment behavior is overstated.
- Defined Steps 16.2 through 16.12 and the final release gate.
- Evidence: `docs/rentals/phase-16-real-state-audit.md`.

### Step 16.2 Rental DB + Permission Foundation

- Added eight independent Rental tables for categories, lessors, equipment,
  media, pricing, availability, requests, and exact-once status logs.
- Added date-range, positive amount/unit, stable identity, commercial snapshot,
  ownership, and overlap-query database contracts.
- Expanded Rental authorization to 24 requester/lessor/Admin permissions and
  assigned default roles through the idempotent Auth seed.
- Alembic upgraded MySQL to `104ae669cc1a`; all eight tables were inspected and
  application/database/Redis health returned `ok`.
- Backend Ruff/compileall passed, 3 focused tests passed, and the full suite
  passed 62 tests with 16 existing UTC deprecation warnings.
- Preserved four unrelated legacy Consultant/Services indexes detected by
  `alembic check`; cleanup remains an explicit pre-release compatibility task.
- Evidence: `docs/rentals/phase-16-db-permission-foundation.md`.

### Step 16.3 Categories + Lessor Profile APIs

- Added public/Admin category governance, hierarchy safety, usage counts, and
  a non-destructive eight-category seed.
- Added owner lessor profile get/save/submit plus Admin filter, pagination, and
  controlled moderation contracts.
- Required approved lessor verification before profile approval and Admin notes
  for rejection/suspension.
- Backend Ruff/compileall passed, 5 focused and all 64 Backend tests passed;
  runtime seed, 7 OpenAPI paths, 401 ownership guard, and health passed.
- Added API documentation and a valid nine-request Rental Postman collection.
- Evidence: `docs/rentals/phase-16-categories-lessor-profiles.md`.

### Step 16.4 Equipment Listing + Media APIs

- Added public approved discovery/detail and owner create/update/list/submit.
- Added equipment identity, operator, delivery, deposit, geo, and lifecycle
  contracts independent from Product and Services.
- Reused real public owner Media with active/ownership checks and deterministic
  primary-image behavior; public responses hide exact address/Admin data.
- Added typed Admin listing and status-specific moderation permissions.
- Backend Ruff/compileall passed, 8 focused and all 67 tests passed; runtime
  exposed 14 Rental paths and health/401/public-list smoke passed.
- Rental Postman coverage expanded to 17 valid requests.
- Evidence: `docs/rentals/phase-16-equipment-media-apis.md`.

### Step 16.5 Availability + Pricing Rules

- Added atomic multi-unit pricing with positive/unique/operator-compatible
  contracts and public active pricing output.
- Added owner availability CRUD and public range checks with UTC normalization,
  block/booking overlap prevention, and private-note protection.
- Hardened Admin approval to require equipment media and active pricing.
- Backend Ruff/compileall passed, 12 focused and all 71 tests passed; Runtime
  exposed 19 Rental paths, remained at Alembic head, and health/401 passed.
- Rental Postman coverage expanded to 25 valid requests.
- Evidence: `docs/rentals/phase-16-pricing-availability.md`.

### Step 16.6 Rental Request/Booking Workflow

- Added requester, assigned-lessor, and Admin request list/detail/workflow APIs.
- Added self-rental, pricing/operator/minimum, availability, ownership, and
  transition validation plus requester cancellation boundaries.
- Acceptance uses equipment row locks, overlap revalidation, and immutable
  unit/rental/deposit/total/currency snapshots without claiming payment.
- Added deterministic exact-once status-log keys and Admin-note privacy.
- Backend Ruff/compileall passed, 16 focused and all 75 tests passed; Runtime
  exposed 29 Rental paths, remained at Alembic head, and health/401 passed.
- Rental Postman coverage expanded to 35 valid requests.
- Evidence: `docs/rentals/phase-16-request-booking-workflow.md`.

### Step 16.7 Notifications + Privacy/Concurrency Hardening

- Added Rental notification events for request creation, acceptance, rejection,
  start, completion, and cancellation through the Phase 11 delivery foundation.
- Added deterministic event keys, recipient deduplication, self-notification
  prevention, role-correct action URLs, and atomic notification creation with
  the booking transaction.
- Serialized pricing and availability writes against booking acceptance through
  the equipment row lock; acceptance revalidates minimum units and operator mode.
- Preserved requester/lessor/Admin ownership and Admin-note privacy contracts;
  no public API or schema migration was added.
- Backend Ruff/compileall passed, focused Rental + Notification tests passed 41,
  and all 79 Backend tests passed with 16 existing UTC warnings. Runtime stayed
  at 29 Rental paths and Alembic head; app/database/Redis health returned `ok`.
- Rental Postman remained 35 valid requests because no route was added.
- Evidence: `docs/rentals/phase-16-notifications-hardening.md`.

### Step 16.8 Mobile Equipment Discovery + Detail

- Added typed Rental category, equipment, media, and pricing models plus
  API/Repository/Riverpod discovery state.
- Added public equipment search and backend-supported category, province/city,
  and operator-mode filters with clear/refresh behavior.
- Added equipment detail with media gallery, lessor identity, commercial and
  delivery facts, deposit, and active pricing rules.
- Added loading, empty, error/retry states, typed model tests, GoRouter paths,
  and a Home entry for equipment rental.
- Did not claim price-range filtering because Backend has no such filter. Rental
  request creation remains Step 16.9 and is clearly identified in the detail UI.
- Mobile analyze passed, all 30 tests passed, and Web/Wasm build checks passed.
- Evidence: `docs/rentals/phase-16-mobile-discovery-detail.md`.

### Step 16.9 Mobile Rental Request Flow

- Added typed availability, request input/detail, snapshot, and status-log
  models plus requester API/Repository/Riverpod operations.
- Added pricing rule, requested-unit, start/end, delivery address, and requester
  note input with operator mode derived from the selected Backend pricing rule.
- Required a successful public availability preflight before submission while
  preserving Backend acceptance-time overlap revalidation as authoritative.
- Added requester list/detail, pull-to-refresh, role-safe timeline, commercial
  snapshots, status labels, and cancellation only for pending/accepted requests
  with a required reason.
- Added request routes and Home navigation. Mobile analyze passed, all 32 tests
  passed, and Web/Wasm build checks passed.
- Evidence: `docs/rentals/phase-16-mobile-request-flow.md`.

### Step 16.10 Mobile Lessor Management + Request Workbench

- Added lessor profile create/edit/submit rendering with moderation status and
  Admin-note handling plus public Media avatar integration.
- Added owner equipment list, typed create/edit/submit, category/operator/geo,
  delivery/deposit, and public owner Media integration.
- Added atomic pricing rule management and availability block create/edit/delete
  against the existing Backend ownership, overlap, and lifecycle contracts.
- Added assigned request list/filter/detail, status timeline, refresh, and only
  the Backend-authorized accept/reject/start/complete actions.
- Added role navigation from Home and GoRouter coverage. Mobile analyze passed,
  all 34 tests passed, and Web/Wasm build checks passed.
- Evidence: `docs/rentals/phase-16-mobile-lessor-workbench.md`.

### Step 16.11 Admin Panel Equipment Rental

- Added a typed four-tab Rental Admin surface for categories, lessor profiles,
  equipment listings, and rental requests.
- Added category create/edit, parent hierarchy, activation, ordering, usage
  counters, and validation-aligned fields.
- Added paginated lessor/equipment moderation with status-specific Admin notes
  and Backend permission enforcement.
- Added paginated request list, typed Admin-only detail, commercial snapshot,
  cancel/Admin notes, exact status timeline, and controlled Admin transitions.
- Added Permission Guard, sidebar/router navigation, loading/empty/error states,
  pagination, and model tests without raw JSON rendering.
- Admin analyze passed, all 14 tests passed, and Web/Wasm build checks passed.
- Evidence: `docs/rentals/phase-16-admin-panel.md`.

### Step 16.12 Docs/Postman + Runtime Regression

- Consolidated Backend, notification, Mobile requester/lessor, Admin, privacy,
  concurrency, financial boundary, and operational verification documentation.
- Validated 35 Postman requests, every raw JSON body, and exact coverage of all
  29 unique Runtime Rental OpenAPI paths with no missing or extra path.
- Backend Ruff/compileall passed and all 79 tests passed with 16 existing
  `datetime.utcnow` warnings outside Rental. Three seed launchers received only
  explicit E402 annotations for their intentional path bootstrap.
- Alembic remained `104ae669cc1a (head)`; Auth seed ran twice identically with
  12 roles and 241 permissions. Runtime confirmed 8 Rental tables, 24 Rental
  permissions, and app/database/Redis health `ok`.
- Mobile analyze/build passed with all 34 tests; Admin analyze/build passed with
  all 14 tests. Both Web builds completed and Wasm dry runs passed.
- Evidence: `docs/rentals/phase-16-docs-runtime-regression.md`.

### Step 16.13 Equipment Rental Release Gate + Tag

- Re-ran the complete release gate without adding features or changing Backend,
  Mobile, or Admin behavior.
- Backend Ruff and compileall passed; all 79 tests passed with 16 existing
  non-Rental `datetime.utcnow` warnings. Alembic remained at
  `104ae669cc1a (head)` and the idempotent Auth seed remained at 12 roles and
  241 permissions.
- Runtime confirmed app/database/Redis health `ok`, 8 Rental tables, 24 Rental
  permissions, and 29 Rental OpenAPI paths.
- Mobile analyze passed, all 34 tests passed, and Web/Wasm build checks passed.
- Admin analyze passed, all 14 tests passed, Web build passed, and Flutter's
  integrated Wasm compatibility dry run passed. The installed Flutter version
  does not accept a separate `flutter build web --wasm --dry-run` option.
- The valid 35-request Postman collection covers all 29 Runtime Rental paths
  exactly, with no missing or extra path.
- Git was clean, `develop` matched `origin/develop`, and the annotated release
  tag is `v0.21.0-equipment-rental-foundation`.
- Financial operations remain outside this foundation: payment, invoice,
  commission, settlement, refund, deposit capture/release, damage, and penalty.
- Evidence: `docs/rentals/phase-16-release-gate.md`.

## Phase 20 — Wallet, Settlement, and Accounting

### Step 20.1 Real-State Audit + Contract Boundary

- Audited the real order finance models, migrations, services, routes,
  permissions, tests, and documentation without changing runtime behavior.
- Confirmed Phase 9 already has order-specific invoices, commission snapshots,
  idempotent Mock payment/verify, transactions, full Mock refunds, inventory
  reservations, Admin audit, and typed Admin reads.
- Confirmed there is no wallet, double-entry ledger, balance buckets,
  settlement/payout implementation, real gateway, or finance integration for
  Services, Rental, and Consultation.
- Identified the blocking `TOMAN` versus Consultation `IRR` inconsistency and
  distinguished service/consultation budgets from final payable prices.
- Defined an incremental 20.2–20.15 delivery plan that preserves Phase 9 API
  compatibility and treats the ledger—not a mutable balance—as accounting truth.
- Evidence: `docs/finance/phase-20-real-state-audit.md`.

### Step 20.2 Canonical Money + Billable Source Contracts

- Standardized every new commercial input on Iranian toman: API/database code
  `TOMAN`, Persian UI label `تومان`, and legacy ratio `10 IRR = 1 TOMAN`.
- Added typed billable-source and financial-event contracts for product orders,
  service requests, rental requests, and consultation requests without posting
  money or changing existing Phase 9 endpoints.
- Added a migration that converts legacy consultation `IRR` budgets and codes
  atomically; the Runtime consultation table was empty at migration time.
- Rejected non-`TOMAN` product, service, rental, and consultation commercial
  inputs and changed Mobile/Admin consultation fallbacks to `TOMAN`.
- Defined that service/consultation budgets are not billable final prices and
  rental deposit principal is not provider revenue.
- Ruff/compileall passed; 53 focused and all 84 Backend tests passed. Alembic is
  `4c9a2f20b102 (head)` and app/database/Redis health is `ok`.
- Mobile analyze and all 34 tests passed; Admin analyze and all 14 tests passed.
- Evidence: `docs/finance/phase-20-money-billable-contracts.md`.

### Step 20.3 Wallet Accounts + Double-Entry Ledger DB/Permissions

- Added Wallet Account, immutable Ledger Transaction, and ordered Ledger Entry
  models plus migration `c7e8a1f20303`.
- Enforced `TOMAN`, positive amounts, equal journal debit/credit totals, unique
  idempotency/journal/reversal references, protected foreign keys, and ORM
  update/delete guards for posted accounting records.
- Added explicit provider pending/available/reserved, customer funds, platform,
  deposit liability, refund clearing, and payout clearing account purposes.
- Added five Wallet/Ledger permissions and explicit own-wallet access for user,
  seller, service provider, lessor, and consultant roles. Internal posting is
  not granted to ordinary or Finance Admin roles.
- Ruff/compileall and 24 focused tests passed; all 88 Backend tests passed with
  16 existing UTC warnings. Alembic reached `c7e8a1f20303 (head)`.
- Auth seed ran twice identically with 12 roles and 246 permissions. Runtime
  confirmed all three tables, all five permissions, and app/database/Redis
  health `ok`.
- Alembic metadata check found no Finance drift; it still reports four existing
  Consultant/Services unique-index naming differences outside this step.
- Evidence: `docs/finance/phase-20-wallet-ledger-foundation.md`.

### Step 20.4 Order Finance Ledger Bridge + Reconciliation

- Bridged successful Phase 9 payment Verify, legacy Mock Pay, and Mock Refund
  completion into balanced ledger journals inside their existing DB commit.
- Posted platform cash against provider pending payable and platform revenue;
  Refund journals exactly reverse the payment economics. Zero-value lines are
  omitted while all stored entries remain positive.
- Added a unique direct link from each journal to its legacy
  `finance_transactions` row for exact-once posting and reconciliation.
- Added a typed, read-only Admin reconciliation endpoint protected by
  `finance.ledger.reconcile`; it reports missing bridges and header/entry
  imbalances but never repairs data.
- Ruff/compileall, 21 focused, and all 90 Backend tests passed. Alembic reached
  `d9a4b2f20404 (head)`; OpenAPI/401 and app/database/Redis health passed.
- Added and JSON-validated the Admin Ledger Reconciliation Postman request.
- Runtime reconciliation was clean with zero existing successful financial
  transactions; therefore no existing real-row posting smoke was available.
- Evidence: `docs/finance/phase-20-order-ledger-bridge.md`.

### Step 20.5 Universal Invoice + Commission Foundation

- Added domain-neutral Invoice, Invoice Item, Commission Policy, and Commission
  Snapshot tables while preserving every Phase 9 public order/payment API.
- Enforced `TOMAN`, positive/nonnegative amount rules, exact provider/platform
  split, unique source/legacy links, immutable item/snapshot records, and one
  database-enforced default Commission Policy per domain source.
- Atomically mirrors new product-order Checkout invoices/items/commission into
  universal billing and synchronizes paid, refund-pending, refunded, and unpaid
  cancellation states. Historical Phase 9 invoices bridge lazily on transition.
- Explicitly blocked Service/Consultation budgets from invoicing and deferred
  Rental until revenue and deposit principal are separated in Step 20.7.
- Ruff/compileall and focused tests passed; all 92 Backend tests passed with 16
  existing UTC warnings. Alembic reached `f7a6d4b20606 (head)` and all four
  Runtime tables plus app/database/Redis health were verified.
- Alembic metadata check found no Finance drift and reported only the four
  pre-existing Consultant/Services unique-index naming differences.
- Runtime contained zero legacy invoices, so no existing-row billing smoke was
  available. No API path was added and Postman remained unchanged.
- Evidence: `docs/finance/phase-20-universal-billing-foundation.md`.

### Step 20.6 Services/Consultation Final-Price Contracts

- Added versioned final-price proposals with database-enforced single active
  and accepted contracts, positive `TOMAN`, retained history, and immutable
  accepted agreements.
- Kept `budget_amount` non-billable. Providers/consultants propose only after
  operational acceptance; only the owning requester accepts or rejects.
- Requester acceptance creates an exact-once universal Invoice/item/commission
  snapshot and fails closed unless the exact domain has an active default
  Commission Policy. No rate was guessed or inherited across domains.
- Blocked `in_progress` until price acceptance. Unpaid cancellation cancels the
  pending Invoice; paid contracts require a future financial refund flow.
- Added eight ownership-protected OpenAPI operations and matching Services/
  Consultants Postman requests. Both collections parse successfully.
- Ruff/compileall, 26 focused, and all 98 Backend tests passed with 16 existing
  UTC warnings. Alembic reached `b9c8d6e40808 (head)`; app/database/Redis health
  and Runtime constraints passed.
- Alembic metadata check found no Step 20.6 drift and still reports only four
  pre-existing Consultant/Services unique-index naming differences.
- Runtime had zero proposals/domain invoices and no configured Service or
  Consultation policy, so a real-row acceptance smoke was not possible.
- Evidence: `docs/finance/phase-20-service-consultation-final-price.md`.

### Step 20.7 Rental Revenue + Deposit Accounting Boundaries

- Added exact-once immutable `finance_rental_terms` from authoritative accepted
  request snapshots: unit price/units, rental revenue, refundable deposit
  principal, funding total, payer/provider, currency, and acceptance time.
- Enforced `TOMAN`, positive revenue, nonnegative deposit, and exact
  `funding total = rental revenue + deposit principal` at database level.
- Rental acceptance creates terms atomically; `in_progress` requires them;
  cancellation and operational completion retain truthful `unfunded` status.
- Deposit principal is never provider revenue or Commission base. No Invoice,
  ledger posting, capture, custody/release, damage, penalty, refund, or
  settlement is claimed.
- Migration safely backfills valid accepted/in-progress/completed requests.
  Runtime contained zero eligible rows and therefore produced zero terms.
- Focused tests passed; final full regression is recorded in the evidence doc.
  All 105 Backend tests passed with 16 existing UTC warnings. Alembic reached
  `ecba19a70b11 (head)`, Runtime constraints and app/database/
  Redis health passed, and no new metadata drift remains.
- Rental Postman JSON remains at 29 paths/35 requests and parses successfully;
  its description now records the Phase 20.7 boundary.
- Evidence: `docs/finance/phase-20-rental-revenue-deposit-boundary.md`.

### Step 20.8 Balance Release + Settlement/Payout Workflow

- Paid Product Orders now release provider share exactly once on `delivered`,
  moving liability from pending to available through a balanced Ledger Journal.
- Added Ledger-derived own Wallet balances for pending/available/reserved; no
  mutable balance cache or cross-domain unfunded revenue is represented.
- Added idempotent own Settlement requests that atomically reserve available
  balance, plus Admin approve/reject and explicitly simulated payout clearing.
- Rejection returns reserved to available. Simulated completion moves reserved
  to payout clearing and never claims an external bank transfer.
- Added immutable Settlement request history, positive `TOMAN` and status DB
  constraints, six ownership/permission-protected APIs, two provider
  permissions, and six Postman requests.
- Ruff/compileall, 26 focused, and all 110 Backend tests passed with 16 existing
  UTC warnings. Alembic reached `fdcb2ab80c12 (head)`; Auth seed twice produced
  12 roles/248 permissions; Runtime health and OpenAPI passed.
- Runtime had zero settlements/release journals, so no real-row movement smoke
  was possible. Step 20.9 owns refund/reversal/adjustment concurrency after
  release or reservation.
- Evidence: `docs/finance/phase-20-balance-release-settlement.md`.

### Step 20.9 Refund, Reversal, Adjustment + Concurrency Hardening

- Product Order Refund now detects a prior Release and posts an immutable,
  exact-once linked Reversal from provider available back to pending before the
  existing Refund Journal reverses Payment economics.
- Release Journal and provider available account row locks serialize Refund
  against Settlement reservation. Refund fails closed when released funds are
  reserved or in simulated payout clearing; negative wallet balances are not
  allowed.
- Added controlled Admin provider-wallet credit/debit Adjustments with a
  dedicated permission, `TOMAN` validation, mandatory reason, idempotency
  conflict detection, balanced adjustment clearing, debit no-overdraft, and
  exact-once Admin Audit logging.
- Added OpenAPI and Postman coverage plus focused contracts for reversal sides,
  blocked reserved funds, adjustment accounting, permissions, and routing.
- Ruff and compileall passed; 25 focused and all 113 Backend tests passed with
  16 existing UTC warnings. Alembic remains at `fdcb2ab80c12 (head)` because
  this step needs no schema change. Auth seed passed twice idempotently with 12
  roles/249 permissions. Runtime app/database/Redis health passed; OpenAPI has
  248 paths including Adjustment. Postman JSON parses with 42 requests.
- Evidence: `docs/finance/phase-20-refund-reversal-adjustment.md`.

### Step 20.10 Real Payment Gateway Adapter + Callback Verification

- Added a Zarinpal v4 Request/Verify adapter with fixed HTTPS provider hosts,
  explicit sandbox selection, timeouts, structured provider failures, and
  configuration validation. It is disabled by default.
- Canonical project `TOMAN` amounts are sent as Zarinpal `IRT`; fractional or
  non-positive amounts fail closed. Merchant ID remains environment-only.
- Product Order Checkout now supports `provider=zarinpal`, persists Authority
  and redirect URL, and retains the existing idempotency contract.
- Added public `GET /api/v1/payments/callback/zarinpal`. Callback `Status=OK`
  never marks an order paid by itself: Authority must match a locked attempt and
  server-to-server Verify must return code 100 or exact-once code 101.
- `NOK` records cancellation. Successful Verify uses the existing atomic
  Payment/Order/Invoice, inventory, Ledger, history, and notification flow.
- No Merchant ID is available in the repository or Runtime. Therefore the
  credentialed Sandbox request/redirect/callback smoke is explicitly pending
  and no external payment is claimed.
- Ruff and compileall passed; all 119 Backend tests passed with 17 existing UTC
  warnings. Alembic remains `fdcb2ab80c12 (head)` because no schema change was
  needed. Runtime app/database/Redis health passed and confirmed Gateway
  disabled, Merchant absent, Sandbox selected. OpenAPI has 249 paths with the
  public Callback; Postman JSON parses with 44 requests.
- Evidence: `docs/finance/phase-20-zarinpal-gateway-callback.md`.

### Step 20.11 Financial Notifications + Privacy/Audit Hardening

- Added explicit Refund requested/completed, Settlement requested/approved/
  rejected/simulated, and Wallet adjusted event types.
- Notifications target only the affected buyer/provider and use the existing
  preference, delivery-log, retry and duplicate-prevention contracts.
- A recursive privacy guard rejects gateway/card secrets, Authority,
  idempotency keys, provider references, raw Callback/Verify payloads, reasons,
  and Admin notes from Payment/Finance event payloads.
- Settlement decisions and simulated clearing now create exact-once Admin Audit
  records. Refund completion Audit no longer copies provider reference.
- Added focused privacy/ownership tests and a Postman preference example.
- Ruff and compileall passed; 45 focused and all 128 Backend tests passed with
  17 existing UTC warnings. Alembic remains `fdcb2ab80c12 (head)` because no
  schema change was required. Runtime app/database/Redis health passed;
  OpenAPI remains 249 paths. Notification Postman JSON parses with 21 requests.
- Evidence: `docs/finance/phase-20-financial-notifications-privacy-audit.md`.

### Step 20.12 Mobile Wallet, Invoices, and Provider Settlements

- Added typed Mobile Finance models/API/Repository/Riverpod state for Wallet,
  payer invoices, Settlement history, and idempotent Settlement creation.
- Added a responsive «مرکز مالی من» screen with canonical Iranian toman
  formatting, pending/available/reserved cards, invoice and Settlement empty/
  loading/error states, pull-to-refresh, validation, and Home navigation.
- Buyer-only roles can still view invoices when provider Wallet/Settlement
  permissions are absent. Provider actions remain permission-controlled.
- Added `GET /api/v1/finance/invoices/me` and detail, scoped strictly to the
  authenticated payer. Their typed contract excludes platform/provider shares.
- Mobile analyze passed; all 38 Flutter tests and Web build passed. Backend
  Ruff/compileall passed; all 129 tests passed with 17 existing UTC warnings.
  Runtime app/database/Redis health passed; OpenAPI has 251 paths.
- Evidence: `docs/finance/phase-20-mobile-finance-center.md`.

### Step 20.13 Admin Accounting, Settlement, and Reconciliation

- Extended the typed Admin Finance model/API/Repository and tabbed UI with
  Ledger Journals, Wallet Accounts, Settlement workflow, and Reconciliation.
- Finance Admin can approve/reject requested Settlements and move approved rows
  to explicitly simulated clearing. UI never labels simulation as bank payout.
- Added a refreshable Reconciliation health card with typed counts for missing
  Payment/Refund bridges and unbalanced journals.
- Added paginated `GET /api/v1/admin/finance/ledger` and `/wallets`, protected by
  dedicated Ledger/Wallet read permissions. Existing loading/empty/error and
  pagination behavior covers the new resources.
- Admin analyze passed, all 16 Admin tests and Web build passed. Backend Ruff/
  compileall and all 129 tests passed with 17 existing UTC warnings. Runtime
  app/database/Redis health passed; OpenAPI has 253 paths.
- Evidence: `docs/finance/phase-20-admin-accounting.md`.

### Step 20.14 Docs/Postman + Runtime Financial Regression

- Consolidated the Phase 20 financial release evidence and corrected the
  Orders/Payments/Finance Postman inventory to its actual 48 requests.
- Backend Ruff and compileall passed; all 129 Backend tests passed with 17
  existing UTC deprecation warnings. Alembic upgraded/current is
  `fdcb2ab80c12 (head)` and Auth seed passed twice idempotently with 12 roles
  and 249 permissions.
- Runtime app/database/Redis health passed. Finance reconciliation was clean:
  all mismatch arrays were empty, with zero successful Payment/Refund rows and
  zero corresponding posted journals in this environment.
- OpenAPI exposes 253 total paths and 27 Finance/Payment/Admin-refund paths.
  The 48-request Postman collection and all 18 variable-bearing raw JSON body
  templates parse successfully after normal Postman variable resolution.
- Mobile analyze passed, all 38 tests passed, and Web build passed. Admin
  analyze passed, all 17 tests passed, and Web build passed; Wasm dry-runs also
  succeeded for both applications.
- Credentialed Zarinpal sandbox smoke was skipped because no Merchant ID/public
  HTTPS callback is configured. Real bank payout remains outside the current
  simulated-clearing contract. No real-row money movement is claimed.
- Evidence: `docs/finance/phase-20-runtime-regression.md`.

### Step 20.15 Wallet/Settlement/Accounting Release Gate + Tag

- Independent gate passed on clean `develop` synchronized with
  `origin/develop`.
- Backend Ruff/compileall passed and all 129 tests passed with 17 existing UTC
  deprecation warnings. Alembic is `fdcb2ab80c12 (head)`; Auth seed remained
  idempotent at 12 roles and 249 permissions.
- Runtime app/database/Redis health passed after restarting the stale Backend
  process so it loaded the release candidate. OpenAPI then exposed the expected
  253 total and 27 financial paths.
- Reconciliation mismatch arrays were empty. Runtime remains a zero-successful-
  transaction environment, so no real money movement is claimed.
- Mobile analyze, 38 tests, Web build and Wasm dry-run passed. Admin analyze,
  17 tests, Web build and Wasm dry-run passed.
- Postman passed with 48 requests and 18 variable-resolved raw JSON templates.
- Release tag: `v0.22.0-wallet-settlement-accounting-foundation`.
- Credentialed Zarinpal and real bank payout remain explicit operational/future
  gaps; payout clearing in this foundation is simulated.
- Evidence: `docs/finance/phase-20-release-gate.md`.

## Phase 18 — Search, Filters, and Discovery

### Step 18.1 Real-State Audit + Contract Boundary

- Audited public Backend and Mobile discovery for Products, Services, Rentals,
  Consultants, and Social without changing runtime behavior.
- Confirmed all five domains already support independent substring search and
  pagination; filter depth and Mobile exposure differ by domain.
- Confirmed there is no unified search module/endpoint, common sort contract,
  relevance score, Persian text normalization, suggestion/history contract, or
  cross-domain Mobile discovery hub.
- Identified exact gaps: no public price range filters, category matching is
  exact-ID rather than descendant-aware, Rental list cannot filter by requested
  availability window, and several Backend filters are not exposed in Mobile.
- Confirmed current `%query%` matching has no full-text/search-engine index and
  fixed domain ordering is used instead of query relevance.
- Defined Steps 18.2–18.12 with MySQL-first, privacy-preserving contracts; an
  external search engine is not introduced without measured need.
- Evidence: `docs/search/phase-18-real-state-audit.md`.

### Step 18.2 Shared Search Contracts + Persian Query Normalization

- Added one central `UnifiedSearchEngine` that orchestrates registered typed
  domain providers and returns grouped cross-domain results in requested order.
- Added the shared provider protocol and strict typed contracts for query,
  selected result types, pagination, sorting, geo/category/price filters,
  grouped results, public navigation routes, rating, and relevance score.
- Added deterministic normalization for Arabic/Persian Yeh and Kaf variants,
  Heh variants, diacritics, tatweel, joiners, whitespace, case, and Persian/
  Arabic digits.
- Shared price filters and result money pairs are canonical `TOMAN`; invalid
  ranges, duplicate result types, unknown fields, unsafe external routes, and
  incomplete price/currency pairs fail closed.
- No migration, permission, public endpoint, Postman request, or existing
  domain behavior changed. Domain providers will connect incrementally.
- Ruff/compileall, all 11 shared-search tests, and all 140 Backend tests passed
  with 17 existing UTC deprecation warnings.
- Evidence: `docs/search/phase-18-shared-contracts.md`.

### Step 18.3 Product + Store Discovery Hardening

- Added Product and Store providers for the central `UnifiedSearchEngine` with
  typed public result routes, geo/money fields, and deterministic relevance.
- Public Product and Store queries now use the same SQL-side Persian/Arabic
  normalization contract as the shared query normalizer.
- Product discovery adds `TOMAN` min/max price, allow-listed relevance/newest/
  price sorting, Store-name matching, and active descendant category scope.
- Store discovery adds allow-listed relevance/newest sorting. Existing approved/
  published/active/non-deleted privacy boundaries and historical default sort
  remain unchanged.
- Mobile Product API/Repository now carry the new typed filter parameters for
  later unified Discovery UI integration; no client-side fake filtering exists.
- Product and Store Postman examples use normalized-query/relevance contracts;
  API documentation records filters and compatibility behavior.
- Ruff/compileall and all 145 Backend tests passed with 17 existing UTC
  deprecation warnings. Mobile analyze and all 38 tests passed.
- Runtime Product and Store normalized-query smoke returned HTTP 200; runtime
  contained no matching public rows. No migration or seed change was required.
- Evidence: `docs/search/phase-18-product-store-discovery.md`.

### Step 18.4 Services Discovery Hardening

- Added the Service Offer provider for the central engine with typed Service
  result routes, provider rating, geo, optional `TOMAN` price, and relevance.
- Public search now uses shared Persian/Arabic normalization across Offer,
  Provider, Category, service-area, and geo fields.
- Added active descendant category scope, `TOMAN` min/max price, and allow-listed
  relevance/newest/price/rating sorts. Null negotiable prices remain last for
  price sorting and are excluded when a price range is selected.
- Preserved approved/active/non-deleted Offer and approved/non-deleted Provider
  boundaries, response shape, pagination, and historical default sort.
- Mobile Service API/Repository carries the new price/sort parameters for the
  later unified Discovery UI. Docs and Postman were updated.
- Ruff/compileall and all 149 Backend tests passed with 17 existing UTC
  deprecation warnings. Mobile analyze and all 38 tests passed.
- Runtime normalized-query/price/rating smoke returned HTTP 200 with a valid
  empty page; app/database/Redis health and 253-path OpenAPI passed.
- Evidence: `docs/search/phase-18-services-discovery.md`.

### Step 18.5 Equipment Rental Discovery Hardening

- Added the Rental Equipment provider for the central `UnifiedSearchEngine`
  with typed routes, geo, minimum active `TOMAN` price, and relevance.
- Applied shared Persian/Arabic normalization to equipment, lessor, category,
  manufacturer, model, slug, and description fields.
- Added active descendant-category scope, price range, and allow-listed
  relevance/newest/price sorting while preserving historical default ordering.
- Added availability-window filtering using the real overlap rules: explicit
  availability blocks and accepted/in-progress requests exclude equipment.
- Mobile Rental API/Repository now carries price, availability, and sort
  parameters without simulating discovery client-side; docs/Postman were updated.
- Ruff/compileall and all 153 Backend tests passed with 17 existing UTC
  deprecation warnings. Mobile analyze, all 38 tests, and Web/Wasm build passed.
- Runtime health reported app/database/Redis `ok`; the hardened public query
  returned HTTP 200. Rebuilt Backend OpenAPI remains 253 paths and exposes all
  new Rental discovery parameters.
- The 35-request Rental Postman collection parses successfully.
- Evidence: `docs/search/phase-18-rental-discovery.md`.

### Step 18.6 Consultant Discovery Hardening

- Added the Consultant provider for the central `UnifiedSearchEngine` with a
  typed public route, geo, rating, specialty summary, and relevance.
- Applied shared Persian/Arabic normalization to display name, title, bio,
  province/city names, and active specialty code/title/description.
- Added allow-listed `relevance`, `newest`, and `rating` sorting while retaining
  the historical featured/rating/review/newest default ordering.
- Preserved approved/non-deleted visibility and the public privacy contract;
  phone, email, admin notes, and moderation fields never enter search results.
- Mobile Consultant API/Repository now carries geo and sort parameters without
  client-side simulation; docs and Postman were updated.
- Ruff/compileall and all 155 Backend tests passed with 17 existing UTC
  deprecation warnings. Mobile analyze, all 38 tests, and Web/Wasm build passed.
- Rebuilt Runtime normalized-query/geo/rating smoke returned HTTP 200; health
  reported app/database/Redis `ok`, OpenAPI remained 253 paths with all seven
  Consultant list parameters, and the 35-request Postman collection parsed.
- Evidence: `docs/search/phase-18-consultant-discovery.md`.

### Step 18.7 Social Discovery Hardening

- Added the Social Post provider for the central `UnifiedSearchEngine` with a
  typed Mobile detail route, geo context, body summary, and relevance.
- Applied shared Persian/Arabic normalization to title, body, geo names, and
  category code/title/description.
- Added category, post-type, province/city filters and allow-listed `relevance`
  and `newest` sorting while preserving the historical newest default.
- Enforced published, public, non-deleted visibility; members-only, draft,
  hidden, rejected, and deleted posts cannot enter public discovery.
- Mobile Social API/Repository now carries geo and sort parameters without
  client-side simulation; docs and Postman were updated.
- Ruff/compileall and all 158 Backend tests passed with 17 existing UTC
  deprecation warnings. Mobile analyze, all 38 tests, and Web/Wasm build passed.
- Rebuilt Runtime normalized-query/type/geo/relevance smoke returned HTTP 200;
  health reported app/database/Redis `ok`, OpenAPI remained 253 paths with all
  eight Social list parameters, and the 22-request Postman collection parsed.
- Evidence: `docs/search/phase-18-social-discovery.md`.

### Step 18.8 Unified Cross-Domain Search API + Ranking Boundary

- Added public read-only `POST /api/v1/search` backed by the single central
  `UnifiedSearchEngine` and all six registered domain providers.
- Added one strict body contract for normalized query, ordered unique result
  types, domain/geo/price/availability filters, safe sort, and pagination.
- Returns groups in requested order with independent pagination and a summed
  total; unlike domain relevance scores are intentionally not globally merged.
- Preserved every provider's visibility/privacy rules and internal Mobile route
  contract. No search history, analytics, migration, seed, or permission added.
- Added focused API/OpenAPI/provider-registration tests, API documentation, and
  a three-request Unified Search Postman collection.
- Ruff/compileall and all 161 Backend tests passed with 18 warnings (17 existing
  UTC deprecations plus one TestClient dependency deprecation).
- Rebuilt Runtime six-domain normalized search returned HTTP 200 with all six
  groups in requested order; health reported app/database/Redis `ok`, OpenAPI
  increased from 253 to 254 paths, and the Search Postman collection parsed.
- Evidence: `docs/search/phase-18-unified-search-api.md`.

### Step 18.9 Mobile Unified Discovery Hub

- Added a typed Mobile Search model/API/Repository/Controller stack consuming
  only `POST /search`; no parallel client-side multi-domain querying exists.
- Added `/search` with one input, six selectable result-type chips, all shared
  safe sort choices, grouped totals/cards, `TOMAN` price and rating rendering.
- Cards use only validated Backend internal routes to open Product, Store,
  Service, Rental, Consultant, and Social detail screens.
- Added initial guidance, loading progress, no-results, API/network error, and
  retry states plus a prominent Home navigation entry.
- Added model tests for grouped response, decimal strings, optional fields, and
  safe fallbacks. Mobile analyze passed with no issues, all 40 tests passed, and
  Web/Wasm build completed successfully.
- Evidence: `docs/search/phase-18-mobile-unified-discovery.md`.

### Step 18.10 Performance, Privacy, and Abuse Hardening

- Added a maximum 120-item grouped response budget while retaining per-domain
  pagination up to 50 when fewer result types are selected.
- Added a Search-specific default 30 requests/60 seconds/client limiter inside
  the existing global limiter, with deterministic 429 and `Retry-After`.
- Bounded in-memory limiter client keys to 10,000 and changed proxy handling so
  `X-Forwarded-For` is trusted only from explicitly allow-listed immediate IPs.
- Added `Cache-Control: no-store` and `X-Robots-Tag: noindex, nofollow`; no query
  history, analytics, personalization, migration, or query-content logging added.
- Documented the multi-instance distributed-limiter boundary and scan-based text
  matching. Existing public/status/geo/price indexes remain; no unmeasured
  FULLTEXT index or external engine was introduced against sparse Runtime data.
- Ruff/compileall and all 164 Backend tests passed with 18 known warnings.
- Rebuilt Runtime health reported app/database/Redis `ok`; requests 1–30 returned
  200, request 31 returned 429 with `Retry-After: 60`, allowed responses carried
  both privacy headers, and OpenAPI remained 254 paths.
- Evidence: `docs/search/phase-18-performance-privacy-abuse.md`.

### Step 18.11 Docs/Postman + Runtime Search Regression

- Consolidated the Unified Search API, ranking, privacy, rate-limit, response
  budget, deployment boundary, Mobile Hub, and reusable regression instructions.
- Expanded Search Postman from 3 to 12 requests: all six domains, individual
  domains, geo/TOMAN price, Rental availability, Persian normalization, privacy
  headers, duplicate types, non-TOMAN, response budget, and interval rejection.
- Added read-only `backend/scripts/search_runtime_regression.py`; it verifies
  health, 254-path OpenAPI, seven positive searches, four negative contracts,
  group ordering/totals, safe internal routes, private-key exclusion, `TOMAN`,
  and no-store/noindex headers.
- Ruff/compileall and all 164 Backend tests passed with 18 known warnings.
  Mobile analyze/all 40 tests/Web-Wasm build passed. Admin analyze/all 17
  tests/Web-Wasm build passed despite no Admin Search behavior change.
- Alembic upgraded/current at `fdcb2ab80c12 (head)`. Auth seed ran twice with
  stable 12 roles / 249 permissions. Health app/database/Redis is `ok`.
- All 13 project Postman collections parsed: 284 total requests; all 12 Search
  raw bodies parsed as JSON.
- Runtime all-domain and each per-domain total were zero. This proves real SQL,
  response shape, privacy, and empty state but not populated real-row navigation;
  typed provider/model tests cover populated contracts.
- Evidence: `docs/search/phase-18-docs-postman-runtime-regression.md`.

### Step 18.12 Search/Filters/Discovery Release Gate + Tag

- Independently reran Backend Ruff/compileall and all 164 tests; all passed
  with the same 18 known deprecation warnings.
- Reran Mobile analyze, all 40 tests, and Web/Wasm build; all passed.
- Reran Admin analyze, all 17 tests, and Web/Wasm build; all passed.
- Verified Docker Backend/MySQL/Redis are running, Alembic is current at
  `fdcb2ab80c12 (head)`, and two Auth seed runs remain stable at 12 roles and
  249 permissions.
- Runtime Search passed seven positive and four negative contracts across all
  six providers with 254 OpenAPI paths and healthy application/database/Redis.
- All 13 current Postman collections and 313 requests parse; the 12 Search
  requests and all raw Search JSON bodies are valid.
- Phase 18 passed its release gate and is released as
  `v0.23.0-search-discovery-foundation`.
- Evidence: `docs/search/phase-18-release-gate.md`.

## Phase 23 — Role-Based My Activity Center

### Step 23.1 Real-State Audit + Contract Boundary

- Confirmed Mobile already has common Buyer/Requester, Finance, Verification,
  Notification, Shop, Service Provider, Lessor, and Consultant destinations,
  but Home exposes them as one flat non-role-aware list.
- Confirmed `AuthUser.roles` and `AuthUser.permissions` are the authoritative
  typed inputs for a multi-role activity catalog; Backend permission checks
  remain the final authorization boundary.
- Found one functional Mobile gap: Backend Seller Order list/detail/status APIs
  exist, but Mobile has no Seller Order workbench.
- Defined a Mobile-first, no-new-aggregate-API delivery sequence through Step
  23.11, including common activity, four business-role sections, seller order
  completion, verification/setup guidance, navigation hardening, regression,
  and release gate.
- Evidence: `docs/activity-center/phase-23-real-state-audit.md`.

### Step 23.2 Typed Role/Permission Activity Catalog

- Added a pure typed Mobile catalog that derives ordered personal, Shop,
  Service Provider, Lessor, and Consultant sections from authoritative
  `AuthUser.roles` and `AuthUser.permissions`.
- Kept setup permissions distinct from approved-role workbench permissions and
  retained permission checks on every action inside a role section.
- Added four focused tests for common permission filtering, setup state, Shop
  action filtering, and deterministic multi-role composition.
- Reserved the permission-protected Seller Orders destination for Step 23.4;
  no current UI consumes it before its real Mobile route/workbench exists.
- Mobile analyze passed and all 44 tests passed. No Backend/Admin/API behavior
  changed.
- Evidence: `docs/activity-center/phase-23-typed-activity-catalog.md`.

### Step 23.3 Activity Center Shell + Common Personal Activity

- Added the responsive authenticated `/activity` Mobile screen and a primary
  Home entry for `مرکز فعالیت‌های من`.
- Rendered the common personal catalog section for Profile, Verification,
  Notifications, Finance, Buyer Orders, and own Service/Rental/Consultation
  requests, with each optional destination permission-driven.
- Added explicit loading and unauthenticated deep-link states and retained the
  real Auth Gate as the login destination.
- Deliberately kept role sections hidden until their Steps 23.4–23.7 integrations
  are complete, and retained legacy Home shortcuts until Step 23.9.
- Mobile analyze passed, all 44 tests passed, and Web/Wasm build passed.
- Evidence: `docs/activity-center/phase-23-activity-shell-personal.md`.

### Step 23.4 Shop Owner Center + Seller Order Workbench

- Connected the permission-backed Shop Owner section to own Store, Products,
  and the newly completed Seller Order Mobile flow.
- Added typed Seller list/detail/status API and repository operations, paginated
  state, status filtering, refresh, empty/error/denied handling, delivery/item/
  timeline detail, optional Seller note, and list refresh after update.
- Exposed only the Backend transition matrix `paid -> confirmed -> processing
  -> shipped -> delivered`; invalid, backward, cancellation, and refund actions
  remain hidden.
- Preserved list/detail privacy and rendered order total/Seller share only in
  canonical `TOMAN`; commission and Admin note are not rendered.
- Mobile analyze passed, all 46 tests passed, and Web/Wasm build passed. Backend
  all 164 tests, Runtime app/database/Redis health, 254-path OpenAPI, and all
  three Seller Order contracts passed.
- Runtime had no authenticated Shop Owner order fixture, so no real status
  mutation is claimed.
- Evidence: `docs/activity-center/phase-23-shop-owner-seller-orders.md`.

### Step 23.5 Service Provider Activity Integration

- Generalized the Activity Center business-section renderer and connected the
  existing Provider Profile, Offers, and assigned-request Workbench flows.
- Preserved setup-vs-approved behavior: base profile management shows only the
  setup destination, while Offers and assigned work require their exact real
  permissions; role name alone never grants an action.
- Added focused approved-provider catalog coverage. Mobile analyze passed, all
  47 tests passed, and Web/Wasm build passed.
- Runtime application/database/Redis health is `ok`; 254-path OpenAPI contains
  all eight required provider profile/offer/assigned-request contracts.
- No Services API or workflow behavior changed and no counters/status were
  fabricated in the Activity Center.
- Evidence: `docs/activity-center/phase-23-service-provider-integration.md`.

### Step 23.6 Lessor Activity Integration

- Connected the permission-backed Lessor section through the shared Activity
  Center renderer to existing Profile, Equipment/commercial management, and
  assigned Rental Request Workbench flows.
- Preserved exact access boundaries for profile management, equipment create/
  update, and assigned-request management; absent Lessor access creates no
  misleading empty section.
- Added focused approved-Lessor catalog coverage. Mobile analyze passed, all 48
  tests passed, and Web/Wasm build passed.
- Runtime application/database/Redis health is `ok`; 254-path OpenAPI passed
  method checks for ten key Lessor Profile, Equipment, Pricing, Availability,
  and assigned-request contracts.
- No Rental API, workflow, availability, pricing, or financial behavior changed.
- Evidence: `docs/activity-center/phase-23-lessor-integration.md`.

### Step 23.7 Consultant Activity Integration

- Connected the permission-backed Consultant section through the shared
  Activity Center renderer to existing Profile/specialty/moderation and assigned
  Consultation Request Workbench flows.
- Kept requester Consultation activity in the common personal section and
  retained exact setup-vs-approved and permission boundaries.
- Added focused approved-Consultant catalog coverage. Mobile analyze passed,
  all 49 tests passed, and Web/Wasm build passed.
- Runtime application/database/Redis health is `ok`; 254-path OpenAPI passed
  exact method checks for five key Consultant Profile and assigned-request
  contracts.
- No Consultation API, workflow, final-price, or financial behavior changed.
- Evidence: `docs/activity-center/phase-23-consultant-integration.md`.

### Step 23.8 Role Setup/Verification + Multi-Role Hardening

- Added a typed four-role journey showing authoritative active roles and real
  setup destinations for Shop Owner, Service Provider, Lessor, and Consultant.
- Added direct Verification history access and authenticated identity refresh
  so newly approved roles/permissions appear without logout/login.
- Hardened multi-role behavior with deterministic ordering, duplicate-safe role
  membership, no role switching, and a business-only active-role count that
  excludes Admin/support/data roles.
- Confirmed Backend approval assigns the exact Verification target role and
  Mobile safely routes both legacy and canonical Verification notification URLs.
- Mobile analyze passed, all 50 tests passed, and Web/Wasm build passed. Runtime
  app/database/Redis health and five identity/Verification OpenAPI contracts
  passed against 254 paths.
- No real role assignment or document upload was performed.
- Evidence: `docs/activity-center/phase-23-role-verification-multirole.md`.

### Step 23.9 Home Navigation Simplification + Deep-Link/Auth Hardening

- Replaced the long duplicated Home management menu with Activity Center,
  Unified Search, public discovery, authenticated Cart, Notification badge, and
  logout entry points.
- Added one shared session-recovery guard across Home and the private identity,
  Verification, Notification, Finance, Cart/Order, requester, owner, Seller,
  Service Provider, Lessor, and Consultant routes used by the center.
- Direct deep links now resolve the real session before building private
  content; unauthenticated/expired sessions render no child and return through
  the root Auth Gate. Backend permission checks remain final authority.
- Added authenticated/unauthenticated Guard Widget tests. Mobile analyze passed,
  all 52 tests passed, and final Web/Wasm build passed.
- No Backend/API/business behavior changed and generated Web output was not
  staged.
- Evidence: `docs/activity-center/phase-23-home-deeplink-auth-hardening.md`.

### Step 23.10 Docs, Tests, and Runtime Regression

- Consolidated the real Activity Center personal and four professional-role
  journeys, permission/auth boundaries, and explicit Runtime fixture limits.
- Added read-only `backend/scripts/activity_center_runtime_regression.py`; it
  verifies healthy application/database/Redis, 254-path OpenAPI, 16 required
  contract groups, and nine representative unauthenticated 401 boundaries
  without performing a mutation.
- Backend Ruff/compileall and all 164 tests passed with 18 known warnings.
  Alembic is current at `fdcb2ab80c12 (head)` and two Auth seed runs remained
  stable at 12 roles / 249 permissions.
- Mobile analyze, all 52 tests, and Web/Wasm build passed. Admin analyze, all
  17 tests, and Web/Wasm build passed.
- All 13 Postman collections and 313 requests parsed; all 125 templated raw JSON
  bodies parsed after variable normalization.
- Evidence: `docs/activity-center/phase-23-docs-tests-runtime-regression.md`.

### Step 23.11 Role-Based My Activity Center Release Gate + Tag

- Independently reran Backend Ruff/compileall and all 164 tests; all passed
  with the same 18 known deprecation warnings.
- Reran Mobile analyze, all 52 tests, and Web/Wasm build; all passed. Reran
  Admin analyze, all 17 tests, and Web/Wasm build; all passed.
- Verified Docker Backend/MySQL/Redis, Alembic head `fdcb2ab80c12`, two stable
  Auth seed runs at 12 roles / 249 permissions, 254-path OpenAPI, 16 Activity
  contract groups, nine private 401 boundaries, and zero Runtime mutations.
- All 13 Postman collections / 313 requests and 125 normalized raw JSON bodies
  passed parsing. Git release candidate was clean and synchronized.
- Phase 23 passed its release gate and is released as
  `v0.24.0-activity-center-foundation`.
- Evidence: `docs/activity-center/phase-23-release-gate.md`.

## Phase 19 — Reviews / Ratings / Reports

### Step 19.1 Real-State Audit + Contract Boundary

- Confirmed there is no marketplace Review/Rating model, migration, API,
  permission, Mobile/Admin feature, or Postman collection.
- Kept existing Social post/comment reports, Verification review logs, and
  future management `reports.*` permissions outside this shared marketplace
  Review engine.
- Confirmed the four authoritative eligibility sources: delivered Order,
  completed Service Request, completed Rental Request, and completed
  Consultation Request, always owned by the real Buyer/Requester.
- Identified Service Provider and Consultant rating/count fields as currently
  unbacked zero-valued placeholders; Product, Store, Equipment, and Lessor have
  no rating aggregates.
- Defined one shared 1–5 Review contract, exact-once source/subject ownership,
  public privacy, governed Review reports, atomic aggregates, moderation audit,
  and an implementation sequence through Step 19.11.
- Docker Desktop/Runtime was unavailable during this read-only audit, so no
  Runtime result is claimed; static source evidence is authoritative for 19.1.
- Evidence: `docs/reviews/phase-19-real-state-audit.md`.

### Step 19.2 Shared Review DB + Permission Foundation

- Added four inactive shared tables for marketplace Reviews, rating aggregates,
  Review reports, and exact-once moderation logs at Alembic head
  `a7c9e1f30d13`.
- Added database constraints for 1–5 scores, typed source/subject compatibility,
  owner/source/subject uniqueness, lifecycle/deletion consistency, aggregate
  ranges, one report per user/Review, and unique moderation event keys.
- Added eight dedicated owner/moderation permissions, assigned four owner
  permissions to customer/business roles, read-only access to Support, full
  moderation to Content Manager/Admin, and all eight to Super Admin.
- Ruff/compileall passed; four focused and all 168 Backend tests passed with 18
  known warnings. Real MySQL migration, two stable 12-role/257-permission seed
  runs, and app/database/Redis health passed.
- `alembic check` reports only the four known pre-existing Consultant/Services
  index reflection differences and no Review-table drift.
- No Review API, client behavior, notification, or fabricated rating was added.
- Evidence: `docs/reviews/phase-19-review-db-permissions.md`.

### Step 19.3 Eligibility, Ownership, Lifecycle + Review CRUD

- Added typed schemas, repository, domain eligibility service, exceptions, and
  authenticated create/list/detail/update/delete Review contracts.
- Backend locks and validates the real delivered Order or completed Service,
  Rental, or Consultation Request, requires its Buyer/Requester, verifies all
  seven subject types against domain data, and prevents self-review.
- Added deterministic duplicate conflict, owner-only privacy, active-only edit,
  hidden-owner delete, idempotent soft delete, 1–5 score, trimmed/bounded body,
  and immutable source/subject/reviewer identity.
- Ruff/compileall and all 180 Backend tests passed with 18 known warnings.
  Runtime app/database/Redis health, 257-path OpenAPI, three Review paths/five
  operations, and unauthenticated 401 passed.
- Added five-request Review Postman collection and complete owner API docs.
  Runtime has no terminal source fixtures, so no fake live Review was created;
  all seven populated eligibility branches are covered by focused tests.
- Aggregate/public reads remain inactive until Step 19.4.
- Evidence: `docs/reviews/phase-19-eligibility-review-crud.md`.

### Step 19.4 Public Reviews, Atomic Aggregates + Discovery Integration

- Added unauthenticated paginated public Review reads for every public Review
  subject, active-only visibility, safe display-name authors, and canonical
  average/count metadata without leaking reviewer/source/private data.
- Review create, score update, and active soft-delete now update the shared
  aggregate in the same transaction with deterministic two-decimal rounding.
- Synchronized legacy Service Provider/Consultant projections and exposed
  canonical ratings on public Product, Store, Service Offer, Rental Equipment,
  and Lessor discovery/detail contracts.
- Added public API documentation, focused contract coverage, and a sixth
  Review Postman request.
- Ruff/compileall and all 181 Backend tests passed with 18 known warnings.
  Runtime app/database/Redis health passed at Alembic head `a7c9e1f30d13`;
  OpenAPI exposes 258 paths including four Review paths, and the public
  missing-subject boundary returned 404.
- All 14 Postman collections / 319 requests passed JSON parsing.
- Evidence: `docs/reviews/phase-19-public-reviews-aggregates.md`.

### Step 19.5 Review Reports, Admin Moderation + Audit Logs

- Added governed Review reporting with six typed reasons, active-only targets,
  explicit self-report rejection, database-backed duplicate prevention, and a
  reporter-safe response.
- Added permission-separated Admin Review/report lists, Review hide/restore/
  delete, report review/resolve/dismiss, and immutable moderation-log reads.
- Review moderation changes the canonical aggregate atomically; deleted
  Reviews and resolved/dismissed reports are terminal, while unchanged
  operations are idempotent.
- Every effective transition writes actor, note, status transition, optional
  report link, timestamp, and unique event key to the durable audit table.
- Focused 17 and all 185 Backend tests passed with 18 known warnings.
- Ruff/compileall passed; runtime app/database/Redis health passed at Alembic
  head `a7c9e1f30d13`. OpenAPI exposes 264 paths / ten Review paths, all six new
  routes were present, and unauthenticated Admin Review/report reads returned
  401.
- All 14 Postman collections / 325 requests passed JSON parsing.
- Evidence: `docs/reviews/phase-19-review-reports-moderation.md`.

### Step 19.6 Notifications, Privacy, Exact-Once + Concurrency Hardening

- Added seven Review/report Notification event types using the existing routed
  Notification pipeline, stable persisted-identity keys, recipient/channel
  uniqueness, and self-notification suppression.
- Report creation targets active users by the real
  `review_reports.admin_read` permission; moderation notifies the Review
  author and report resolution notifies the reporter.
- Minimized payloads exclude Review/report/resolution text, contacts, private
  source identity, and unrelated reporter identity.
- Hardened concurrent first-Aggregate creation with a savepoint, unique-row
  recovery, and locking read before atomic delta application.
- Added focused coverage for stable keys, privacy-safe payloads, permission
  recipients, aggregate recovery use, and existing exact-once contracts.
- Ruff/compileall and all 186 Backend tests passed with 18 known warnings.
- Runtime app/database/Redis health passed at Alembic head `a7c9e1f30d13`;
  OpenAPI remained 264 paths / ten Review paths. Permission-based recipient
  lookup resolved the real seeded Review Admin, and a rolled-back
  `review.reported` event smoke left zero rows.
- All 14 Postman collections / 325 requests remained JSON-valid; no API request
  was added because this step hardens existing contracts.
- Evidence: `docs/reviews/phase-19-notification-privacy-hardening.md`.

### Step 19.7 Mobile Review Creation, History + Public Rendering

- Added one typed shared Mobile Review API/repository/model foundation for all
  seven subjects, including public ratings, owner history, create, update, and
  delete contracts.
- Added a protected 1–5-star creation form, permission-aware `نظرات من`
  Activity Center entry, lifecycle-aware history edit/delete, and complete
  loading/error/empty/saving states.
- Connected eligible creation actions to delivered Orders and completed
  Service, Rental, and Consultant Requests; Backend remains authoritative.
- Added reusable public Review rendering to Product, Store, Service Offer,
  Rental Equipment, and Consultant detail screens.
- Flutter analyze passed, all 54 tests passed including three focused Review
  model contracts, and Flutter Web build/Wasm dry run passed.
- Evidence: `docs/reviews/phase-19-mobile-reviews.md`.

### Step 19.8 Admin Review/Report Moderation Panel

- Added a typed Admin Reviews feature with API/repository/state layers for
  Review, report, moderation-log, and pagination contracts.
- Added permission-guarded route/sidebar navigation and two responsive tabs
  with status filters, pagination, refresh, loading, error, empty, and saving
  states.
- Added Review hide/restore/terminal-delete and report reviewed/resolved/
  dismissed actions, all requiring a moderation note, plus an immutable audit
  timeline dialog.
- No raw JSON reaches UI; terminal/invalid actions are hidden or disabled while
  Backend permissions and lifecycle remain authoritative.
- Admin Flutter analyze passed, all 20 tests passed including four focused
  Review contracts, and Web build/Wasm dry run passed.
- Runtime app/database/Redis health remained `ok`; OpenAPI remained 264 paths
  with all five Admin Review route groups present.
- Evidence: `docs/reviews/phase-19-admin-moderation-panel.md`.

### Step 19.9 Cross-Domain Contract + Runtime Hardening

- Added explicit typed OpenAPI response envelopes to every Admin Review/report
  list, status-update, and moderation-log route group.
- Unified Product, Store, and Rental Equipment Search results now read average
  and count from the canonical shared Review aggregate, matching the existing
  Service and Consultant integration without synthetic data.
- Preserved existing API paths, Review lifecycle, Search visibility/privacy,
  Mobile behavior, Admin behavior, and `TOMAN` money contracts.
- Ruff/compileall and all 186 Backend tests passed with 18 known warnings.
- Mobile analyze, all 54 tests, and Web build/Wasm dry run passed.
- Admin analyze, all 20 tests, and Web build/Wasm dry run passed.
- Runtime app/database/Redis health passed at Alembic head `a7c9e1f30d13`;
  OpenAPI remained 264 paths / ten Review paths and the typed Admin response
  references were verified from the live schema.
- All 14 Postman collections / 325 requests passed JSON parsing. No request was
  added because this step hardens existing contracts.
- Evidence: `docs/reviews/phase-19-cross-domain-runtime-hardening.md`.

### Step 19.10 Docs, Postman + Runtime Regression

- Consolidated the complete owner, public, reporting, Admin moderation,
  aggregate, privacy, and audit-log API documentation.
- Updated the Review Postman collection metadata and replaced the hard-coded
  report resolution ID with the reusable `review_report_id` variable; all 12
  implemented Review operations remain represented.
- Added a reusable read-only Runtime regression covering health, all ten Review
  OpenAPI path groups, typed responses, seven subject/four source enums, public
  privacy, seven unauthenticated boundaries, and missing-subject 404 behavior.
- Ruff/compileall and all 186 Backend tests passed with 18 known warnings.
- Mobile analyze, all 54 tests, and Web build/Wasm dry run passed.
- Admin analyze, all 20 tests, and Web build/Wasm dry run passed.
- Runtime app/database/Redis health, Alembic head `a7c9e1f30d13`, and two
  idempotent Auth seed runs at 12 roles / 257 permissions passed.
- All 14 Postman collections / 325 requests / 130 raw bodies parsed; the
  Runtime regression performed zero successful mutations.
- Evidence: `docs/reviews/phase-19-docs-postman-runtime-regression.md`.

### Step 19.11 Reviews / Ratings / Reports Release Gate + Tag

- Re-ran the complete Backend, database/seed, Runtime/OpenAPI, Review
  regression, Mobile, Admin, Postman, and Git release gate without adding
  features or changing behavior.
- Ruff/compileall and all 186 Backend tests passed with 18 known warnings.
- Alembic upgraded/current at `a7c9e1f30d13`; two Auth seed runs remained
  stable at 12 roles / 257 permissions; app/database/Redis health passed.
- The read-only Review regression verified ten path groups, typed contracts,
  seven subjects, four sources, privacy/access boundaries, and zero mutations.
- Mobile analyze, all 54 tests, and Web/Wasm build passed.
- Admin analyze, all 20 tests, and Web/Wasm build passed.
- All 14 Postman collections / 325 requests / 130 raw JSON bodies parsed.
- The release candidate was clean and synchronized on `develop`; Phase 19 is
  released as `v0.25.0-reviews-foundation`.
- Evidence: `docs/reviews/phase-19-release-gate.md`.

## Phase 22 — Production Hardening / Deployment

### Step 22.1 Production Readiness Real-State Audit

- Recorded owner decision to defer Phase 21 AI/RAG and make Phase 22 the active
  engineering track.
- Reverified clean/synchronized `develop` at
  `v0.25.0-reviews-foundation`, healthy Backend/MySQL/Redis Runtime, single
  Alembic head, 98 tables, and the latest Backend/Mobile/Admin/Postman gates.
- Confirmed production blockers: no CI/CD or production/staging topology,
  placeholder Nginx/backup, no worker orchestration/observability/recovery
  evidence, and disabled credentialed providers.
- Identified governance/security/contract debt: `main` 122 commits behind,
  inconsistent app versions, four Alembic index drifts, 281/303 operations
  without useful typed success schemas, unsafe-default guard gaps, deferred
  refresh rotation, non-secure Mobile token storage, and shallow E2E coverage.
- Kept AI/RAG and new business modules outside Phase 22.
- Defined a bounded Step 22.2–22.13 implementation and release sequence.
- No application, API, database, client, provider, or infrastructure behavior
  changed.
- Evidence: `docs/production/phase-22-real-state-audit.md`.

### Step 22.2 Release, Branch, Version + Documentation Governance

- Defined authoritative roles for `develop`, `release/vX.Y.Z`, `main`, and
  `hotfix/vX.Y.Z`, plus fast-forward/reviewed promotion and immutable annotated
  tag rules.
- Classified historical `*-foundation` tags as development milestones rather
  than retroactive production-deployment claims.
- Set the next shared product line to `0.26.0-dev.1`: PEP 440
  `0.26.0.dev1` for Backend and build `+26` for both Flutter clients.
- Updated the stale progress header and documented the difference between
  roadmap phases, historical step numbers, and semantic release versions.
- Selected `v0.25.0-reviews-foundation` as the safe stable `main` recovery
  target; later Phase 22 commits remain on `develop`.
- Promoted the exact stable-tag tree to `main` through non-force merge commit
  `c6ac2f1`, preserving the newer remote PR ancestry, then merged that history
  back into `develop` with zero file-tree change.
- No application/API/database/client behavior or runtime secret changed.
- Evidence: `docs/production/release-branch-version-governance.md`.

### Step 22.3 Production Configuration, Secret + Dev-Switch Safety

- Added startup fail-fast validation for staging/production debug, Dev OTP,
  JWT/Super Admin defaults, HTTPS base URLs/CORS, rate limiting, database/Redis
  credentials, absolute Media storage, and production payment sandbox.
- Enabled Email/SMS/Push/Payment providers now require a complete supported and
  transport-safe configuration instead of silently accepting partial config.
- Removed the static OTP fallback when Dev OTP is disabled; codes now use a
  six-digit cryptographic random source and are not returned to the client.
- Aligned local Media storage with the documented `MEDIA_STORAGE_DIR` setting
  and added a non-secret runtime configuration validation command.
- Added seven focused safety contracts. Ruff/compileall and all 193 Backend
  tests passed; unsafe production failed with stable codes and no secret echo.
- Local Docker development app/database/Redis health remained `ok`.
- Real OTP/provider delivery and credentialed network verification remain
  explicitly deferred to Step 22.10.
- Evidence: `docs/production/production-config-safety.md`.

### Step 22.4 Database Drift, Migration + Backup/Restore Hardening

- Added Alembic revision `b8d4f2c71e04` to remove four redundant unnamed
  Consultant/Service unique indexes while preserving the canonical named
  unique indexes and uniqueness contracts.
- Downgrade, upgrade, and `alembic check` passed; reflected database metadata
  now matches the SQLAlchemy model metadata.
- Replaced the backup placeholder with atomic MySQL/Media backup, versioned
  manifest, byte-size and SHA-256 verification, archive traversal/link
  rejection, and explicit-confirmation restore tooling.
- Created and verified a real local backup, then restored it to the isolated
  `farmnet_restore_22_4` database; all 98 tables were present and the drill
  database was removed afterward.
- Backup safety tests: 8 passed. Backend Ruff/compileall and all 193 Backend
  tests passed with 18 known warnings; app/database/Redis health remained `ok`.
- Production off-host storage, scheduling, retention, alerting, and recovery
  orchestration remain bounded infrastructure work for later Phase 22 steps.
- Evidence: `docs/production/database-backup-restore-hardening.md`.

### Step 22.5 Typed OpenAPI Response Contract Hardening

- Added the `StandardSuccessEnvelope` OpenAPI component for legacy JSON routes
  while preserving all 22 existing exact domain response models.
- Every one of 303 operations across 264 paths now has a non-empty successful
  response schema: 278 shared envelopes, 22 exact domain models, and three
  binary Media download contracts.
- Corrected the three Media access specifications to
  `application/octet-stream` binary responses instead of empty JSON schemas.
- Added regression tests for complete success-schema coverage, real envelope
  compatibility, exact-model precedence, and binary response accuracy.
- No runtime serialization, endpoint behavior, database, permission, Mobile,
  or Admin behavior changed.
- Backend Ruff/compileall passed; Backend tests reported 197 passed with 18
  known warnings and backup-tool tests reported 8 passed.
- Mobile analyze/all 54 tests and Admin analyze/all 20 tests passed. Runtime
  app/database/Redis health remained `ok`.
- Evidence: `docs/api/openapi-success-contract.md`.

### Step 22.6 Authentication, Session + Token Storage Hardening

- Bound every new access/refresh token to an existing database session through
  `sid`; access tokens now also carry unique `jti` values.
- Enforced active, unexpired, same-user session validation on every
  authenticated Backend request, making logout invalidate access immediately.
- Added transaction-locked, one-time refresh-token rotation without extending
  the original session lifetime.
- Added replay detection: reuse of a known revoked refresh token revokes the
  complete session and all active tokens in its family.
- Replaced plaintext Mobile/Admin `SharedPreferences` bearer storage with
  `flutter_secure_storage`, including one-time legacy migration and erasure.
- Corrected the broad Git `storage/` ignore rule that had hidden both client
  token-storage source files; runtime storage remains ignored.
- Added six Backend session/rotation tests and three secure-storage tests per
  Flutter client.
- Backend Ruff/compileall passed; 203 Backend and eight backup-tool tests
  passed. Mobile analyze/57 tests/Web build and Admin analyze/23 tests/Web
  build passed.
- Real Runtime OTP/login/access/rotation/replay smoke passed, its fixture was
  removed, and app/database/Redis health remained `ok`.
- Documented the residual Web bearer/XSS boundary and mandatory HTTPS,
  HSTS/CSP controls without introducing an unplanned cookie/CSRF API migration.
- Evidence: `docs/production/auth-session-token-storage-hardening.md`.

### Step 22.7 Abuse Protection, Security Headers + Transport Hardening

- Added atomic Redis-backed distributed rate limiting for staging/production
  while retaining bounded in-memory development behavior.
- Added independent general, Search, and sensitive Auth limits; Redis failure
  now fails closed with a stable HTTP 503 contract.
- Hardened trusted-proxy parsing with IP/CIDR allowlists and right-to-left XFF
  chain resolution to prevent spoofed-first-value bypasses.
- Added global security headers, protected-response `no-store`, trusted HTTPS
  HSTS, explicit CORS methods/headers, and exposed rate-limit/trace headers.
- Production-like startup now requires Redis rate limiting and an explicit
  trusted immediate proxy.
- Replaced the Nginx placeholder with a TLS 1.2/1.3, HTTP redirect, edge-limit,
  security-header, bounded-size/timeout, and canonical proxy-header template.
- Focused regressions reported 19 passed; full Backend reported 212 passed
  with 27 known warnings and eight backup-tool tests passed.
- Real Redis atomic limiting, Runtime Auth 429/headers, CORS/security headers,
  `nginx -t`, app/database/Redis health, and Alembic no-drift checks passed.
- Mobile/Admin behavior did not change; their Step 22.6 gate remains the
  applicable client baseline.
- Evidence: `docs/production/abuse-security-transport-hardening.md`.

### Step 22.8 Production Topology, Container + Worker Hardening

- Added a production Compose topology for internal MySQL/Redis, one-shot
  migration, non-root Backend, independent Email/SMS/Push workers, and the
  Nginx TLS edge; only Nginx publishes host ports.
- Added digest-pinned base/service images, a multi-stage read-only Backend
  runtime, version-locked Python dependencies, strict Docker build exclusions,
  persistent database/Redis/Media volumes, resource/log limits, and reduced
  Linux privileges.
- Added regular-file secret loading through `*_FILE` settings without secret
  echo, plus ignored local production secret/config paths.
- Replaced one-batch notification execution with supervised long-running
  workers supporting graceful shutdown, structured logs, isolated database
  sessions, atomic heartbeat state, and failure/staleness health contracts.
- A complete isolated Production topology drill passed: migration exited `0`;
  Backend, three workers, MySQL, Redis, and Nginx were healthy; HTTPS health
  reported app/database/redis `ok`; Backend ran as `10001` with a read-only
  root filesystem; MySQL/Redis had no host port bindings.
- The drill's containers, networks, and volumes were removed afterward.
- Backend Ruff/compileall passed and all 217 Backend tests passed with 27 known
  deprecation warnings.
- Real production deployment, certificate automation, immutable registry
  publication/scanning, provider credentials, monitoring, and rollout remain
  later Phase 22 work.
- Evidence:
  `docs/production/production-topology-container-worker-hardening.md`.

### Step 22.9 Observability, Readiness, Metrics + Alerting

- Separated dependency-free `/live` from dependency-aware `/ready`; readiness
  returns 503 when MySQL or Redis is unavailable while legacy health contracts
  remain unchanged.
- Added JSON request logs with sanitized trace IDs, normalized routes, status,
  and duration without query/body/header/credential capture.
- Added low-cardinality HTTP, build-info, in-progress, latency, and dependency
  readiness Prometheus metrics.
- Added internal-only, digest-pinned, non-root Prometheus and Alertmanager
  services with persistent data, retention, health, resource, and security
  boundaries; Nginx blocks public `/metrics` and `/ready`.
- Added five availability/readiness/error-ratio/latency alert rules and
  deterministic firing tests.
- A complete isolated Production drill passed all service health checks,
  three live Prometheus targets, JSON log correlation, public probe isolation,
  Prometheus/Alertmanager validation, and alert firing tests.
- Ruff/compileall and all 222 Backend tests passed with 27 known warnings.
- Real operator paging remains explicitly unconfigured pending an owner-chosen
  incident channel and credentials; no delivery claim is made.
- Evidence: `docs/production/observability-readiness-metrics-alerting.md`.

### Step 22.10 Credentialed Staging Provider Verification — Active/Blocked

- Added a redacted preflight/execute harness for SMTP Email, HTTP JSON SMS,
  HTTP JSON Push, and Zarinpal sandbox.
- Execute mode is fail-closed outside staging, requires an exact confirmation
  phrase and external test destination, and never outputs secret, recipient,
  token, URL, provider response, or exception-message data.
- Added a non-secret staging provider template and four safety tests.
- Thirty-one focused notification/payment/gate tests and all 226 Backend tests
  passed.
- Actual environment preflight safely returned `PROVIDER_DISABLED` for all
  four providers; no credential or approved test destination exists and no
  external request was attempted.
- SMS/Push vendor compatibility must be confirmed against the generic
  Bearer-auth HTTP JSON contract or implemented through a vendor adapter.
- This step is not complete and must not be reported as credentialed success.
- Evidence:
  `docs/production/credentialed-staging-provider-verification.md`.

## Phase 24 — Farm Management / Digital Farm Profiles

### Step 24.1 Real-State Audit + Domain/Privacy Boundary

- Confirmed no Farm, Plot, Crop Cycle, soil/water/irrigation, operation diary,
  or farm-specific Mobile/Admin/API model currently exists.
- Separated personal Profile, Geo, Weather, Activity, marketplace, and future
  AI responsibilities from the new private Farm aggregate.
- Defined multiple farms per user, nested plots/history, canonical square-metre
  area, hierarchical Geo validation, archive-first lifecycle, and private
  coordinates/boundaries.
- Defined the crop-reference, cycle, soil/water, operation, Weather, Mobile,
  Activity/Admin, documentation, regression, and release sequence.
- Kept Phase 22.10 honestly open on external credentials and prohibited AI/RAG
  from consuming incomplete farm data as if production-ready.
- No application/API/database/client behavior changed.
- Evidence: `docs/farms/phase-24-real-state-audit.md`.

### Step 24.2 Crop/Measurement References, Permissions + DB Contract

- Added four reference tables for measurement units, crop categories, crops,
  and curated crop varieties through Alembic revision `c3e7a9f41b02`.
- Established square metre as the canonical area base, positive conversion
  factors, annual/perennial crop types, restricted reference deletion, and
  explicit uniqueness/index contracts.
- Added an idempotent reference seed with 8 units, 7 categories, and 13 crops;
  no unverified varieties were guessed.
- Added own-farm, farm-admin, reference-read, and reference-management
  permissions with least-privilege role mappings.
- Migration upgrade and no-drift checks passed against MySQL; Auth and Farm
  seeds each ran twice with stable counts; app/database/Redis health was `ok`.
- Ruff/compileall passed, 4 focused tests passed, and all 230 Backend tests
  passed with 27 existing deprecation warnings.
- Mobile/Admin were unchanged and therefore not rebuilt in this Backend-only
  foundation step.
- Evidence:
  `docs/farms/phase-24-reference-permission-db-contract.md`.

### Step 24.3 Owner-Scoped Farm CRUD + Archive Lifecycle

- Added the private `farms` aggregate with an authenticated owner, normalized
  name/description, active/archive lifecycle, consistent archive metadata, and
  owner-scoped indexes through Alembic revision `d4f8b0a52c13`.
- Added typed create/list/detail/update/archive/restore APIs; list pagination
  excludes archived farms by default.
- Owner identity is never accepted from client data. Every lookup includes the
  authenticated owner, and cross-owner requests return the same 404 contract
  as nonexistent records.
- No destructive Farm delete or public Farm discovery route exists.
- Archived farms are immutable until explicitly restored.
- Ruff/compileall, 10 focused tests, all 236 Backend tests, MySQL migration and
  no-drift checks, typed OpenAPI contracts, and app/database/Redis health
  passed.
- Mobile/Admin were unchanged in this Backend-only step.
- Evidence: `docs/farms/phase-24-owner-farm-crud-archive.md`.

### Step 24.4 Plot, Geo Point/Boundary + Area Consistency

- Added positive declared Farm area and private nested Plot records through
  Alembic revision `e5a9c1b63d24`.
- Stored area canonically in square metres and serialized optional exact point
  and closed-boundary data only through authenticated owner APIs.
- Added complete active Geo hierarchy checks across Province, County,
  District, Rural District, City, and Village.
- Locked the owner Farm before allocation changes and prevented total Plot area
  (including retained archived Plots) from exceeding declared Farm area.
- Added typed list/create/detail/update/archive/restore Plot routes with
  cross-owner 404 behavior and no public Farm/Plot route.
- Ruff/compileall, 18 focused tests, all 244 Backend tests, MySQL migration,
  Alembic no-drift, OpenAPI privacy contracts, and health passed.
- Evidence: `docs/farms/phase-24-plot-geo-boundary-area.md`.

### Step 24.5 Crop Catalog, Varieties + Crop-Cycle Lifecycle

- Added authenticated read APIs for active crop categories, crops, and curated
  varieties.
- Added owner-scoped Plot crop cycles through Alembic revision
  `f6bad2c74e35`, with planned/actual dates and explicit lifecycle transitions.
- Enforced crop/variety membership and rejected overlaps unless every involved
  cycle explicitly uses `intercrop`.
- Allowed edits only while planned and retained completed/cancelled history.
- Ruff/compileall, 24 focused tests, all 250 Backend tests, MySQL migration,
  no-drift, OpenAPI privacy contracts, and health passed.
- Evidence: `docs/farms/phase-24-crop-catalog-cycle-lifecycle.md`.

### Step 24.6 Soil, Water, Irrigation + Laboratory Observations

- Added one owner-private soil and irrigation profile per Plot, retained Farm
  water sources, and dated soil/water observations through revision
  `07cbe3d85f46`.
- Enforced soil texture/depth, water source lifecycle, irrigation efficiency,
  exact-one observation subject, ordered dates, nonnegative values, and
  metric-specific canonical units.
- Kept laboratory values as observations without generating agricultural
  prescriptions or AI conclusions.
- Ruff/compileall, 28 focused tests, all 254 Backend tests, migration replay,
  Alembic no-drift, OpenAPI privacy, and health passed.
- Evidence: `docs/farms/phase-24-soil-water-irrigation-lab.md`.

### Step 24.7 Operation Diary, Inputs, Harvest + Farm Media

- Added operations, measured operation inputs, harvest observations, and
  exact-one-subject media links through revision `18dcf4e96057`.
- Limited new records to active owner-scoped cycles and rejected dates before
  the actual cycle start.
- Required positive active measurement units and limited harvest units to mass
  or count.
- Required attached media to be active, private, owned by the authenticated
  user, and uploaded for `farm_record`; duplicate subject attachments are
  rejected.
- Added typed private APIs for operation/input, harvest, and media workflows;
  no public Farm diary route or destructive history rewrite exists.
- Ruff/compileall, 33 focused Farm tests, all 259 Backend tests, MySQL
  migration/no-drift, fresh container build, OpenAPI contracts, and
  app/database/Redis health passed.
- Evidence:
  `docs/farms/phase-24-operation-diary-inputs-harvest-media.md`.

### Step 24.8 Privacy, Concurrency, Audit + Retention Hardening

- Added append-only, owner-attributed Farm audit events through revision
  `29edf5a07168`; events commit atomically with each Farm-domain mutation.
- Kept audit payloads minimal and excluded Farm names, descriptions,
  coordinates, boundaries, observations, notes, and captions.
- Confirmed stable Farm/Plot/Cycle row-lock boundaries for conflicting
  mutations.
- Added ORM update/delete guards for diary, harvest, lab, Farm-media, and audit
  records, plus closed-cycle update and all-cycle delete protection.
- Retained archive-first lifecycle with no automatic purge or destructive owner
  endpoint; account-erasure policy remains an explicit future governance task.
- Ruff/compileall, 10 audit/retention tests, 43 focused Farm tests, all 269
  Backend tests, MySQL migration/no-drift, fresh container build, and
  app/database/Redis health passed.
- Evidence:
  `docs/farms/phase-24-privacy-concurrency-audit-retention.md`.

### Step 24.9 Farm Weather Linking + Contextual Alerts

- Added one-to-one Plot Weather links and private/public Weather-location scope
  through revision `3af106b82c79`.
- Kept existing locations backward-compatible and public while excluding
  private Farm locations from normal Weather lookup/current/forecast/alert
  routes.
- Reused the existing provider, 30/180-minute cache, forecast persistence,
  alert rules, duplicate detection, and Notification foundation.
- Omitted coordinates, internal location IDs, and owner IDs from contextual
  responses and notifications; private alerts notify only the Farm owner.
- Added owner-private current/forecast/alert, explicit refresh, coordinate
  synchronization, missing-coordinate validation, and audit contracts.
- Ruff/compileall, 6 Farm Weather tests, 49 focused Farm tests, all 275 Backend
  tests, MySQL migration/no-drift, fresh container build, OpenAPI paths, and
  app/database/Redis health passed.
- Evidence: `docs/farms/phase-24-farm-weather-contextual-alerts.md`.

### Step 24.10 Mobile My Farms, Plots, Cycles + Diary

- Added a typed authenticated Mobile Farms feature for Farm and Plot
  create/list, crop-cycle create/list/transitions, operation diary, harvest,
  and contextual Plot Weather.
- Added protected nested routes plus Home and permission-aware Activity Center
  navigation.
- Added explicit loading, empty, error, refresh, inactive-cycle, and
  missing-coordinate states.
- Added an authenticated active measurement-unit reference endpoint so Mobile
  harvest uses friendly mass/count choices instead of database IDs.
- Backend Ruff/compileall, all 276 Backend tests, runtime health, 63 Mobile
  tests, and Mobile Web build passed.
- Farm Mobile code has no analyzer diagnostics. Seven non-fatal pre-existing
  `withOpacity` deprecation infos remain in a shared card and concurrently
  edited Auth UI and were not mixed into this commit.
- Evidence: `docs/farms/phase-24-mobile-my-farms.md`.

### Step 24.11 Activity Center + Restricted Admin Support

- Retained the role/permission-aware Mobile Activity Center Farm entry.
- Added read-only Admin Farm list/detail/audit APIs and a typed Admin page with
  search, lifecycle filtering, pagination, summaries, and audit history.
- Enforced `farms.admin_read` in Backend and Admin routing.
- Excluded exact location, boundary, lab, diary, and media/storage data; no
  write or ownership-transfer action is available.
- Backend Ruff/compileall, 2 focused tests, all 278 Backend tests, Admin
  analyze, 24 Admin tests, and Admin Web build passed.
- Evidence: `docs/farms/phase-24-activity-admin-support.md`.

### Step 24.12 Docs, Postman + Runtime Regression

- Added the Farm API overview, complete 42-request Postman collection, its
  deterministic generator, and a read-only Runtime regression.
- Verified 41 Farm/Admin Farm OpenAPI operations, six private 401 boundaries,
  Alembic `3af106b82c79 (head)`, twice-idempotent seed, and healthy
  app/database/Redis.
- Backend: 278 tests; Mobile: 63 tests and Web build; Admin: 24 tests and Web
  build. All 16 Postman collections / 398 requests parse.
- Evidence: `docs/farms/phase-24-docs-postman-runtime-regression.md`.

### Pre-release Mobile Auth UI Reconciliation

- Added responsive login backgrounds, a reusable glass card, and visually
  aligned email/OTP authentication screens without changing Auth contracts.
- Mobile analyze is clean; all 63 tests and Web/Wasm build passed.
- Generated platform registrants and local Flutter migration output were not
  included.

### Step 24.13 Farm Management Release Gate + Tag

- Independent Git/content/verification gates passed on clean `develop`.
- Created the annotated non-production milestone
  `v0.26.0-farm-management-foundation`.
- Production release claims remain excluded by release governance.
- Evidence: `docs/farms/phase-24-release-gate.md`.

## Phase 25 — Unified Subscription & Entitlement Platform

### Step 25.1 Real-State Audit + AI Entitlement Boundary

- Confirmed Subscription is documented and permission-seeded but has no real
  models, tables, migrations, APIs, or UI.
- Defined one product-wide role-independent Entitlement platform; AI is a
  consumer, not a separate subscription system.
- Fixed permission + entitlement + quota enforcement, TOMAN-only billing,
  atomic reservation, non-paywalled safety, and marketplace-invoice reuse
  boundaries.
- Approved Steps 25.2 through 25.12.
- Evidence: `docs/subscriptions/phase-25-real-state-audit.md`.

### Step 25.2 Plan, Feature, Subscription + Entitlement DB Contract

- Added eight normalized tables for plans, features, plan values,
  subscriptions, periods, entitlement snapshots, usage, and reservations.
- Enforced TOMAN-only plan/period money, free-plan price, typed feature,
  validity-range, non-negative usage, and idempotent reservation constraints.
- Added five owner-facing permissions without changing existing Admin
  permissions.
- Alembic `96f4165b43fe`, no drift, seed 12 roles / 268 permissions, 3 focused
  and all 281 Backend tests, Ruff/compileall, and runtime health passed.
- Evidence: `docs/subscriptions/phase-25-db-contract.md`.

### Step 25.3 Plan Catalog + Public/User Read APIs

- Added an idempotent 15-feature registry and active Free v1 plan with 15 typed
  values and TOMAN 0.
- Added public active-plan list/detail plus authenticated own subscription,
  entitlement, and usage reads.
- Owner reads are non-mutating and return an explicit empty state before
  lifecycle provisioning.
- Seed twice, 5 focused and all 283 Backend tests, no drift, runtime catalog,
  three 401 owner boundaries, Ruff/compileall, and health passed.
- Evidence: `docs/subscriptions/phase-25-plan-catalog-read-apis.md`.

### Step 25.4 Subscription Lifecycle, Periods + Cancellation

- Added idempotent Free provisioning with owner locking, a 30-day snapshotted
  period, 15 Entitlements, and usage rows for five enabled metered features.
- Added end-period cancel, resume, immediate Free-only cancel, reactivation,
  reason capture, and optimistic version conflicts.
- Paid activation and immediate paid cancellation remain blocked until the
  financial contract is implemented.
- Runtime lifecycle, 8 focused and all 286 Backend tests, Ruff/compileall,
  no-drift, and health passed.
- Evidence: `docs/subscriptions/phase-25-lifecycle-periods-cancellation.md`.

### Step 25.5 Atomic Quota Reservation, Usage + Idempotency

- Added a non-mutating owner quota-estimate API and kept all quota mutations
  behind an internal Backend service boundary.
- Added row-locked reserve, exact-once finalize, idempotent release/expiry,
  replay-safe idempotency keys, and limit checks over used plus reserved quota.
- Enforced active metered Entitlements, ownership privacy, bounded TTL, and
  Decimal(18,4) quota values without mixing quota with TOMAN billing.
- Real MySQL reserve/replay/release restoration, 14 focused and all 292
  Backend tests, Ruff/compileall, Alembic no-drift, and health passed.
- Evidence: `docs/subscriptions/phase-25-atomic-quota.md`.

### Step 25.6 TOMAN Invoice, Wallet + Payment Integration

- Added an explicit platform-owned Subscription Invoice contract without a
  fake provider while preserving all marketplace provider requirements.
- Added idempotent Checkout and Verify, pending-before-payment lifecycle,
  Zarinpal reuse, non-production-only mock verification, TOMAN snapshots, and
  one exact-once balanced platform cash/revenue journal.
- Entitlements are created only after verified payment; a Free upgrade closes
  only at that point, and concurrent active paid access is rejected.
- Alembic `7b98f2da6a10`, 22 focused and all 300 Backend tests,
  Ruff/compileall, no-drift, transaction-rolled-back real MySQL commerce, and
  app/database/Redis health passed.
- Evidence: `docs/subscriptions/phase-25-toman-commerce.md`.

### Step 25.7 Renewal, Expiry, Grace Period + Notifications

- Added automatic Free renewal, end-period cancellation, three-day paid
  Grace, paid renewal Checkout/Verify, and terminal expiry with matching
  Entitlement boundaries.
- Renewal uses its own platform-owned TOMAN Period/Invoice/Payment contract
  and exact-once Entitlement snapshot.
- Added five deterministic lifecycle events and a bounded row-locked
  `SKIP LOCKED` processor/CLI for scheduler execution.
- Alembic `bc620ec4f128`, 27 focused and all 305 Backend tests,
  Ruff/compileall, no-drift, real rolled-back MySQL renewal/expiry, empty
  worker execution, and app/database/Redis health passed.
- Evidence: `docs/subscriptions/phase-25-renewal-grace-notifications.md`.

### Step 25.8 Mobile Plans, Current Subscription, Usage + Checkout

- Added typed Mobile plan, subscription, entitlement, usage, checkout, and
  verification contracts over the real Billing APIs.
- Added a protected, permission-backed Subscription Center with TOMAN plan
  selection, Free activation, paid checkout/renewal, cancellation/resume,
  lifecycle/grace state, and metered usage including reservations.
- Kept payment activation server-authoritative: local development uses the
  Backend mock flow and non-local checkout delegates to Zarinpal.
- Focused analyze, all 68 Mobile tests, web build, and Wasm dry-run passed.
- Full analyze retains two unrelated concurrent warnings in Home and Social
  files; those user changes were not modified or included.
- Evidence: `docs/subscriptions/phase-25-mobile-subscriptions.md`.

### Step 25.9 Admin Plans, Subscriptions, Usage + Manual Operations

- Added seven permission-protected Admin Billing APIs for versioned plan
  management, subscription list/detail/usage, manual activation, and
  version-checked cancellation.
- Kept active plans immutable and prevented retirement of the default Free
  plan.
- Manual activation records Admin actor/reason and Admin-sourced
  Entitlements, while creating no fake payment or invoice.
- Added a typed permission-aware Admin Panel with filters, pagination,
  lifecycle operations, TOMAN prices, provenance, and usage visibility.
- Migration `d8f3a9c21b74`, 31 focused and all 309 Backend tests,
  Ruff/compileall, no-drift, seed twice, runtime OpenAPI/401/health, all 26
  Admin tests, analyze, and web build passed.
- Concurrent Mobile design changes were not modified or included.
- Evidence: `docs/subscriptions/phase-25-admin-subscriptions.md`.

### Step 25.10 Security, Concurrency, Audit + Reconciliation Hardening

- Added MySQL Generated unique slots for one active plan version per code and
  one active/grace subscription per user.
- Added immutable exact-once Billing Audit for Admin, user, checkout/payment,
  and Worker lifecycle changes from migration time forward.
- Added dedicated audit/reconciliation permissions and a typed Admin
  Audit/Reconciliation view.
- Added a read-only API and CLI that reconcile Subscription, Period,
  Entitlement, Usage, Invoice, Payment, and Ledger without automatic repair.
- Real runtime reconciliation was clean across 2 subscriptions, 2 periods, 30
  Entitlements, 10 Usage rows, and zero issues.
- Migration `e17c4b82a6d9`, all 314 Backend and 27 Admin tests,
  Ruff/compileall, Admin analyze/build, no-drift, seed twice with 270
  permissions, nine runtime paths, authenticated audit/reconciliation, and
  health passed.
- Concurrent Mobile design changes were not modified or included.
- Evidence:
  `docs/subscriptions/phase-25-security-audit-reconciliation.md`.

### Step 25.11 Docs, Postman + Runtime Regression

- Added the canonical Billing API, lifecycle, privacy, permission, TOMAN,
  payment, Audit, and reconciliation documentation for all 22 runtime paths
  and 23 operations.
- Added a 30-request Subscriptions Postman collection covering every runtime
  operation and seven negative/replay contracts.
- Added automated checks for complete OpenAPI operation coverage, parseable
  variable-resolved JSON bodies, documentation path coverage, and obvious
  secret exclusion.
- Updated the roadmap, database, permissions, and Postman indexes to match the
  deployed ten-table and 15-permission implementation.
- Read-only runtime regression passed for public/owner/Admin reads, privacy,
  callback failure, clean reconciliation, OpenAPI, and app/database/Redis
  health.
- Ruff, compileall, all 316 Backend tests, all collection JSON parses, Alembic
  head/no-drift, and seed twice with 270 permissions passed.
- State-changing Postman execution was reserved for an isolated synthetic
  environment. No Mobile or Admin source changed; concurrent Mobile work was
  not modified or included.
- Evidence: `docs/subscriptions/phase-25-docs-postman-runtime.md`.
- Next: Step 25.12 Subscription Release Gate + Tag.

### Step 25.12 Unified Subscription Release Gate + Tag

- Passed the final independent Backend, Runtime, Mobile, Admin, Postman, and
  Git safety gates.
- Stabilized the concurrent Mobile redesign in independent commit `03258c0`;
  Mobile analyze reported no issues, 68 tests passed, and Web build passed.
- Final Backend Ruff/compileall and all 316 tests passed.
- Final Admin analyze, all 27 tests, and Web build passed.
- Alembic remained at `e17c4b82a6d9` with no drift; two auth seeds retained 12
  roles and 270 permissions.
- Runtime reconciliation remained clean with zero issues and
  app/database/Redis health all reported `ok`.
- All 16 Postman collections parsed; Billing remained 22 OpenAPI paths, 23
  operations, and 30 Subscription requests.
- Released as `v0.27.0-subscriptions-foundation`.
- Phase 25 Unified Subscription & Entitlement Platform: complete.
- Next: resume Phase 21 farmer-focused AI/RAG under the official name
  **Barzegar (برزگر)**.
- Evidence: `docs/subscriptions/phase-25-release-gate.md`.

## Phase 21 — Barzegar Farmer AI/RAG

Official product name: **Barzegar (برزگر)** — Farm-Net agricultural AI
assistant.

### Step 21.1 Real-State Audit + Product/Privacy Boundary

- Verified that no AI runtime, Provider adapter, RAG index, AI tables/routes,
  Mobile/Admin AI feature, or approved knowledge registry exists yet.
- Confirmed Phase 24 provides explicit owner-selected multi-Farm context and
  Phase 25 provides atomic quota for seven typed AI capabilities.
- Classified all 30 `docs/FARMER` PDFs as unapproved candidate sources until
  provenance, licensing, version, extraction, approval, and revocation are
  governed.
- Defined Barzegar as farmer-focused, Provider-neutral, cited,
  privacy/consent-scoped, safety-gated, and integrated with the existing
  Subscription quota boundary.
- Explicitly excluded autonomous prescriptions, silent access to all Farms,
  production Provider enablement, ungoverned web/document ingestion, and
  assumed self-hosted GPU infrastructure.
- Approved the 16-step Phase 21 sequence.
- Next: Step 21.2 AI Core DB, Permissions, Retention + Provider-Neutral
  Contracts.
- Evidence: `docs/ai/phase-21-barzegar-real-state-audit.md`.

### Step 21.2 AI Core DB, Permissions, Retention + Provider-Neutral Contracts

- Added nine additive AI tables for Conversations, selected-Farm consent
  manifests, Requests, Messages, execution Attempts, technical Usage, Feedback,
  idempotent deletion work, and immutable Audit.
- Linked Farm context to real Farm/Plot/Cycle FKs and commercial quota to the
  existing Billing reservation boundary.
- Added explicit lifecycle, idempotency, retention, deletion, Provider replay,
  technical cost, safe Audit, and `RESTRICT` ownership constraints.
- Added nine owner-scoped and two new restricted Admin permissions; the Admin
  role now has eight AI operations in total.
- Added immutable Provider-neutral request/result/usage contracts without an
  SDK, credential, concrete Provider, or network call.
- Migration `a21c4b82a6e0`, six focused and all 322 Backend tests,
  Ruff/compileall, MySQL upgrade/no-drift, seed twice with 281 permissions,
  nine runtime AI tables, and app/database/Redis health passed.
- Next: Step 21.3 Knowledge Source Governance, Ingestion + Persian Extraction.
- Evidence: `docs/ai/phase-21-ai-core-foundation.md`.

### Step 21.3 Knowledge Source Governance, Ingestion + Persian Extraction

- Added five governed tables for source provenance/licensing, versions,
  immutable PDF documents, exact-once ingestion jobs, and page-level extracted
  text.
- Kept source/version human approval independent from extraction success and
  used `RESTRICT` foreign keys for governance history.
- Added checksum-bound Persian extraction with NFKC and Persian character
  normalization, stable failures, quality flags, and encrypted-PDF rejection.
- Added separate review and ingestion permissions for Admin and Content
  Manager; ordinary users receive no knowledge-management permission.
- Audited 30 candidate PDFs/1,245 pages under `docs/FARMER`; one encrypted file
  requires manual review and no candidate was automatically approved.
- Migration `b21d5c93b7f1`, all 329 Backend tests, Ruff/compileall, MySQL
  upgrade/no-drift, seed twice with 283 permissions, five-table inspection,
  rebuilt runtime image with `pypdf`, and app/database/Redis health passed.
- Next: Step 21.4 Retrieval Store, Chunking, Embeddings + Citation Contracts.
- Evidence: `docs/ai/phase-21-knowledge-governance.md`.

### Step 21.4 Retrieval Store, Chunking, Embeddings + Citation Contracts

- Added four normalized MySQL tables for page chunks, embedding model registry,
  external point lifecycle, and immutable response citations.
- Selected pinned Qdrant `v1.18.2` as the external vector store; vector arrays
  are not stored in MySQL JSON.
- Added deterministic Persian page chunking with offsets, overlap, SHA-256,
  model/version contracts, and exact citation quote validation.
- Enforced approved source/version, successful extraction, reviewed page,
  active-point filtering, version filtering, exact-once indexes, and withdrawal
  removal boundaries.
- Added `ai.retrieval.manage` to Admin and Content Manager; ordinary users
  receive no index-management access.
- Real Qdrant collection/upsert/filtered-query/remove/cleanup/health smoke,
  migration/no-drift, and seed twice with 284 permissions passed.
- All 338 Backend tests, Ruff, compileall, app/database/Redis health, and Qdrant
  health passed.
- Next: Step 21.5 Conversation, Request/Run + Idempotent Async Workflow.
- Evidence: `docs/ai/phase-21-retrieval-foundation.md`.

### Step 21.5 Conversation, Request/Run + Idempotent Async Workflow

- Added six typed owner-scoped APIs for conversation create/list/detail,
  request submit/status, and queued cancellation.
- Added canonical request fingerprints; exact replays return the original row
  and changed payload reuse returns a stable conflict.
- Added database queue availability, priority, attempt bounds, worker identity,
  lease expiry, queue indexes, and exact-once input/output message kinds.
- Worker claims use row locks with `SKIP LOCKED`; stale leases close their
  running attempt before bounded retry and terminal exhaustion cannot remain
  stuck in `running`.
- Owner contracts hide idempotency, fingerprint, worker, lease, attempt, and
  Provider internals.
- Provider, selected-Farm context, and Subscription quota execution remain
  explicitly reserved for Steps 21.6, 21.7, and 21.8.
- All 344 Backend tests, Ruff/compileall, MySQL migration/no-drift, runtime
  create/replay/cancel/cleanup, five-path/six-operation OpenAPI inspection, and
  app/database/Redis health passed.
- Next: Step 21.6 Selected Farm Context, Consent, Freshness + Privacy Hardening.
- Evidence: `docs/ai/phase-21-async-workflow.md`.

### Step 21.6 Selected Farm Context, Consent, Freshness + Privacy Hardening

- Added three typed owner APIs for selected-Farm consent create/list/revoke.
- Added consent idempotency, stable selection fingerprint, one-active scope,
  version, bounded expiry, hierarchy, revocation, and lifecycle constraints.
- Revalidated real Farm owner → Plot → Crop Cycle lineage at consent and request
  capture time; inaccessible selections return a non-enumerating not-found.
- Added minimal allowlisted context snapshots and excluded descriptions, notes,
  boundaries, precise coordinates, media, history, and other Farms by default.
- Added freshness hashing and worker-time revalidation; changed or inactive
  context blocks execution and requires a new snapshot.
- All 349 Backend tests, Ruff/compileall, MySQL migration/no-drift, real
  consent/request/revoke/stale-block/cleanup, seven-path/nine-operation OpenAPI
  inspection, and app/database/Redis health passed.
- Next: Step 21.7 Model Gateway, Prompt/Policy Registry + Routing.
- Evidence: `docs/ai/phase-21-selected-farm-context.md`.

### Step 21.7 Model Gateway, Prompt/Policy Registry + Routing

- Implemented Provider-neutral gateway and OpenAI Responses adapter.
- Added 3 versioned model configurations, 6 prompt policies, and 6 active
  feature/request routes with a cost-aware Luna/Terra/Sol hierarchy.
- Pinned prompt and route versions on requests and model configuration/route on
  execution attempts.
- Limited fallback to one alternate model and transient failures only;
  insufficient quota, invalid credentials, invalid input, and missing models do
  not retry.
- Ruff, compileall, all 353 Backend tests, Alembic head `g21c4a18d6e5`,
  registry inspection, and app/database/Redis health passed.
- Live OpenAI Responses reached the Provider but returned
  `429 insufficient_quota`. The owner approved deferring Billing activation
  because an international payment card is unavailable.
- Provider activation remains disabled. Deterministic HTTP mocks cover success,
  parsing, usage, failure classification, and fallback behavior.
- Status: completed. Next: Step 21.8 Subscription Quota, Technical Usage/Cost +
  Reconciliation.
- Evidence: `docs/ai/phase-21-model-gateway-routing.md`.

### Step 21.8 Subscription Quota, Technical Usage/Cost + Reconciliation

- Reused Phase 25 Billing Entitlements and reservations; no parallel
  Subscription or quota tables were added.
- Metered AI requests reserve one unit exactly once before queue insertion;
  boolean AI features require enabled access without fake numeric usage.
- Resolved processing priority from the active Subscription Entitlement.
- Finalized only usable successful answers and released cancellation, stale
  context, terminal failure, and exhausted-attempt reservations.
- Added exact-once Provider/model/token/latency usage and optional versioned
  TOMAN-only cost calculation; no exchange rate is guessed.
- Added read-only reconciliation across request, commercial reservation, and
  technical usage states.
- Fixed optional context JSON to persist SQL `NULL` and added compensation for
  request flush/commit failure discovered by real runtime regression.
- Ruff/compileall, all 357 Backend tests, Alembic head/no-drift, two real MySQL
  quota lifecycle flows, and app/database/Redis health passed.
- Next: Step 21.9 Agricultural Safety, Output Validation + Human Escalation.
- Evidence: `docs/ai/phase-21-subscription-quota-usage.md`.

### Step 21.9 Agricultural Safety, Output Validation + Human Escalation

- Added Persian poisoning/emergency and high-risk chemical triage.
- Emergency guidance is available before Entitlement and consumes no quota.
- High-risk usable output requires citations, uncertainty, and human review.
- Invalid output is blocked, unbilled, and releases reserved quota.
- Added explicit user-triggered escalation to the existing Consultant workflow
  with TOMAN and an auditable request link; no automatic consult purchase.
- Ruff/compileall, 360 Backend tests, migration, and real emergency runtime
  passed.
- Next: Step 21.10 Image Analysis Boundary + Evidence-Gated Diagnosis.
- Evidence: `docs/ai/phase-21-agricultural-safety.md`.

### Step 21.10 Image Analysis Boundary + Evidence-Gated Diagnosis

- Added owner-scoped Media binding for image analysis with exact-once checksum,
  MIME, size, and dimension snapshots.
- Enforced JPEG/PNG/WebP, 10MB maximum, and 256×256 minimum.
- Added provider-neutral in-memory image input and Responses `input_image`.
- Required visible evidence, uncertainty, and human review; no certain
  diagnosis from one image.
- Ruff/compileall, 363 Backend tests, migration/no-drift, and health passed.
- Real owner-image smoke skipped: no qualifying owner image exists locally.
- Next: Step 21.11 Smart Diary Suggestions + Farmer Reports.

### Step 21.11 Smart Diary Suggestions + Farmer Reports

Status: completed

- Added exact-once, owner-scoped `ai_diary_suggestions` and
  `ai_farmer_reports` artifacts at Alembic head `k21g8e5c1029`.
- Smart diary and report requests now require matching selected-Farm consent.
- Smart diary output is a typed pending proposal; it never auto-writes Farm
  data. Explicit owner acceptance creates one real audited Farm operation using
  the active-cycle, date, ownership, and operation-type contracts.
- Owner rejection and repeated terminal decisions are idempotent.
- Farmer reports retain a source snapshot with the selected Farm/Plot/Cycle,
  context freshness hash, and real operation/input/harvest counts.
- Added owner list/accept/reject/report APIs and contract tests.
- Ruff, compileall, 368 backend tests, migration, database and Redis health: OK.
- Live Provider generation remains disabled until OpenAI billing is activated.
- Next: Step 21.12 Mobile Barzegar Assistant.
- Evidence: `docs/ai/phase-21-smart-diary-reports.md`.

### Step 21.12 Mobile Barzegar Assistant

Status: completed

- Added typed Mobile models/API/repository for Barzegar conversations,
  requests, selected-Farm consent, diary suggestions, and farmer reports.
- Covered all six real Backend request kinds and their exact feature codes.
- Added the authenticated `/barzegar` Home entry and a three-section farmer UI:
  chat, smart diary, and reports.
- Added real Farm/Plot/Cycle selection with purpose-matched 24-hour consent.
- Added private JPEG/PNG/WebP Media upload for evidence-gated image analysis.
- Added request status refresh, safety copy, Provider-disabled notice, and
  permission/entitlement/quota/error/empty/loading states.
- Diary proposals require explicit farmer acceptance or rejection.
- Reports render real operation/input/harvest snapshot counts.
- Flutter analyze: OK.
- Flutter tests: 72 passed.
- Flutter Web build and Wasm dry run: OK.
- Generated output was not staged.
- Next: Step 21.13 Admin Barzegar Governance.
- Evidence: `docs/ai/phase-21-mobile-barzegar.md`.

## Progress Update Rule

After every completed step:

1. update this document with the commit and verification evidence;
2. update relevant API, notification, and database docs;
3. add or update the Postman collection;
4. report tracked and untracked Git status separately;
5. do not mark a step done until its required tests and smoke checks pass.

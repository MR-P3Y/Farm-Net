# Farm-Net Project Context

Last verified: 2026-07-19
Repository path: `E:\Farm-Net`
Primary development branch: `develop`

## Product

Farm-Net is an agriculture super-app and marketplace for farmers, agricultural
businesses, operational service providers, consultants, experts, and platform
administrators.

The product is broader than an online store. Its intended domains include:

- identity, profiles, roles, and permissions;
- geographic data and addresses;
- stores, products, carts, orders, payments, and commission;
- media, documents, verification, and notifications;
- agricultural weather and alerts;
- an agricultural social community and expert answers;
- agricultural consultants;
- agricultural operational services;
- later: equipment rental, subscriptions, promotion, reviews, wallet and
  settlement, AI/RAG, analytics, and controlled data access.

The current Services Module is an agricultural operational-services
marketplace. It is not equipment rental. Examples include spraying, ploughing,
pruning, harvesting, product transport, soil testing, irrigation installation,
and agricultural labour.

Do not use the old product name `Keshavarz Man`. The product name is Farm-Net.

## Repository Structure

```text
E:\Farm-Net
|-- backend/       FastAPI, SQLAlchemy, Alembic, MySQL, Redis
|-- mobile/        Flutter mobile application
|-- admin-panel/   Flutter Web administration application
|-- infra/         Docker Compose and infrastructure foundations
|-- docs/          Product, architecture, workflow, and API documentation
|-- postman/       Postman collections
|-- scripts/       Development, migration, seed, and backup placeholders/tools
|-- data/          Seed and reference data
`-- media/         Local media workspace
```

The backend is a modular monolith. It is not currently a microservices system.

## Implemented Foundations

The repository contains foundations for:

- repository governance and documentation;
- FastAPI backend and Flutter application foundations;
- Flutter Web admin foundation;
- authentication, sessions, roles, and permissions;
- profiles, documents, verification, and geo;
- stores and products;
- carts, orders, mock payment, and commission snapshot foundations;
- media storage and controlled file access;
- in-app notifications;
- weather, cache, alerts, a mock provider, and an OpenWeather-ready provider;
- social posts, comments, reactions, bookmarks, reports, and moderation;
- expert answers;
- consultant profiles, requests, workflows, mobile UI, and admin UI.

These are foundations, not a claim that the product is production-ready.
Real payment, SMS, email, push delivery, production deployment, broad automated
tests, and several planned business modules remain incomplete.

## Current Services Status

The following Services work is present on `develop`:

```text
3b8af10  Step 17.1 - Services DB + Permission Foundation
0f3a07d  Step 17.2 - Categories + Provider Profile APIs
c247d9d  Step 17.3 - Service Offer APIs
bda9699  Step 17.10 - Admin Panel Services
```

Database tables already present:

- `service_categories`
- `service_provider_profiles`
- `service_provider_categories`
- `service_offers`
- `service_offer_media`
- `service_requests`
- `service_request_status_logs`

Categories, provider profiles, and offers have backend repository/service/API
and admin moderation support. Service Request tables, permissions, schemas,
repository operations, workflow services, requester/provider/admin routes,
status logs, role-specific privacy contracts, exact-once in-app notifications,
API docs, Postman coverage, focused backend tests, mobile service discovery and
detail UI, requester request flow, and provider profile/offer management are
implemented, including the mobile provider request workbench and the typed
four-tab Services admin panel. The canonical Postman collection now covers the
complete public, owner, moderation, and request workflow contracts.

The Services sequence through Step 17.11 is complete. The next product step
must be selected from the roadmap and explicitly authorized:

```text
Next roadmap step: not selected
```

Phase 9 completion resumed after the Services release. Steps 9.1 (read-only
audit) and 9.2 (financial contracts and database hardening) are complete.
Seven additive financial tables now provide the foundation for atomic checkout,
inventory reservation, idempotent payment attempts, transactions, and refunds.
Current API and client behavior remains on the existing Mock payment flow until
Step 9.3 and later explicitly connect these contracts.

Step 9.3 now connects Checkout and the Mock lifecycle to these contracts with
row-level locks, atomic stock decrement, reservations, invoice/snapshot
creation, transaction recording, and cancellation release. Checkout request
Step 9.4 adds persistent Checkout replay protection, request fingerprint
conflict detection, exact-once reservation expiry release, and role-specific
Buyer/Seller/Admin response privacy. Mobile now supplies the required Checkout
idempotency key. A real payment gateway remains deferred to a later step.

Step 9.5 adds provider-neutral payment initiation and verification API
contracts, currently backed only by the deterministic Mock provider. Initiation
is idempotent and verification is exact-once across payment attempt, invoice,
legacy payment, order, transaction, reservation, history, and notifications.
No real gateway secret, callback, or external money movement is implemented.

Step 9.6 activates the existing refund contract for Admin: idempotent full-refund
requests and exact-once Mock completion. Partial refunds and real provider money
movement remain deferred so financial state is not overstated.

Step 9.7 adds typed paginated Admin finance read APIs and the first persistent
`admin_audit_logs` contract. Refund request/completion audit actor, target,
old/new state, request metadata, and trace ID atomically with the finance change.

Step 9.8 exposes those contracts in the Admin Panel through five typed,
paginated finance tabs behind `finance.invoices.read`, with loading, empty,
error/retry states and sidebar navigation.

Step 9.9 migrates Mobile payment UX from the legacy Mock Pay action to the
idempotent initiate/verify contracts. Buyer order detail exposes only its safe
invoice identifier and no longer renders platform commission or seller amount.

Step 9.10 completes Phase 9 documentation/Postman and release regression: 29
OpenAPI paths, 34 collection requests, Backend 28 tests, Mobile 26 tests, Admin
5 tests, both Web builds, migration/seed, and DB/Redis health all pass.

Phase 9 completion passed its release gate and is released as
`v0.18.0-orders-finance-foundation`.

Phase 11 Notifications is active. Step 11.1 completed the real-state audit:
the in-app inbox, ownership APIs, producer integration, and Mobile/Admin
foundations exist; external provider delivery, durable retries, preferences,
and device tokens do not. Step 11.2 is the next authorized implementation
boundary and must begin with database exact-once and deterministic event
contracts. See `docs/notifications/phase-11-real-state-audit.md`.

Step 11.2 completed database and provider-neutral delivery hardening at Alembic
head `e72b9f4c31a6`: exact-once notification identity, deterministic source
event keys, explicit self-notification policy, and durable retry/lease fields.
No external delivery worker or provider was added. Step 11.3 is next.

Step 11.3 completed user preferences and verified-destination routing at
Alembic head `f84c2a1d9037`. In-app remains default; opted-in Email/SMS create
pending delivery work, while Push/Telegram await destination foundations.
Step 11.4 retry queue and delivery operations is next.

Step 11.4 completed the provider-neutral retry queue at Alembic head
`a16d7c4e52b9`: atomic claim/lease, monotonic attempts, backoff, terminal
failure, expired-worker recovery, and Admin delivery observability/requeue.
Step 11.5 Email Provider Foundation is next; no real provider is connected yet.

Step 11.5 completed a fail-closed SMTP Email foundation with safe envelope
rendering, verified destination checks, queue integration, provider result
recording, and a one-batch CLI worker. It was verified without credentials or
network delivery. Step 11.6 SMS Provider Foundation is next.

Step 11.6 completed a fail-closed, provider-neutral HTTPS JSON SMS foundation
with verified destinations, safe bounded messages, queue result recording, and
a one-batch CLI worker. No vendor credential or live SMS was used. Step 11.7
Push Notification Foundation is next.

Step 11.7 completed device ownership, active-device routing, and a fail-closed
provider-neutral Push batch dispatcher at Alembic head `b27e8d5f64c1`. No live
Push credential/message was used. Step 11.8 Mobile Notification Center
Hardening is next.

Step 11.8 completed Mobile Notification Center hardening: typed preferences and
device contracts, channel settings UI, resilient updates, and expanded action
routing. Real vendor token acquisition remains explicitly blocked on SDK/vendor
credentials. Step 11.9 Admin Notification Operations is next.

Step 11.9 completed typed Admin delivery operations: queue filtering and
pagination, detail/error inspection, attempt timeline, permission guarding, and
controlled retry matching Backend eligibility rules. Step 11.10 consolidated
Docs/Postman + Runtime Regression is next.

Step 11.10 completed consolidated documentation, 14-path/20-request Postman
coverage, and full Backend/Mobile/Admin runtime regression. Phase 11
implementation through documentation is complete; the release gate/tag is the
next explicit step. Live external delivery remains configuration/vendor work.

Step 11.11 passed the independent release gate. Phase 11 is released as
`v0.19.0-notifications-delivery-foundation`; live provider enablement and Mobile
vendor Push SDK/token acquisition remain explicit deployment/future work.

Phase 12 Category Management is active. Step 12.1 adds safe Product Category
management on the existing domain model: public discovery, protected Admin
create/update/list contracts, hierarchy validation, usage counters, and typed
Admin UI. Other category domains remain independent by design.

Step 12.2 completed the cross-domain governance audit. Services needs hierarchy,
seed, and usage hardening; Social lacks Admin category management; Consultants
needs usage counts and Admin search wiring. Domain tables remain independent.
Step 12.3 Services Category Contract Hardening is next.

Step 12.3 hardened Services categories with cycle prevention, parent clearing,
non-destructive idempotent seed behavior, domain usage counters, and matching
Admin UI. Step 12.4 Social Category Management is next.

Step 12.4 completed Social Category Management with category-specific
permissions, Admin APIs/UI, post usage counts, and non-destructive seed behavior.
Step 12.5 Consultant Specialty Usage + Admin Search Hardening is next.

Step 12.5 added Consultant specialty profile/request usage counts and wired
Backend search into Admin UI. Runtime has no specialty reference rows and no
unapproved defaults were invented. Step 12.6 Unified Admin Taxonomy Navigation
+ UX Consistency is next.

Step 12.6 added a permission-aware Admin taxonomy hub and unified navigation
across Product, Services, Consultant, and Social management while preserving
their independent contracts.

Step 12.7 completed consolidated Category Management documentation, validated
the four canonical domain Postman collections, and passed full Backend/Mobile/
Admin runtime regression. Runtime reference rows are Product 24, Services 8,
Social 6, and Consultant 0; Consultant defaults remain intentionally absent
until an authoritative specialty taxonomy is approved. Step 12.8 Category
Management Release Gate passed independently. Phase 12 is released as
`v0.20.0-category-management-foundation`; the Consultant default taxonomy
remains an explicit future business-data decision.

Phase 16 Equipment Rental is active. Step 16.1 confirmed that no Rental module
exists beyond the `lessor` role, four moderation permission placeholders,
equipment store/product classifications, and equipment-ownership verification.
Rental will be an independent domain with lessor profiles, moderated equipment,
availability/pricing, date-bound bookings, status logs, notifications, Mobile,
and Admin surfaces. Existing order-only finance contracts are not silently
reused.

Step 16.2 added eight independent Rental tables at Alembic head
`104ae669cc1a`, explicit lifecycle/pricing/operator enums, range/amount and
exact-once log constraints, and 24 requester/lessor/Admin permissions. A known
four-index Alembic baseline drift in pre-existing Consultant/Services tables
was not mixed into the Rental migration. Step 16.3 Categories + Lessor Profile
APIs is next.

Step 16.3 added governed Rental categories, an idempotent eight-row equipment
taxonomy, owner lessor profile create/edit/submit, and Admin moderation. Lessor
approval requires an approved role Verification Request. Step 16.4 Equipment
Listing + Media APIs is next.

Step 16.4 added public and owner equipment listings, real Media ownership and
visibility validation, operator/delivery/location contracts, submission, and
status-specific Admin moderation. Public responses exclude exact address and
moderation data.

Step 16.5 added atomic multi-unit pricing, operator compatibility, owner
availability blocks, public range checks, overlap prevention against blocks and
accepted/in-progress bookings, and pricing/media approval readiness. Step 16.6
Rental Request/Booking Workflow is next.

Step 16.6 added requester, assigned-lessor, and Admin booking workflows with
row-lock acceptance, overlap revalidation, immutable commercial snapshots,
controlled cancellation/transitions, role privacy, and deterministic status
logs. No payment movement is claimed. Step 16.7 Notifications +
Privacy/Concurrency Hardening is next.

Step 16.7 added exact-once Rental request notifications for creation and every
terminal/workflow transition, with recipient deduplication and self-notification
prevention. Pricing and availability writes now share the equipment row lock
used by acceptance, while acceptance revalidates minimum units and operator
compatibility. Step 16.8 Mobile Equipment Discovery + Detail is next.

Step 16.8 added typed Mobile Rental discovery/detail, category/geo/operator
filters, search, media gallery, active pricing display, lessor summary, shared
loading/empty/error states, and Home navigation. Backend price-range filtering
does not exist and was not simulated client-side. Step 16.9 Mobile Rental
Request Flow is next.

Step 16.9 added Mobile availability preflight, pricing/date/unit selection,
typed request creation, requester list/detail, exact status timeline rendering,
commercial snapshots, and status-bound cancellation with a required reason.
Step 16.10 Mobile Lessor Management + Request Workbench is next.

Step 16.10 added Mobile lessor profile lifecycle, owner equipment/media editing
and submission, atomic pricing and availability management, assigned request
list/detail/timeline, and the exact lessor accept/reject/start/complete actions.
Step 16.11 Admin Panel Equipment Rental is next.

Step 16.11 added the typed Admin Rental panel with governed category hierarchy,
lessor and equipment moderation, paginated request operations, Admin-only detail
and exact status logs, controlled request transitions, permission guarding, and
loading/empty/error handling. Step 16.12 Docs/Postman + Runtime Regression is
next.

Step 16.12 consolidated the complete Rental API/client documentation and proved
the release candidate through full Backend, Runtime, Mobile, Admin, and Postman
regression. Runtime exposes 29 Rental paths backed by 8 tables and 24 Rental
permissions; the 35-request Postman collection covers every path exactly. Step
16.13 Equipment Rental Release Gate + Tag is next.

Step 16.13 passed the final Equipment Rental release gate across Backend,
Runtime, Mobile, Admin, Postman, and Git safety checks. Phase 16 is complete and
released as `v0.21.0-equipment-rental-foundation`. This foundation deliberately
does not claim payment, invoice, commission, settlement, refund, deposit
capture/release, damage, or penalty processing.

Phase 20 Step 20.1 audited the real financial state. Phase 9 contains a strong
order-specific Mock payment/invoice/commission/refund foundation, but the
project has no wallet, double-entry ledger, balance release, settlement/payout,
real gateway, or cross-domain finance integration. The audit preserves Phase 9
contracts, identifies the `TOMAN`/Consultation `IRR` mismatch as blocking, and
defines Step 20.2 Canonical Money + Billable Source Contracts as next.

Phase 20 Step 20.2 established Iranian toman as the only commercial currency:
`TOMAN` in API/database and `تومان` in Persian UI, with the explicit legacy
conversion `10 IRR = 1 TOMAN`. Typed billable-source/event contracts now cover
orders, services, rentals, and consultations while preserving Phase 9 APIs.
Service/consultation budgets remain non-billable and rental deposits remain
separate from revenue. Step 20.3 Wallet Accounts + Double-Entry Ledger is next.

Phase 20 Step 20.3 added the `TOMAN`-only Wallet Account and immutable
double-entry Ledger database/permission foundation at Alembic head
`c7e8a1f20303`. It stores no mutable balance and posts no money yet. Database
constraints protect positive/equal journal totals, idempotency, source identity,
reversal uniqueness, and accounting history. Step 20.4 Order Finance Ledger
Bridge + Reconciliation is next.

Phase 20 Step 20.4 atomically bridges successful product-order payments and
refunds into exact-once balanced journals linked directly to the existing
financial transaction. A permission-protected, read-only reconciliation API
reports missing or unbalanced bridges. Provider funds remain pending; no
balance release or settlement occurs. Step 20.5 Universal Invoice + Commission
Foundation is next.

## Known Gaps

- Services has focused backend and client model/widget coverage; broad
  end-to-end browser/device automation is still required.
- Real payment gateway integration is not implemented.
- SMS, email, and push providers are not connected for production delivery.
- Contracts, subscriptions, promotion, equipment rental, reviews, wallet,
  settlement, AI/RAG, BI/data access, and production hardening remain future work.

## Development Environment

The Windows development environment was recovered and stabilized after the
Windows reinstall. This recovery is considered completed as confirmed by the
project owner on 2026-07-15. Tool versions and executable health should still be
reported in verification output whenever a new machine or shell is used.

The authoritative repository is `E:\Farm-Net`. A similarly named workspace on
drive C must not be treated as the product repository.

## Engineering Rules

Use the established module pipeline:

1. models and migration;
2. permission seed;
3. schemas, repository, and service;
4. public/user APIs;
5. admin APIs;
6. notifications where required;
7. mobile UI;
8. admin-panel UI;
9. API docs and Postman;
10. compile, analyze, tests, health, and smoke verification;
11. clean step-based commit and release tag when the phase is complete.

Additional rules:

- Keep commits step-based and focused.
- Never stage or commit unrelated or generated files.
- Never commit `.env`, credentials, local uploads, caches, build outputs, or DB
  dumps.
- If `backend/app/common.zip` exists, do not stage or commit it.
- Preserve user changes and unrelated untracked files.
- Do not reset, clean, delete volumes, or rewrite history without explicit
  authorization.
- Treat documentation, permission checks, status transitions, privacy, tests,
  and notification behavior as part of feature completion.

## Release Reference

The latest completed tagged foundation is:

```text
v0.21.0-equipment-rental-foundation
```

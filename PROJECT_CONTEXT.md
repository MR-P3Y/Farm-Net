# Farm-Net Project Context

Last verified: 2026-07-24
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

Phase 18 Step 18.10 bounds Unified Search to 120 grouped items and a dedicated
default 30 requests/60 seconds/client inside the global limiter. Rate-limit key
memory is capped, untrusted `X-Forwarded-For` is ignored, trusted proxies require
an explicit allow-list, and 429 responses include `Retry-After`. Search responses
are `no-store`/`noindex`; query history, analytics, and explicit query logging
remain absent. Existing domain indexes are sufficient for current sparse data;
FULLTEXT/external search remains evidence-driven. Step 18.11 Docs/Postman +
Runtime Search Regression is next.

Phase 18 Step 18.11 consolidates the final Search API/operations documentation,
expands Unified Search Postman from 3 to 12 positive/negative requests, and adds
a reusable read-only Runtime regression script. Backend/Mobile/Admin full gates,
Alembic head, two idempotent auth seeds, health, OpenAPI, six-provider execution,
privacy headers, and validation failures passed. Runtime currently has zero
matching public rows in all six domains, so populated-result behavior is covered
by typed tests rather than falsely claimed as real-row evidence. Step 18.12
Search/Filters/Discovery Release Gate + Tag is next.

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

Phase 20 Step 20.5 added the `TOMAN`-only universal Invoice, Item, Commission
Policy, and immutable Commission Snapshot foundation at Alembic head
`f7a6d4b20606`. Product Checkout is atomically mirrored while all Phase 9 APIs
remain compatible. Service/Consultation budgets cannot invoice, and Rental is
deferred for revenue/deposit separation. Step 20.6 Services/Consultation
Final-Price Contracts is next.

Phase 20 Step 20.6 added versioned, ownership-protected final-price agreements
for Services and Consultations at Alembic head `b9c8d6e40808`. Budgets remain
non-billable; requester acceptance alone creates the exact-once universal
Invoice and immutable commission snapshot. Work cannot start without accepted
price. Acceptance fails closed until an active default policy for that exact
domain is configured. Step 20.7 Rental Revenue + Deposit Contracts is next.

Phase 20 Step 20.7 adds immutable accepted Rental financial terms at Alembic
head `ecba19a70b11`. Rental revenue and refundable deposit principal remain
separate and sum exactly to the future funding total. The terms are explicitly
unfunded: no Invoice, payment capture, deposit custody/release, commission,
damage, penalty, refund, or ledger posting is claimed. Step 20.8 Balance Release
+ Settlement/Payout Workflow is next.

Phase 20 Step 20.8 releases paid Product Order provider revenue from pending to
available exactly once at delivery and adds Ledger-derived own balances plus an
idempotent Settlement reserve/approve/reject/simulated-clearing workflow at
Alembic head `fdcb2ab80c12`. Simulated payout is not an external bank transfer.
Unfunded domains cannot release revenue. Step 20.9 Refund, Reversal, Adjustment
+ Concurrency Hardening is next.

Phase 20 Step 20.9 makes Product Order Refund safe after provider balance
Release. A released amount is restored to pending through a linked immutable
Reversal before the Refund journal; row locks serialize it against Settlement.
Refund fails closed when funds are reserved or already in simulated clearing,
so no provider wallet can become negative. Controlled `TOMAN` provider wallet
Adjustments are balanced, idempotent, reason-required, permission-guarded and
audited. Step 20.10 is next.

Phase 20 Step 20.10 adds a disabled-by-default Zarinpal v4 adapter for Product
Order payment attempts. It sends canonical `TOMAN` as provider currency `IRT`,
stores Authority, redirects only to the fixed production/sandbox Zarinpal host,
and treats Callback `OK` solely as a signal for server-to-server Verify. Codes
100 and exact-once 101 are accepted. Merchant ID remains environment-only and
is never returned or persisted. No credential exists in the repository, so no
real or sandbox money movement has been claimed. Step 20.11 is next.

Phase 20 Step 20.11 adds owner-only lifecycle notifications for Refund,
Settlement and Wallet Adjustment. A central privacy guard rejects sensitive
keys in Payment/Finance notification payloads. Settlement decisions and
simulated clearing gain exact-once Admin Audit records; Refund audit no longer
copies provider references. Step 20.12 Mobile Wallet, Invoices, and Provider
Settlements is next.

Phase 20 Step 20.12 adds a Mobile «My Finance Center» with Ledger-derived
pending/available/reserved wallet balances, provider Settlement request/history,
and payer-owned invoices in canonical Iranian toman. Two new payer-owned invoice
APIs exclude platform/provider economics. Buyer-only roles retain invoice access
when provider wallet permissions are absent. Step 20.13 Admin Accounting,
Settlement, and Reconciliation is next.

Phase 20 Step 20.13 extends the typed Admin Finance panel with paginated Ledger
Journals, Wallet Accounts, Settlement decisions/simulated clearing, and a live
Reconciliation health summary. New Admin read APIs use existing dedicated
Finance permissions. No raw JSON or real bank payout is introduced. Step 20.14
Docs/Postman + Runtime Financial Regression is next.

Phase 20 Step 20.14 consolidated the financial API/Postman contract and ran the
full release regression. Backend lint/compile/tests, migration/seed, runtime
health, reconciliation and OpenAPI passed; Mobile and Admin analyze/tests/Web
builds passed. The runtime contained no successful Payment or Refund rows, so
reconciliation is clean but zero-data. Credentialed Zarinpal sandbox and real
bank payout remain explicitly unverified. Step 20.15 Release Gate + Tag is next.

Phase 20 Step 20.15 passed its independent release gate. The Wallet,
Settlement, and Accounting foundation is released as
`v0.22.0-wallet-settlement-accounting-foundation`. This release does not claim
credentialed Zarinpal operation, production payment, or real bank payout.

Phase 18 Search/Filters/Discovery is now active. Step 18.1 audited the real
public discovery surfaces. Products, Services, Rentals, Consultants, and Social
already expose independent substring search and selected filters, and their
Mobile screens provide uneven subsets. There is no unified search contract,
Persian normalization, relevance model, explicit client-selectable sorting,
cross-domain result endpoint, or shared discovery screen. Step 18.2 Shared
Search Contracts + Persian Query Normalization is next.

Phase 18 Step 18.2 added the central `UnifiedSearchEngine`, provider protocol,
typed query/filter/group/result contracts, `TOMAN`-only shared price range, safe
internal result routes, and deterministic Persian/Arabic text and digit
normalization. No public route or existing domain behavior changes in this
foundation step. Step 18.3 Product Discovery Hardening is next.

Phase 18 Step 18.3 connects Product and Store providers to the central engine.
Their public search now uses the shared Persian normalizer and deterministic
relevance boundary. Products add descendant-aware categories, canonical
`TOMAN` price range, and allow-listed relevance/newest/price sorting; Stores add
relevance/newest sorting. Existing visibility and default ordering remain
compatible. Step 18.4 Services Discovery Hardening is next.

Phase 18 Step 18.4 connects approved Service Offers to the central engine with
shared Persian normalization, provider/category/geo matching, active descendant
categories, `TOMAN` price range, and allow-listed relevance/newest/price/rating
sorting. Negotiable offers never receive invented prices. Existing public
privacy and default ordering remain compatible. Step 18.5 Equipment Rental
Discovery Hardening is next.

Phase 18 Step 18.5 connects approved Rental Equipment to the central engine.
Public discovery now shares Persian normalization across equipment, lessor,
category, and equipment metadata; supports active descendant categories,
canonical `TOMAN` price range, availability intervals, and allow-listed sorts.
Availability excludes explicit blocks plus accepted/in-progress request overlap.
Existing public privacy and default ordering remain compatible. Step 18.6
Consultant Discovery Hardening is next.

Phase 18 Step 18.6 connects approved Consultant profiles to the central engine.
Public discovery now shares Persian normalization across profile identity, bio,
geo names, and active specialties; supports specialty/geo filters and
allow-listed relevance/newest/rating sorting. Public search results preserve the
existing privacy contract and never expose contact or moderation fields. Step
18.7 Social Discovery Hardening is next.

Phase 18 Step 18.7 connects published public Social posts to the central engine.
Public discovery now shares Persian normalization across title, body, geo names,
and category metadata; supports category/type/geo filters and allow-listed
relevance/newest sorting. Members-only, hidden, rejected, deleted, and draft
content cannot enter results. Step 18.8 Unified Cross-Domain Search API is next.

Phase 18 Step 18.8 exposes the public read-only `POST /api/v1/search` endpoint.
One typed request selects any ordered subset of all six providers and returns
independently paginated groups plus a summed total. Persian normalization,
strict `TOMAN`, filter validation, safe internal routes, and each provider's
privacy boundary are retained. Rankings are not globally merged across unlike
domains, and no query history or analytics is stored. Step 18.9 Mobile Unified
Discovery Hub is next.

Phase 18 Step 18.9 adds the Mobile `/search` Unified Discovery Hub and a primary
Home entry. One typed API/Repository/Controller flow queries any non-empty
selection of the six domains, renders grouped totals and typed cards, supports
the shared safe sorts, displays canonical `TOMAN` prices, and navigates only via
Backend-provided internal routes. Initial/loading/empty/error/retry states and
safe model parsing are covered. Step 18.10 Performance, Privacy, and Abuse
Hardening is next.

Phase 18 Steps 18.10 and 18.11 completed performance/privacy/abuse hardening
and consolidated documentation, Postman, and Runtime regression. Step 18.12
then passed the independent Backend, Mobile, Admin, Runtime, Postman, database,
seed, and Git release gates. Phase 18 is complete and released as
`v0.23.0-search-discovery-foundation`. Runtime contains no matching public rows,
so real populated-result ranking remains test-backed rather than claimed as
live-data evidence.

Phase 23 Role-Based My Activity Center is active. Step 23.1 audited the real
Mobile identity and navigation state: common and four business-role surfaces
exist but are exposed through a flat, non-role-aware Home page. The center will
derive a typed multi-role action catalog from real roles/permissions and retain
Backend authorization as final authority. Backend Seller Order operations exist
but their Mobile workbench is the one confirmed functional gap. Step 23.2 Typed
Role/Permission Activity Catalog is next.

Phase 23 Step 23.2 adds one typed Mobile activity catalog driven by real roles
and permissions. It composes common and four independent business-role sections,
distinguishes setup access from approved operational workbenches, and supports
multi-role users without a role switch. The Seller Orders destination remains
unexposed until its Mobile workbench is implemented. Step 23.3 Activity Center
Shell + Common Personal Activity is next.

Phase 23 Step 23.3 adds the authenticated responsive `/activity` Mobile shell
and Home entry. It renders permission-backed common Profile, Verification,
Notification, Finance, Buyer Order, and requester activities from the typed
catalog, with loading and unauthenticated deep-link states. Business-role
sections remain hidden until their integrations are complete. Step 23.4 Shop
Owner Center + Seller Order Workbench is next.

Phase 23 Step 23.4 completes the Shop Owner section and the previously missing
Mobile Seller Order workbench over the existing owner-scoped Backend APIs.
Seller list/detail/pagination/privacy and the exact paid-to-delivered transition
chain are typed and tested; Store, Products, and Seller Orders are permission-
backed Activity Center destinations. Step 23.5 Service Provider Activity
Integration is next.

Phase 23 Step 23.5 connects the existing Service Provider Profile, Offers, and
assigned-request Workbench through the shared role-section renderer. Setup and
approved operations remain permission-distinct, existing moderation/403 states
remain authoritative in their destination screens, and no Services API behavior
changed. Step 23.6 Lessor Activity Integration is next.

Phase 23 Step 23.6 connects the existing Lessor Profile, Equipment/commercial
management, and assigned Rental Request Workbench through the shared role
renderer. Exact profile/equipment/assigned permissions remain authoritative;
pricing, availability, and status stay in their real owner screens. Step 23.7
Consultant Activity Integration is next.

Phase 23 Step 23.7 connects the existing Consultant Profile/specialties and
assigned Consultation Request Workbench through the shared role renderer.
Requester requests remain personal activity, while professional work requires
the exact assigned-management permission. Step 23.8 Role Setup/Verification +
Multi-Role Hardening is next.

Phase 23 Step 23.8 adds a typed four-business-role journey, canonical setup and
Verification destinations, and authenticated identity refresh after approval.
Multi-role rendering is ordered, duplicate-safe, non-switching, and excludes
Admin/support/data roles from the professional count. Step 23.9 Home Navigation
Simplification + Deep-Link/Auth Hardening is next.

Phase 23 Step 23.9 simplifies Home to discovery plus one Activity Center entry
and adds a shared session-recovery guard around Home and private center routes.
Direct links no longer build private children before auth resolution; Backend
permissions remain the final authority. Step 23.10 Docs, Tests, and Runtime
Regression is next.

Phase 23 Step 23.10 consolidates the Activity Center contracts and adds a
reusable read-only Runtime regression. Backend 164 tests, Mobile 52 tests,
Admin 17 tests, both Flutter Web/Wasm builds, 254-path OpenAPI, health,
idempotent 12-role/249-permission seed, nine private 401 checks, and all 13
Postman collections / 313 requests passed. No Runtime mutation was performed.
Step 23.11 Release Gate + Tag is next.

Phase 23 Step 23.11 passed the independent release gate across Backend,
Runtime, Mobile, Admin, Postman, and Git safety. Role-Based My Activity Center
is released as `v0.24.0-activity-center-foundation`. Authenticated fixtures for
live mutation across every professional role remain an explicit E2E boundary.

Phase 19 Reviews / Ratings / Reports is now active. Step 19.1 confirmed there
is no marketplace Review engine. Existing Social reports and Verification
review logs remain separate. Delivered Orders and completed Service, Rental,
and Consultation Requests are the only authoritative eligibility sources; the
real Buyer/Requester is the only reviewer. Step 19.2 Shared Review DB +
Permission Foundation is next. See
`docs/reviews/phase-19-real-state-audit.md`.

Phase 19 Step 19.2 adds four inactive shared Review/aggregate/report/moderation
tables at Alembic head `a7c9e1f30d13` and eight dedicated permissions. MySQL,
idempotent 12-role/257-permission seed, health, and all 168 Backend tests pass.
No API or rating mutation is active. Step 19.3 Eligibility, Ownership,
Lifecycle + Review CRUD is next.

Phase 19 Step 19.3 activates owner Review CRUD with server-authoritative,
row-locked eligibility across the four completed source domains and seven
subjects. Self-review, cross-owner access, unrelated targets, duplicates, and
invalid lifecycle changes are rejected. Backend 180 tests, 257-path OpenAPI,
health, privacy 401, docs, and five Postman requests pass. Runtime has no
terminal source fixture and no fake Review was inserted. Step 19.4 Public
Reviews, Aggregates + Discovery Integration is next.

Phase 19 Step 19.4 activates public active-only Review lists and the canonical
shared rating aggregate. Review create/update/delete adjusts aggregate
sum/count/average atomically; legacy Service Provider and Consultant rating
fields are synchronized projections. Product, Store, Service Offer, Rental
Equipment, and Lessor public contracts now expose canonical rating data.
Ruff/compileall, all 181 Backend tests, runtime health, 258-path OpenAPI, and
14 Postman collections / 319 requests pass. Step 19.5 Review Reports + User
Safety is next.

Phase 19 Step 19.5 adds Review reporting and Backend Admin moderation. Self and
duplicate reports are rejected; reporter responses stay private. Admin hide,
restore, delete, and report resolution are permission-separated, audited, and
atomically reflected in canonical ratings. All 185 Backend tests pass. Step
19.5 runtime health, 264-path OpenAPI, Admin 401 boundaries, and 14 Postman
collections / 325 requests pass. Step 19.6 Notifications, Privacy, Exact-Once
+ Concurrency Hardening is next.

Phase 19 Step 19.6 integrates seven Review/report events into the shared
Notification engine with permission-based Admin recipients, stable exact-once
keys, self-notification suppression, and privacy-minimized payloads. Concurrent
first-Aggregate creation now recovers the unique winner under a locking read.
All 186 Backend tests, runtime health, permission-recipient lookup,
rolled-back event smoke, 264-path OpenAPI, and 14 Postman collections / 325
requests pass. Step 19.7 Mobile Review Creation, History + Public Rendering is
next.

Phase 19 Step 19.7 adds the shared Mobile Review API/models, protected creation
flow, My Activity history with edit/delete, and reusable public rendering on
Product, Store, Service Offer, Rental Equipment, and Consultant detail pages.
Delivered/completed source screens expose server-authoritative creation entry
points. Flutter analyze, all 54 tests, and Web build pass. Step 19.8 Admin
Review/Report Moderation Panel is next.

Phase 19 Step 19.8 adds the permission-guarded typed Admin Review/report
moderation panel with filters, pagination, required notes, lifecycle-aware
actions, and immutable audit timeline rendering. Admin Flutter analyze, all 20
tests, Web build, runtime health, and five Admin Review OpenAPI route groups
pass. Step 19.9 Cross-Domain Contract and Runtime Hardening is next.

Phase 19 Step 19.9 hardens cross-domain contracts by publishing explicit typed
OpenAPI responses for all five Admin Review route groups and sourcing Product,
Store, and Rental Equipment unified-search ratings from the canonical Review
aggregate. Ruff/compileall, all 186 Backend tests, all 54 Mobile tests, all 20
Admin tests, both Web builds, runtime app/database/Redis health, 264-path
OpenAPI, and 14 Postman collections / 325 requests pass. Step 19.10
Documentation, Postman + Runtime Regression is next.

Phase 19 Step 19.10 completes Review documentation and Postman metadata and
adds a reusable read-only Runtime regression for all ten Review path groups,
typed schemas, privacy, access boundaries, and missing-subject behavior. Ruff/
compileall, all 186 Backend tests, all 54 Mobile tests, all 20 Admin tests, both
Web builds, two stable 12-role/257-permission seeds, runtime health, 264-path
OpenAPI, and 14 Postman collections / 325 requests pass with zero Runtime
mutations. Step 19.11 Release Gate + Tag is next.

Phase 19 Step 19.11 passed the independent release gate across Backend,
database/seed, Runtime/OpenAPI, Review regression, Mobile, Admin, Postman, and
Git. Phase 19 Reviews / Ratings / Reports is complete and released as
`v0.25.0-reviews-foundation`.

Phase 21 AI/RAG is intentionally deferred by owner decision. Phase 22
Production Hardening is active. Step 22.1 audited the real release baseline and
confirmed healthy development Runtime/tests alongside production blockers:
no CI/CD or production topology, placeholder Nginx/backup, `main` 122 commits
behind `develop`, four Alembic index drifts, mostly untyped OpenAPI responses,
auth/session hardening gaps, disabled external providers, and no production
observability/E2E/recovery evidence. The approved sequence is 22.2 through
22.13; Release/Branch/Version + Documentation Governance is next.

## Known Gaps

- Services has focused backend and client model/widget coverage; broad
  end-to-end browser/device automation is still required.
- The Zarinpal adapter is implemented but disabled; credentialed sandbox and
  production activation remain operational gaps.
- SMS, email, and push providers are not connected for production delivery.
- Contracts, subscriptions, promotion, real payout integration,
  AI/RAG, BI/data access, and production hardening remain future work.

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
v0.25.0-reviews-foundation
```

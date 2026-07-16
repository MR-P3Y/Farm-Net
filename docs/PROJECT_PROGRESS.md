# Farm-Net Project Progress

Last verified: 2026-07-16
Branch at verification: `develop`
Verified HEAD: `c247d9d`

## Current Position

The Windows development environment recovery is complete. Product development
should resume at `Step 17.10 - Admin Panel Services`.

Do not restart Step 17.1, 17.2, or 17.3. Their implementations are already in
the repository.

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
| 17.10 Admin Panel Services | Next | Not started |
| 17.11 Docs/Postman + Runtime Regression | Planned | Not started |
| Services mobile UI | In progress | Discovery, requester flow, provider profile and offers done |
| Services admin UI | Not started | No `admin-panel/lib/features/services` |
| Services API docs/Postman | Done for request backend | `docs/api/services.md`, Services collection |
| Services automated tests | Started | 13 focused Request workflow/contract tests |
| Services release/tag | Not started | No Services tag after v0.14.0 |

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

## Progress Update Rule

After every completed step:

1. update this document with the commit and verification evidence;
2. update relevant API, notification, and database docs;
3. add or update the Postman collection;
4. report tracked and untracked Git status separately;
5. do not mark a step done until its required tests and smoke checks pass.

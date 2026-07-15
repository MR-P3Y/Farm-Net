# Farm-Net Project Progress

Last verified: 2026-07-15
Branch at verification: `develop`
Verified HEAD: `c247d9d`

## Current Position

The Windows development environment recovery is complete. Product development
should resume at `Step 17.5 - Services Request Notifications + Contract Hardening`.

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
| 17.5 Request Notifications + Contract Hardening | Next | Deferred explicitly from 17.4 |
| 17.6 Mobile Service Discovery + Detail | Planned | Not started |
| 17.7 Mobile Service Request Flow | Planned | Not started |
| 17.8 Provider Profile + Offer Management Mobile | Planned | Not started |
| 17.9 Provider Request Workbench | Planned | Not started |
| 17.10 Admin Panel Services | Planned | Not started |
| 17.11 Docs/Postman + Runtime Regression | Planned | Not started |
| Services mobile UI | Not started | No `mobile/lib/features/services` |
| Services admin UI | Not started | No `admin-panel/lib/features/services` |
| Services API docs/Postman | Not started | No Services API doc or collection |
| Services automated tests | Started | Focused Request workflow tests added |
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

# Farm-Net Project Context

Last verified: 2026-07-16
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
v0.17.0-services-foundation
```

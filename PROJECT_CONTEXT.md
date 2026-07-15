# Farm-Net Project Context

Last verified: 2026-07-15
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
status logs, privacy boundaries, and focused backend tests are implemented.
Notifications, UI, API docs, and Postman coverage remain for later steps.

The next product implementation step is:

```text
Step 17.5 - Services Request Notifications + Contract Hardening
```

## Known Gaps

- Services mobile feature does not exist.
- Services admin-panel feature does not exist.
- `docs/api/services.md` does not exist.
- A Services Postman collection does not exist.
- Services Request has focused tests; broader Services regression is still required.
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
v0.14.0-expert-consultants-foundation
```

Services commits currently follow that tag and have not yet been released as a
Services foundation tag.

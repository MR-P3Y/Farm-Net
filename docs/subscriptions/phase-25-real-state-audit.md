# Phase 25.1 — Unified Subscription & Entitlement Real-State Audit

Date: 2026-07-26

Status: completed as a read-only architecture audit.

## Decision

Farm Net will have one product-wide Subscription and Entitlement platform.
AI is a consumer of that platform, not a separate billing system. Roles and
permissions decide whether a user may perform an operation; entitlements and
quotas decide whether the user's current plan enables it and at what limit.

```text
permission allowed
AND entitlement enabled
AND quota available
```

Safety, consent withdrawal, personal-data deletion, source visibility, severe
weather warnings, and human-escalation guidance must never be paywalled.

## Verified real state

### Present

- Historical design documentation names `billing_plans`,
  `billing_plan_features`, `billing_subscriptions`, and
  `billing_feature_usage`.
- Auth seed contains plan and subscription Admin permissions.
- Finance has TOMAN-only billing invoices, invoice items, wallets, immutable
  balanced ledger transactions, ledger entries, settlement flows, and
  reconciliation.
- Orders has payment attempts, Mock payment, and a disabled/unverified
  production Zarinpal boundary.
- Mobile has typed own-invoice and wallet views.
- Admin has typed Finance operations.

### Absent

- No Subscription SQLAlchemy model or database table.
- No Subscription Alembic revision.
- No plan, plan-feature, subscription, entitlement, quota, usage, renewal, or
  add-on service.
- No public/user or Admin Subscription API.
- No Mobile plan/current-subscription/usage/checkout UI.
- No Admin plan/subscription/usage UI.
- No Subscription lifecycle notifications or scheduled expiry worker.
- No atomic quota reservation, idempotent usage finalization, or refund of
  failed reservations.
- No AI module or AI usage record exists yet.

Seeded future permissions and design documents are not implementation evidence.

## Existing Finance reuse boundary

The ledger, wallet, reconciliation, payment-gateway abstraction, TOMAN
constraints, trace IDs, and idempotency conventions should be reused.

The current `finance_billing_invoices` contract is marketplace-oriented:
it requires both payer and provider users and enforces
`platform_amount + provider_amount = total_amount`. A Farm Net subscription is
platform-owned and has no marketplace provider. Step 25.6 must therefore
introduce an explicit platform-billing contract or a backward-compatible
invoice extension; it must not fake a provider user or weaken existing
marketplace constraints.

Subscription activation must follow verified payment and be idempotent.
Wallet balance and AI credits remain separate concepts:

```text
wallet/ledger amount = real TOMAN money
feature quota = non-monetary product allowance
```

## Canonical capability model

Plans are versioned commercial packages. Features are stable product codes.
Entitlements are resolved values for a subscription period. Usage is an
append-only, auditable consumption history.

Feature value kinds:

- boolean;
- integer limit;
- decimal limit;
- string policy;
- JSON policy;
- unlimited.

Initial cross-product namespaces:

```text
farms.max_count
history.retention_days
reports.export_pdf
reports.deep_monthly
support.level

ai.text_chat
ai.farm_context
ai.deep_analysis
ai.image_analysis
ai.smart_diary
ai.report_export
ai.processing_priority

store.products_max_count
services.offers_max_count
rentals.equipment_max_count
```

The exact defaults and commercial prices are deferred until runtime cost and
product data exist. All customer-facing prices remain `TOMAN`.

## AI quota requirements fixed before AI implementation

AI requires more than a counter:

1. estimate the feature cost before a run;
2. atomically reserve quota;
3. reject concurrent over-consumption;
4. finalize exactly once after a usable response;
5. release on Provider, timeout, validation, or internal failure;
6. deduplicate by idempotency key;
7. record Provider/model/token/cost details separately in future AI usage;
8. never deduct quota for safety blocks or unauthorized requests.

`billing_feature_usage` is the customer-facing commercial allowance record.
Future `ai_usage_records` will store technical Provider usage and cost. They
must reconcile but must not be the same table.

## Initial plan families

- `free`: useful baseline access and safety features.
- `farmer_plus`: farm-context AI, higher limits, smart diary and reports.
- `professional`: role-aware professional limits for farmer, seller, service
  provider, lessor, or consultant.
- `organization`: deferred until the individual product is stable.

A plan does not grant a professional role or bypass provider approval.

## Approved Phase 25 sequence

1. **25.1** Real-State Audit + AI Entitlement Boundary.
2. **25.2** Plan, Feature, Subscription + Entitlement DB Contract.
3. **25.3** Plan Catalog + Public/User Read APIs.
4. **25.4** Subscription Lifecycle, Periods + Cancellation.
5. **25.5** Atomic Quota Reservation, Usage + Idempotency.
6. **25.6** TOMAN Invoice/Wallet/Payment Integration.
7. **25.7** Renewal, Expiry, Grace Period + Notifications.
8. **25.8** Mobile Plans, Current Subscription, Usage + Checkout.
9. **25.9** Admin Plans, Subscriptions, Usage + Manual Operations.
10. **25.10** Security, Concurrency, Audit + Reconciliation Hardening.
11. **25.11** Docs, Postman + Runtime Regression.
12. **25.12** Unified Subscription Release Gate + Tag.

## Completion gate

Phase 25 is complete only when:

- one subscription resolves product-wide typed entitlements;
- roles/permissions and subscriptions remain independent;
- Free, Farmer Plus, and Professional plans are supported;
- quotas reserve and finalize exactly once under concurrency;
- failed AI-style runs can release reservations without consumption;
- checkout uses TOMAN and activates only after verified payment;
- upgrade, downgrade, cancellation, expiry, and grace rules are explicit;
- Mobile and Admin use typed contracts;
- privacy and safety features are not paywalled;
- tests, migration, seed, OpenAPI, health, Postman, Git, and release gates pass.

Phase 21 Farmer AI/RAG resumes after this foundation is released.

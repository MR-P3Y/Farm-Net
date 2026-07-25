# Phase 25.3 — Plan Catalog + Public/User Read APIs

Date: 2026-07-26

Status: completed.

## Delivered

- Added an idempotent registry of 15 namespaced product features.
- Added one active default `free` plan, version 1, priced at `0 TOMAN`.
- Added all 15 typed Free plan values, including the reserved future AI
  allowances.
- Added public typed plan list and detail APIs.
- Added authenticated owner-scoped current subscription, entitlement, and
  usage read APIs.
- Empty owner state returns `null` subscription or empty lists; reads do not
  create or mutate a subscription.

## APIs

```text
GET /api/v1/billing/plans
GET /api/v1/billing/plans/{plan_code}
GET /api/v1/billing/subscription/me
GET /api/v1/billing/entitlements/me
GET /api/v1/billing/usage/me
```

The first two routes are public and expose only active/effective plan versions.
The last three require explicit owner permissions and always filter by the
authenticated user ID.

## Initial Free contract

- one Farm;
- 30-day history policy;
- 20 future AI text requests;
- eight future AI Farm-context requests;
- one future AI image analysis;
- no deep AI analysis or AI report export;
- limited Store products, Service offers, and Rental equipment.

These values are product configuration and do not claim that the future AI
features are implemented. Paid prices and plans remain deferred until runtime
cost data and Admin plan management exist.

## Verification

- Ruff and compileall: passed.
- focused Subscription tests: 5 passed.
- complete Backend tests: 283 passed; 27 existing warnings.
- Subscription seed twice: 15 features / 1 plan / 15 values, no duplicates.
- Alembic no-drift: passed at `96f4165b43fe`.
- Runtime public catalog: one Free plan, TOMAN 0, 15 features.
- Owner endpoints without authentication: three 401 responses.
- Runtime app/database/Redis health: passed.

Next: Step 25.4 Subscription Lifecycle, Periods + Cancellation.

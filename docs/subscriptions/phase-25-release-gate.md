# Phase 25.12 — Unified Subscription Release Gate

Status: passed.

Release tag: `v0.27.0-subscriptions-foundation`

Currency: `TOMAN`

## Released Scope

- versioned public Billing plans and typed feature values;
- owner Subscription, Entitlement, Usage, estimate, Free provisioning,
  cancellation, resume, checkout, renewal, and payment verification;
- atomic quota reservation/finalization/release with idempotency;
- TOMAN Invoice, Wallet/Ledger, mock payment, and disabled-by-default
  Zarinpal integration;
- expiry, Grace, renewal, and exact-once notification lifecycle;
- Mobile plan, current subscription, Usage, and checkout center;
- Admin plan/subscription lifecycle, Audit, and reconciliation;
- concurrency unique slots, immutable Audit, privacy, and reconciliation;
- canonical API documentation and the 30-request Postman collection.

## Final Verification

```text
Backend Ruff: OK
Backend compileall: OK
Backend pytest: 316 passed
Alembic current: e17c4b82a6d9 (head)
Alembic check: no new upgrade operations
Auth seed twice: 12 roles / 270 permissions
Subscription reconciliation: clean / 0 issues
Health: app ok / database ok / redis ok
OpenAPI Billing: 22 paths / 23 operations
Postman JSON: 16 collections valid
Subscription Postman: 30 requests
Mobile analyze: no issues
Mobile tests: 68 passed
Mobile web build: OK
Admin analyze: no issues
Admin tests: 27 passed
Admin web build: OK
Git develop vs origin/develop before release docs: 0 / 0
Git working tree before release docs: clean
```

The concurrent Mobile redesign was stabilized separately in commit `03258c0`.
Its API/Repository compatibility was restored without changing Backend API
behavior. Mobile analyze, tests, and web build then passed before this Gate.

## Honest Operational Boundaries

- Zarinpal is implemented but remains disabled until credentialed
  sandbox/production verification.
- State-changing Postman payment and subscription scenarios must run only in
  an isolated non-production environment with synthetic users.
- This is a foundation release, not a claim of production provider readiness.

## Next Product Track

Resume Phase 21 with the official product identity:

```text
Barzegar (برزگر) — Farm-Net agricultural AI assistant
```

Phase 21 must remain farmer-focused and must consume the Subscription
Entitlement/quota boundary completed in this release.

# Phase 25.9 — Admin Plans, Subscriptions, Usage + Manual Operations

Status: completed

## Backend Admin Contract

Seven permission-protected paths are available under
`/api/v1/admin/billing`:

- list and create plan versions;
- update Draft plans;
- activate or retire plan versions;
- list subscriptions with search, status filters, and pagination;
- read subscription detail and metered usage;
- manually activate a subscription;
- cancel immediately or at period end.

Active plans are immutable. Administrators create a new Draft version, review
its TOMAN price and typed feature values, then activate it. Activating a new
version retires the prior active version of the same plan family. The default
Free plan cannot be retired.

## Manual Activation Boundary

Manual activation:

- requires `billing.subscriptions.activate`;
- locks the target user and rejects a second active/grace subscription;
- accepts only an active plan;
- requires a human-readable reason;
- records `activation_source=admin`, the acting Admin user, and the reason;
- snapshots Entitlements with source `admin`;
- creates no fake payment, payment attempt, or invoice.

Migration `d8f3a9c21b74` adds the activation provenance fields. MySQL cannot
combine the nullable Admin FK using `ON DELETE SET NULL` with the cross-column
Check originally considered for this contract, so the source enum remains a DB
Check while the required actor/reason invariant is enforced in the sole Admin
activation service.

Cancellation requires the current subscription version. Immediate
cancellation closes the current period and Entitlements; period-end
cancellation preserves access until lifecycle processing reaches the boundary.

## Admin Panel

The typed Admin screen includes:

- permission-backed navigation and route;
- plan and subscription tabs;
- search, status filters, pagination, loading, empty, and error states;
- new Draft version creation by cloning a reviewed feature template;
- plan activation and retirement;
- manual activation with required user, active plan, and reason;
- subscription detail, activation provenance, TOMAN price, and typed usage;
- immediate or period-end cancellation.

No raw JSON is rendered by the UI.

## Verification

- Backend Ruff: passed.
- Backend compileall: passed.
- Backend tests: 309 passed.
- Subscription/Admin focused tests: 31 passed.
- Alembic upgrade/current: `d8f3a9c21b74`.
- Alembic no-drift check: passed.
- Auth seed twice: 12 roles and 268 permissions on both runs.
- Runtime OpenAPI: 7 Admin Billing paths.
- Runtime unauthenticated boundary: 401.
- Health: app, database, and Redis OK.
- Admin analyze: passed with no issues.
- Admin tests: 26 passed.
- Admin web build and Wasm dry-run: passed.

Concurrent Mobile design work remains owner-controlled and was not modified,
formatted, staged, or included in this step.

## Next

Phase 25.10 — Security, Concurrency, Audit + Reconciliation Hardening.

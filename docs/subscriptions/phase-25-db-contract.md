# Phase 25.2 — Plan, Feature, Subscription + Entitlement DB Contract

Date: 2026-07-26

Status: completed.

## Delivered tables

1. `billing_plans`
2. `billing_features`
3. `billing_plan_features`
4. `billing_subscriptions`
5. `billing_subscription_periods`
6. `billing_entitlements`
7. `billing_feature_usage`
8. `billing_usage_reservations`

Alembic revision: `96f4165b43fe`.

## Contract boundaries

- Plans are versioned and priced only in `TOMAN`.
- Free plans must have zero price.
- Custom billing periods require an explicit positive duration.
- Features have stable namespaced codes and typed value kinds.
- Safety-exempt features cannot be metered.
- Plan feature values remain separate from resolved period entitlements.
- Subscription periods snapshot plan code, version, price, and currency.
- Entitlements snapshot the effective feature code, limit/policy, and validity
  range so later plan edits do not rewrite historical access.
- Feature usage separates consumed and reserved amounts.
- Reservations have a unique idempotency key and explicit terminal state.
- Wallet/ledger money and product quota remain different accounting domains.

## Lifecycle foundations

Subscription:

```text
pending → active → grace → expired
pending/active/grace → cancelled
```

Period:

```text
pending → active → closed
pending → void
```

Reservation:

```text
reserved → finalized
reserved → released
reserved → expired
```

The database provides status, range, non-negative amount, uniqueness, TOMAN,
terminal-state, and optimistic-version constraints. Transition services,
single-active-subscription enforcement, quota locking, and expiry processing
remain deliberately assigned to later Phase 25 steps.

## Permissions

The base user role now receives:

```text
billing.plans.public_read
billing.subscription.read_own
billing.subscription.manage_own
billing.usage.read_own
billing.entitlements.read
```

Existing Admin plan/subscription/usage permissions remain unchanged.

## Verification

- Ruff: passed.
- compileall: passed.
- focused Subscription tests: 3 passed.
- complete Backend tests: 281 passed; 27 existing warnings.
- Alembic upgrade: passed at `96f4165b43fe (head)`.
- Alembic no-drift check: passed.
- Auth seed twice: 12 roles / 268 permissions.
- Runtime app/database/Redis health: passed.

Next: Step 25.3 Plan Catalog + Public/User Read APIs.

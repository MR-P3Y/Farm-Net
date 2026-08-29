# Phase 26.3: service commission, refund, and completion release

## Owner-approved policy

1. The default Services commission is `10%` and is editable by an authorized
   Admin. The selected percent is snapshotted when the final-price Invoice is
   created.
2. A paid service receives a full refund before work starts. After work starts,
   the full-refund request requires Admin review.
3. Provider proceeds remain pending until the requester confirms completed
   work. Admin has an explicit override. No automatic timeout releases funds.

All monetary values use canonical `TOMAN`. A service requester and provider
must be distinct users; the financial self-payment prohibition remains intact.

## State and accounting contracts

`finance_billing_refunds` owns the immutable invoice, successful payment
attempt, payer/provider, amount, reason, idempotency key, review decision, and
processing snapshots. One Invoice can have at most one full refund.

Completion confirmation moves the provider share exactly once:

```text
provider_pending -> provider_available
```

The request must already be `completed`. Provider completion alone does not
release funds.

On a successful full refund:

```text
provider_pending  (debit provider share)
platform_revenue  (debit commission)
platform_cash     (credit full invoice total)
```

If completion was already confirmed, the pending-to-available release is
reversed first. Refund processing fails closed when released money has already
entered settlement/reservation and cannot be recovered from available balance.

## API surface

- `POST /api/v1/services/requests/{id}/refund`
- `POST /api/v1/services/requests/{id}/confirm-completion`
- `POST /api/v1/admin/services/requests/{id}/confirm-completion`
- `GET /api/v1/admin/commission/policies`
- `GET|PATCH /api/v1/admin/commission/policies/service_request/default`
- `GET /api/v1/admin/finance/billing-refunds`
- `PATCH /api/v1/admin/finance/billing-refunds/{id}/decision`
- `POST /api/v1/admin/finance/billing-refunds/{id}/complete-mock`

The last operation moves no real gateway money. It is available only for a
successful Mock payment outside production. A real Provider refund adapter is
still required before production refunds can be called operationally complete.

## Mobile and Admin behavior

Mobile renders the full-refund rule before confirmation, shows review and
processing states, and exposes the bottom floating completion-confirmation
action only to the requester of a completed request. The Provider workbench
shows whether funds are still waiting or have been released.

Admin exposes the Services commission, refund review/Mock completion, and the
manual completion confirmation override. Existing light/dark and
Persian/English contracts are preserved; dates continue to use the shared
Jalali/Gregorian presentation layer without changing Gregorian ISO API values.

## Deployment

```powershell
cd E:\Farm-Net\backend
alembic upgrade head
python scripts/seed_finance.py
```

The migration head is `r26f6a7b8c9d`. The seed creates the `10.00%` Services
default only when absent and preserves later Admin edits. No environment change
or service restart is required by the schema/seed operation itself.

## Verification on 2026-08-10

- Backend Ruff/compileall: passed; all 437 tests passed.
- Alembic current/head: `r26f6a7b8c9d`; `alembic check` reports no drift.
- Finance seed ran twice with zero writes and retained `10.00%`.
- Rollback-safe lifecycle smoke passed price, Invoice, Mock payment, start,
  completion, requester confirmation, release, reviewed refund, release
  reversal, full refund, and cancellation without retaining test rows.
- Mobile: clean analyze, 166 tests, Web release/Wasm dry run, and Android debug
  APK passed with the Android reverse task excluded.
- Admin: clean analyze, 35 tests, and Web release/Wasm dry run passed.
- Source OpenAPI contains all eight new paths; sampled unauthenticated requests
  return `401`. Postman parses with 46 requests.
- After explicit owner approval, only `farmnet_backend` received one complete
  restart. Runtime app/database/Redis health is `ok`, all eight paths are live,
  and sampled unauthenticated requests return `401` rather than `404`. MySQL,
  Redis, Qdrant, phone, and Chrome were not restarted. The two-account manual
  acceptance flow remains pending.

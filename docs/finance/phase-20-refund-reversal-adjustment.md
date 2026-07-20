# Phase 20.9 Refund, Reversal, Adjustment and Concurrency Hardening

## Accounting Contract

Product Order Refund keeps the original Payment and Release journals immutable.
If Release exists, a new exact-once Reversal journal debits provider available
and credits provider pending, with `reversal_of_id` pointing to Release. The
legacy Refund journal can then debit pending and reverse platform revenue/cash
exactly as before.

The Release journal and provider available wallet account are row-locked. When
available balance is below the provider share because funds are reserved or
already moved to simulated payout clearing, Refund fails closed. It never
creates a negative provider balance and never claims recovery of a real bank
payout.

## Controlled Adjustment

`POST /api/v1/admin/finance/adjustments` requires
`finance.adjustments.create`. Payload requires provider, positive amount,
`credit` or `debit`, `TOMAN`, idempotency key, and a meaningful reason. Every
adjustment is a balanced posted journal against adjustment clearing. Debit is
blocked above available balance. Replays return the same journal; mismatched
payloads conflict. One Admin Audit Log is stored per journal.

## Boundary

No posted journal is edited or deleted. No partial Refund, real payment gateway,
real payout, chargeback provider integration, or cross-domain funded release is
introduced by this step.

## Verification

- Ruff: passed.
- Python compileall: passed.
- Focused Backend tests: 25 passed.
- Full Backend regression: 113 passed, 16 existing UTC deprecation warnings.
- Alembic current/heads: `fdcb2ab80c12 (head)`; no migration is required.
- Auth seed: passed twice, 12 roles and 249 permissions.
- Runtime health: app/database/Redis all `ok`.
- OpenAPI: 248 paths; Admin Adjustment route present.
- Postman: valid JSON, 42 requests including one Adjustment request.

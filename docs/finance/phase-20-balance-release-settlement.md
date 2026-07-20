# Phase 20.8 Balance Release and Settlement/Payout Workflow

## Release Truth

Only Product Orders currently have a successful payment journal. When a paid
order reaches `delivered`, an exact-once balanced Journal moves its provider
share from `provider_pending` to `provider_available`. No new money is created.
Services, Consultations, and Rentals remain ineligible because they have no
successful payment event.

Wallet balances are calculated from immutable Ledger entries; no mutable cached
balance is introduced. The own-wallet API returns `pending`, `available`, and
`reserved` values in `TOMAN`.

## Settlement Workflow

Eligible provider roles can submit an idempotent settlement request no greater
than available balance. Creation atomically moves available liability to
reserved liability. Admin approval changes workflow state only. Rejection
returns reserved to available through another Journal.

The final operation is explicitly `simulated_completed`: it moves reserved
liability to platform payout clearing. It does not call a bank, PSP, card, or
external payout provider and does not claim that money reached the user.

Every movement has source identity, idempotency key, actor, trace ID, positive
`TOMAN` amount, and balanced debit/credit entries. Financial request identity
is immutable and history cannot be deleted.

## APIs and Permissions

- `GET /finance/wallet/me` — `wallet.read_own`
- `GET /finance/settlements/me` — `settlements.read_own`
- `POST /finance/settlements` — `settlements.create_own`
- `GET /admin/finance/settlements` — `finance.settlements.read`
- `PATCH /admin/finance/settlements/{id}/decision` — `finance.settlements.manage`
- `POST /admin/finance/settlements/{id}/simulate-payout` — same Admin permission

The new own-settlement permissions are granted to shop owner, service provider,
lessor, and consultant roles. Only balances actually present in their Ledger
can be reserved.

## Explicit Next-Step Boundary

Refund/reversal after release or reservation, race hardening across refund and
settlement, negative-balance prevention under those competing commands, and
adjustment journals belong to Step 20.9. Real provider payout belongs to later
credentialed gateway/payout work.

## Verification

- Ruff/compileall: passed
- focused finance/order tests: 26 passed
- full Backend: 110 passed with 16 existing UTC warnings
- Alembic: `fdcb2ab80c12 (head)`
- Auth seed twice: 12 roles, 248 permissions
- OpenAPI: six Wallet/Settlement path templates
- Runtime: zero settlements and zero release journals; no real-row smoke candidate
- health: app/database/Redis `ok`
- Alembic metadata: no Step 20.8 drift; four old index naming differences remain
- Postman: six requests added and collection parses successfully

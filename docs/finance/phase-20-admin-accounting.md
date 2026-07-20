# Phase 20.13 Admin Accounting, Settlement and Reconciliation

## Admin Surface

The Finance page now provides typed, paginated tabs for invoices, attempts,
transactions, refunds, Audit Logs, Ledger Journals, Wallet Accounts and
Settlements. Requested Settlements expose approve/reject actions; approved rows
expose only simulated clearing.

A typed Reconciliation card reports clean/mismatch state and counts of missing
Payment bridges, missing Refund bridges and unbalanced journals. Refresh runs
the existing read-only reconciliation service.

## Security Boundary

Routes retain `finance.ledger.read`, `finance.wallets.read`,
`finance.settlements.read/manage`, and `finance.ledger.reconcile` guards. The UI
uses typed fields and does not render raw JSON. No real bank payout is executed.

## Verification

- Admin Flutter analyze: passed.
- Admin tests: 16 passed.
- Admin Web build: passed, including Wasm dry run.
- Backend Ruff/compileall: passed.
- Backend tests: 129 passed, 17 existing UTC warnings.
- Runtime health: app/database/Redis all `ok`.
- OpenAPI: 253 paths including Ledger and Wallet Admin reads.

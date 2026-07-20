# Phase 20 Wallet/Settlement/Accounting Release Gate

## Release

- Step: 20.15
- Tag: `v0.22.0-wallet-settlement-accounting-foundation`
- Branch: `develop`
- Result: passed

## Verified scope

This release contains canonical Iranian toman contracts, Wallet Accounts,
immutable double-entry Ledger, order Payment/Refund bridges, universal Invoice
and Commission snapshots, Service/Consultation final-price agreements, Rental
revenue/deposit boundaries, provider balance release, Settlement reservation
and simulated clearing, Refund/Reversal/Adjustment hardening, private financial
notifications and audit, the disabled-by-default Zarinpal adapter, Mobile
Finance Center, typed Admin Finance operations, and consolidated API/Postman
documentation.

## Gate evidence

- Backend: Ruff and compileall passed; 129 tests passed with 17 existing
  `datetime.utcnow` deprecation warnings.
- Database: Alembic upgraded/current at `fdcb2ab80c12 (head)`; Auth seed passed
  twice at 12 roles and 249 permissions.
- Runtime: application, database, and Redis all `ok`; OpenAPI exposes 253 total
  paths and 27 Finance/Payment/Admin-refund paths.
- Reconciliation: no missing Payment/Refund bridges, unbalanced journals, or
  entry mismatches. The runtime has zero successful Payment/Refund rows.
- Mobile: analyze passed; 38 tests passed; Web build and Wasm dry-run passed.
- Admin: analyze passed; 17 tests passed; Web build and Wasm dry-run passed.
- Postman: valid 48-request collection; all 18 raw JSON templates parse after
  normal Postman variable resolution.
- Git: clean release candidate and `develop` synchronized with
  `origin/develop` before release documentation.

The first runtime OpenAPI probe returned 247 paths because the long-running
Backend process had not reloaded the latest source. A non-destructive Backend
restart loaded the release candidate; health then passed and OpenAPI returned
the expected 253/27 counts.

## Explicit operational boundary

Zarinpal remains disabled by default. No Merchant ID or public HTTPS callback
was available, so no credentialed sandbox or production payment was performed.
Settlement completion is simulated clearing, not a real bank payout. Zero-data
reconciliation is consistency evidence, not evidence of real money movement.

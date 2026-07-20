# Phase 20.12 Mobile Wallet, Invoices and Provider Settlements

## Mobile Contract

The authenticated Finance Center shows payer-owned invoices for every buyer.
Roles with provider Finance permissions additionally see Ledger-derived pending,
available and reserved balances, Settlement history, and Settlement creation.
All values are labeled and submitted as Iranian toman (`TOMAN`).

The screen includes loading/error/empty states, pull-to-refresh, positive whole-
toman validation and Backend error rendering. A successful Settlement refreshes
balances and history.

## Invoice Privacy

The two `/finance/invoices/me` routes filter by `payer_user_id`. Their schema
does not contain `platform_amount` or `provider_amount`, preventing disclosure
of internal/provider economics to buyers. Admin invoice routes remain separate.

## Verification

- Mobile Flutter analyze: passed.
- Mobile tests: 38 passed.
- Mobile Web build: passed, including Wasm dry run.
- Backend Ruff/compileall: passed.
- Backend tests: 129 passed, 17 existing UTC warnings.
- Runtime health: app/database/Redis all `ok`.
- OpenAPI: 251 paths including two owner invoice paths.
- Credentialed provider payment and real bank payout remain outside this step.

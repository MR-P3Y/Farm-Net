# Phase 16.12 — Docs/Postman + Runtime Regression

## Contract inventory

- Eight Rental tables and 24 seeded Rental permissions.
- 29 Runtime OpenAPI paths across public, requester, lessor, and Admin roles.
- 35 Postman requests covering all 29 unique paths with valid raw JSON bodies.
- Complete API, notification, privacy, concurrency, Mobile, and Admin docs.

## Verification

```text
Backend Ruff (app + scripts): OK
Backend compileall: OK
Backend pytest: 79 passed, 16 existing non-Rental UTC warnings
Alembic: 104ae669cc1a (head)
Auth seed twice: 12 roles, 241 permissions, identical
Rental tables: 8
Rental permissions: 24
Health: app=ok, database=ok, redis=ok
Runtime Rental OpenAPI paths: 29

Mobile analyze: OK
Mobile tests: 34 passed
Mobile Web build + Wasm dry run: OK

Admin analyze: OK
Admin tests: 14 passed
Admin Web build + Wasm dry run: OK

Postman JSON: OK
Postman requests: 35
Postman raw body errors: 0
Postman unique paths: 29
OpenAPI missing/extra paths: 0/0
```

## Explicit financial boundary

The accepted Rental request stores immutable price, rental, deposit, total, and
currency snapshots. No invoice, payment, deposit capture/release, commission,
refund, settlement, damage claim, or penalty behavior is represented as
implemented.

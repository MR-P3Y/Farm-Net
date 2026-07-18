# Phase 16.5 — Availability + Pricing Rules

## Completed

- Added atomic owner pricing replacement/list and public active pricing.
- Enforced positive prices/minimum units, unique unit/operator pairs, supported
  units, uppercase currency, and operator-mode compatibility.
- Added owner availability list/create/update/delete and public date-range
  checks with timezone normalization.
- Prevented block-to-block and block-to-accepted/in-progress-booking overlap;
  adjacent ranges remain valid.
- Hid owner block notes from public conflict output.
- Hardened equipment approval to require media and active pricing.

## Verification

```text
Ruff: OK
compileall: OK
focused Rental tests: 12 passed
full Backend tests: 71 passed, 16 existing datetime.utcnow warnings
Alembic: 104ae669cc1a (head), no schema change
Runtime Rental OpenAPI paths: 19
Unauthenticated owner pricing: 401
Health: app=ok, database=ok, redis=ok
Postman JSON: 25 requests, parse OK
```

Rental request creation, price snapshots, booking locks, and workflow begin in
Step 16.6.

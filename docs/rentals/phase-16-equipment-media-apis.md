# Phase 16.4 — Equipment Listing + Media APIs

## Completed

- Added public approved equipment list/detail with category, geo,
  operator-mode, and text filters.
- Added approved-lessor owned list/create/update/submit operations.
- Added technical identity, delivery, deposit, location, activation, and
  with/without/either-operator contracts.
- Integrated the real Media domain with owner, active, and public checks,
  maximum 20 items, unique files, and deterministic primary media.
- Added Admin equipment listing and status-specific approve/reject/suspend
  permission enforcement.
- Kept private address, Admin notes, actor IDs, and internal timestamps out of
  public contracts.

## Verification

```text
Ruff: OK
compileall: OK
focused Rental tests: 8 passed
full Backend tests: 67 passed, 16 existing datetime.utcnow warnings
Runtime Rental OpenAPI paths: 14
Public equipment list: OK (total=0 before approved fixtures)
Unauthenticated owner list: 401
Health: app=ok, database=ok, redis=ok
Postman JSON: 17 requests, parse OK
```

Pricing rules and availability blocks remain Step 16.5. Equipment approval
readiness will be hardened there to require at least one active pricing rule.

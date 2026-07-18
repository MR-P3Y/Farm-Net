# Phase 16.7 — Rental Notifications + Privacy/Concurrency Hardening

## Completed

- Added notification events for request `created`, `accepted`, `rejected`,
  `in_progress`, `completed`, and `cancelled`.
- Used deterministic event keys, unique recipients, and self-notification
  suppression through the existing Phase 11 Notification foundation.
- Kept notification creation in the same transaction as request/status-log
  writes (`commit=False`) so partial domain delivery records are not claimed.
- Routed requester, lessor, and Admin actions to the correct opposite parties.
- Serialized pricing replacement and availability create/update/delete with
  booking acceptance using the equipment row lock.
- Revalidated pricing minimum units and operator compatibility at acceptance.
- Preserved list/detail ownership and `admin_note` privacy. No API route,
  database schema, payment, invoice, settlement, or external provider was added.

## Verification

```text
Ruff: OK
compileall: OK
focused Rental + Notification tests: 41 passed
full Backend tests: 79 passed, 16 existing datetime.utcnow warnings
Alembic: 104ae669cc1a (head), no schema change
Runtime Rental OpenAPI paths: 29
Health: app=ok, database=ok, redis=ok
Postman JSON: 35 requests, parse OK
```

The Rental Postman collection remains 35 requests because Step 16.7 hardens
behavior on the existing request paths and adds no endpoint.

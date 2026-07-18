# Phase 16.6 — Rental Request/Booking Workflow

## Completed

- Added requester create/list/detail/cancel contracts with exact ownership.
- Added approved-lessor assigned list/detail and controlled transitions:
  `pending -> accepted|rejected`, `accepted -> in_progress`, and
  `in_progress -> completed`.
- Added Admin list/detail and controlled management transitions.
- Prevented self-rental, inactive/wrong pricing, operator mismatch, below-minimum
  units, blocked ranges, and invalid cancellation/transitions.
- Acceptance locks equipment, revalidates commercial/availability state, and
  records immutable price, rental, deposit, total, and currency snapshots.
- Added deterministic unique status-log events and role-specific Admin-note
  privacy. No invoice, payment, deposit capture, or settlement is claimed.

## Verification

```text
Ruff: OK
compileall: OK
focused Rental tests: 16 passed
full Backend tests: 75 passed, 16 existing datetime.utcnow warnings
Alembic: 104ae669cc1a (head), no schema change
Runtime Rental OpenAPI paths: 29
Unauthenticated requester list: 401
Health: app=ok, database=ok, redis=ok
Postman JSON: 35 requests, parse OK
```

Notifications, public/private contract hardening, and pricing/availability race
hardening are Step 16.7.

# Phase 24.8 — Privacy, Concurrency, Audit + Retention Hardening

Verified: 2026-07-26

## Outcome

Farm mutation paths retain the authenticated owner boundary, serialize
conflicting aggregate changes with row locks, and append a minimal audit event
inside the same transaction as the business change.

Alembic revision `29edf5a07168` adds `farm_audit_logs`. Each event records the
Farm, actor, action, target identity, optional non-sensitive structural
details, and creation time. Foreign keys use `RESTRICT`.

Audit details deliberately do not copy Farm names/descriptions, coordinates,
boundaries, laboratory values, diary notes, media captions, or other private
content. There is no owner or public audit API in this step. Restricted Admin
support is deferred to Step 24.11.

## Concurrency

- Farm and Plot allocation/lifecycle mutations lock the owner Farm.
- Plot mutations lock the Plot after the Farm, preserving stable lock order.
- Crop-cycle mutations lock the owning aggregate/cycle.
- environment upserts lock the Farm and Plot;
- diary writes lock the owner-scoped active cycle;
- audit creation and business mutation commit or roll back together.

## Retention

Operations, operation inputs, harvest observations, laboratory observations,
Farm media links, and audit logs have ORM update/delete guards. Crop cycles
cannot be changed after reaching `completed` or `cancelled`, and crop-cycle
rows cannot be deleted through ORM.

Farm, Plot, and water-source records use archive-first lifecycle. There is no
automatic purge and no destructive owner endpoint. A future account-erasure
workflow must define legal retention, media cleanup, de-identification, and
audit preservation explicitly; this step does not guess that policy.

## Verification

- Ruff/compileall: passed.
- Audit/retention tests: 10 passed.
- All focused Farm tests: 43 passed.
- Full Backend suite: 269 passed with 27 existing warnings.
- MySQL migration/no-drift: passed at `29edf5a07168`.
- Fresh Backend image/container: passed.
- Runtime app/database/Redis health: all `ok`.

## Next step

Step 24.9 — Farm Weather Linking + Contextual Alerts.

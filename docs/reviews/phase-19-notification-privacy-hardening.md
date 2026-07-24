# Phase 19.6 — Notifications, Privacy, Exact-Once + Concurrency Hardening

## Notifications

- New Review reports notify only active users who hold
  `review_reports.admin_read`; role names are not hard-coded.
- Hide, restore, and delete notify the Review author.
- Reviewed, resolved, and dismissed reports notify the reporter.
- The actor is excluded by the shared self-notification contract.
- Stable event keys use persisted report or moderation-log IDs.
- Existing event and recipient/channel unique constraints make retries
  exact-once across routed channels.

## Privacy

Notification payloads carry only IDs required for navigation, governed reason,
and resulting status. They exclude Review body, report description, resolution
note, contact information, source/order/request identity, and unrelated
reporter identity. Public and owner schemas retain their existing least-data
contracts; full reporter/moderator fields remain permission-protected Admin
data.

## Concurrency

Review/source uniqueness remains database-enforced. Canonical aggregate
creation now uses a nested transaction savepoint: simultaneous first Reviews
for one subject either create the aggregate or recover the winning unique row
with a locking read, then apply their delta under lock. Report uniqueness is
database-enforced, and unchanged/terminal moderation retries do not create a
second log or notification.

No SMS/email/push provider activation or client UI is part of this step.

## Verification

| Check | Result |
| --- | --- |
| Ruff / compileall | OK |
| Full Backend tests | 186 passed; 18 known warnings |
| Runtime health | app/database/Redis `ok` |
| Alembic | `a7c9e1f30d13` head |
| OpenAPI | 264 paths / ten Review paths |
| Permission recipient lookup | real seeded Review Admin resolved |
| Review event smoke | accepted, rolled back, zero residual rows |
| Postman | 14 collections / 325 requests; JSON parse OK |

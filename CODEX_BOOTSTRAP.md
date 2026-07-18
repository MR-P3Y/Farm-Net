# Codex Bootstrap for Farm-Net

Use this checklist whenever a new Codex task starts without previous chat
history.

## Repository

The authoritative project is:

```text
E:\Farm-Net
```

Do not confuse it with similarly named folders or empty repositories on drive C.

## Mandatory First Read

Before proposing or changing code, read:

1. `PROJECT_CONTEXT.md`
2. `docs/PROJECT_PROGRESS.md`
3. `README.md`
4. relevant module documentation and source files

Then inspect:

```powershell
git status --short --branch
git log --oneline --decorate -20
git tag --list
```

Also inspect relevant models, migrations, permission seed, schemas, repository,
service, routers, notification events, mobile/admin features, API docs, and
Postman collections.

## Before Editing

Report:

- repository path;
- current branch and HEAD;
- tracked and untracked Git status;
- latest relevant commits and tags;
- files that already implement the requested feature;
- the exact current step;
- proposed scope and verification plan.

Do not assume the latest chat handoff is current when repository evidence says
otherwise.

## Current Handoff

As of 2026-07-16:

```text
Windows environment recovery: completed
Step 17.1 Services DB + Permissions: completed (3b8af10)
Step 17.2 Categories + Provider Profiles: completed (0f3a07d)
Step 17.3 Service Offers backend: completed (c247d9d)
Step 17.4 Services Request Flow: completed (f1adaf5)
Step 17.5 Request Notifications + Contract Hardening: completed
Step 17.6 Mobile Service Discovery + Detail: completed
Step 17.7 Mobile Service Request Flow: completed
Step 17.8 Provider Profile + Offer Management Mobile: completed
Step 17.9 Provider Request Workbench: completed
Step 17.10 Admin Panel Services: completed (bda9699)
Step 17.11 Docs/Postman + Runtime Regression: completed
Step 17.12 Services Release Gate + Tag: completed (v0.17.0-services-foundation)
Phase 9.1 Orders/Payments audit: completed
Phase 9.2 Financial Contracts + DB Hardening: completed
Phase 9.3 Atomic Checkout + Inventory Reservation: completed
Phase 9.4 Checkout Idempotency + Contract Hardening: completed
Phase 9.5 Payment Orchestration + Idempotent Verify: completed
Phase 9.6 Refund Request + Idempotent Processing: completed
Phase 9.7 Admin Finance Read Models + Audit: completed
Phase 9.8 Admin Finance UI: completed
Phase 9.9 Mobile Payment UX + Contract Migration: completed
Phase 9.10 Docs/Postman + Release Regression: completed
Phase 9.11 Release Gate + Tag: completed (v0.18.0-orders-finance-foundation)
Phase 11.1 Notifications real-state audit: completed
Phase 11.2 Delivery Contracts + DB Hardening: completed (e72b9f4c31a6)
Phase 11.3 User Preferences + Channel Routing: completed (f84c2a1d9037)
Phase 11.4 Retry Queue + Failure/Delivery Logs: completed (a16d7c4e52b9)
Phase 11.5 Email Provider Foundation: completed
Phase 11.6 SMS Provider Foundation: completed
Phase 11.7 Push Notification Foundation: completed (b27e8d5f64c1)
Phase 11.8 Mobile Notification Center Hardening: completed
Phase 11.9 Admin Notification Operations: completed
Phase 11.10 Docs/Postman + Runtime Regression: completed
Phase 11.11 Notifications Release Gate + Tag: completed (v0.19.0-notifications-delivery-foundation)
Phase 12.1 Product Category Management: completed
Phase 12.2 Category Governance Alignment Audit: completed
Next: Phase 12.3 Services Category Contract Hardening
```

Services means agricultural operational services, not equipment rental.

## Change Rules

- Modify only files required for the authorized step.
- Preserve unrelated tracked and untracked changes.
- Never stage or commit `.env`, secrets, build output, caches, local storage,
  uploaded media, DB dumps, or generated package metadata.
- If `backend/app/common.zip` exists, do not touch, stage, or commit it.
- Do not use destructive Git commands, delete Docker volumes, or replace the
  repository without explicit authorization.
- Do not commit or tag unless the user explicitly requests it.

## Implementation Pipeline

Follow this order unless repository evidence requires a narrower corrective
step:

1. DB model and Alembic migration
2. permission seed and role assignment
3. schemas
4. repository
5. domain service and status transitions
6. public/user/provider APIs
7. admin APIs
8. notification events and delivery triggers
9. mobile UI
10. admin-panel UI
11. API docs and Postman
12. compile, lint/analyze, tests, migration, health, and smoke checks
13. progress documentation
14. clean step-based commit/tag when explicitly authorized

## Verification Report

For each implementation step, provide:

- commands run and concise results;
- backend compile/lint/test results;
- Alembic heads/current/upgrade result when DB changes are involved;
- seed result when permissions change;
- Flutter analyze/test/build results for affected apps;
- health and feature smoke results;
- OpenAPI route count or contract check;
- final `git status`, separating intended source changes from generated or
  unrelated files.

Never describe a foundation as production-ready unless real external providers,
security controls, tests, deployment, monitoring, and operational verification
actually support that claim.

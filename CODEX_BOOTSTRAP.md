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
Next: Step 17.8 Provider Profile + Offer Management Mobile
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

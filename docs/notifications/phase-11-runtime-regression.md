# Phase 11.10 — Docs/Postman + Runtime Regression

## Contract inventory

- Runtime OpenAPI exposes 14 Notifications paths.
- The canonical Postman collection contains 20 requests, including two login
  helpers and coverage for all 14 real Notifications paths.
- User coverage includes inbox, unread count, ownership mutations,
  preferences, and Push device registration/deactivation.
- Admin coverage includes notification list/detail/system message plus delivery
  queue, detail/attempt history, and controlled retry.

## Runtime verification

```text
Backend focused Ruff: OK
Backend compileall: OK
Backend focused Notifications tests: 21 passed
Backend full pytest: 49 passed, 16 existing datetime.utcnow warnings
Alembic upgrade head: OK
Auth/permission seed: OK
Email disabled-mode worker: claimed=0, sent=0
SMS disabled-mode worker: claimed=0, sent=0
Push disabled-mode worker: claimed=0, sent=0
Health app/database/redis: OK
OpenAPI Notifications paths: 14

Mobile analyze: OK
Mobile tests: 28 passed
Mobile Web build/Wasm dry run: OK

Admin analyze: OK
Admin tests: 7 passed
Admin Web build/Wasm dry run: OK

Postman JSON parse: OK
Postman requests: 20
Postman real Notifications path coverage: 14/14
```

## Accurate release boundary

In-app messaging is active. Email, SMS, and Push have queue, retry, provider
adapter, and fail-closed worker foundations, but production vendor credentials
are not configured and no live external message was sent during verification.
Mobile Push token acquisition remains blocked on selecting and integrating a
real vendor SDK. Telegram delivery is not implemented.

No API, database, Mobile, Admin, or provider behavior changed in this step.

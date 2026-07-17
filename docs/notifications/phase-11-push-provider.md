# Phase 11.7 Push Notification Foundation

Completion date: 2026-07-18

## Implemented

- Owner-scoped Android/iOS/Web device token registry with unique token identity.
- Idempotent registration/token transfer and owner-only soft unregistration.
- Device token is accepted on write but never returned by API schemas.
- Push routing only when an active device exists.
- Fail-closed HTTPS JSON batch adapter, dispatcher, queue integration, and CLI:
  `python scripts/process_push_notifications.py --limit 50`.

## Configuration

```text
PUSH_ENABLED=false
PUSH_PROVIDER=http_json
PUSH_API_URL=
PUSH_API_KEY=
PUSH_TIMEOUT_SECONDS=15
```

## Verification

- Alembic/MySQL head: `b27e8d5f64c1`.
- Backend Ruff: OK; full tests: 49 passed with 16 existing UTC warnings.
- Device ownership/routing and fake batch transport: OK.
- Docker disabled runtime: zero claim/send; health app/database/Redis OK.
- Device register/unregister paths present in OpenAPI.
- No real Push key or network message was used.

## Deferred

- Vendor-specific FCM/APNs adapter and invalid-token feedback processing.
- Mobile token acquisition/refresh wiring: Step 11.8.

# Phase 11.3 User Preferences and Channel Routing

Completion date: 2026-07-18

## Implemented

- Owner-scoped `notification_preferences` table with unique
  user/event/channel identity.
- `GET` and idempotent `PUT /api/v1/notifications/preferences` contracts.
- Global `*` preferences and event-specific overrides.
- Routing precedence: event override, then global preference, then defaults.
- Default routing remains `in_app` only, preserving existing behavior.
- Email requires a verified email; SMS requires a verified phone.
- Enabled Email/SMS routes create exact-once pending notifications and delivery
  state for later provider workers.
- Push/Telegram preferences are stored but not routed without destination
  registries.
- Admin system messages remain mandatory in-app messages.

## Verification

- Alembic/MySQL head: `f84c2a1d9037`.
- Runtime table and unique constraint inspection: OK.
- Backend Ruff: OK.
- Backend full tests: 36 passed with 16 existing UTC deprecation warnings.
- Runtime health application/database/Redis: OK.
- OpenAPI notification paths: 9, including GET/PUT on preferences.
- Notifications Postman JSON: parseable and includes both preference requests.

## Deferred

- Retry worker and attempt history: Step 11.4.
- Real Email/SMS provider adapters: Steps 11.5 and 11.6.
- Device tokens and Push provider: Step 11.7.
- Mobile preference UI: Step 11.8.

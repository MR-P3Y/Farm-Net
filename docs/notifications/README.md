# Notifications Foundation

## Current Phase

```text
Phase 11 - Notifications / Events / Messaging Foundation
```

## Implemented

* Notification DB tables
* Notification permission seed
* Notification service foundation
* User notification APIs
* Admin notification APIs
* Order/payment event integration
* Verification/media event integration
* Flutter mobile notification inbox foundation
* Admin panel notification management foundation
* Database exact-once notification identity
* Provider-neutral retry and worker-lease fields
* User-owned global and event-specific channel preferences
* Verified Email/SMS destination routing to pending delivery state
* Atomic external-channel queue claim, retry backoff, and attempt history
* Fail-closed SMTP Email transport and one-batch dispatcher
* Fail-closed HTTPS JSON SMS transport and one-batch dispatcher
* Push device registry and fail-closed HTTPS JSON batch dispatcher
* Admin delivery queue, attempt timeline, filters, pagination, and controlled retry UI

## Tables

```text
notification_events
notifications
notification_delivery_logs
notification_preferences
notification_delivery_attempts
```

## Current Channel

```text
in_app
```

## User APIs

```text
GET    /api/v1/notifications/me
GET    /api/v1/notifications/me/unread-count
PATCH  /api/v1/notifications/{id}/read
PATCH  /api/v1/notifications/read-all
DELETE /api/v1/notifications/{id}
GET    /api/v1/notifications/preferences
PUT    /api/v1/notifications/preferences
```

## Admin APIs

```text
GET   /api/v1/admin/notifications
GET   /api/v1/admin/notifications/{id}
POST  /api/v1/admin/notifications/system-message
GET   /api/v1/admin/notifications/deliveries
GET   /api/v1/admin/notifications/deliveries/{id}
POST  /api/v1/admin/notifications/deliveries/{id}/retry
```

## Notes

SMS, email, push, and Telegram channels are not yet connected to real providers.

They are reserved for future delivery integration.

Step 11.2 hardening is documented in
`docs/notifications/phase-11-delivery-contracts.md`. It adds durable delivery
contracts but does not claim that an external delivery worker exists.

Step 11.3 preference precedence and destination rules are documented in
`docs/notifications/phase-11-preferences-routing.md`.

Step 11.4 queue, lease, backoff, and attempt history contracts are documented
in `docs/notifications/phase-11-retry-queue.md`.

Step 11.5 SMTP configuration and safe activation are documented in
`docs/notifications/phase-11-email-provider.md`.

Step 11.6 SMS transport and safe activation are documented in
`docs/notifications/phase-11-sms-provider.md`.

Step 11.7 device registry and Push dispatch are documented in
`docs/notifications/phase-11-push-provider.md`.

Step 11.8 Mobile preferences, action routing, and the exact vendor-SDK gap are
documented in `docs/notifications/phase-11-mobile-hardening.md`.

Step 11.9 typed Admin delivery operations and retry controls are documented in
`docs/notifications/phase-11-admin-operations.md`.

The verified current-state analysis and hardening boundary are recorded in
`docs/notifications/phase-11-real-state-audit.md`. In particular, pending rows
for external channels do not mean that delivery or retry is implemented.

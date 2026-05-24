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

## Tables

```text
notification_events
notifications
notification_delivery_logs
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
```

## Admin APIs

```text
GET   /api/v1/admin/notifications
GET   /api/v1/admin/notifications/{id}
POST  /api/v1/admin/notifications/system-message
```

## Notes

SMS, email, push, and Telegram channels are not yet connected to real providers.

They are reserved for future delivery integration.

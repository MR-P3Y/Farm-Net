# Notification Events

## Foundation status

Implemented in:

```text
Phase 11 - Notifications / Events / Messaging Foundation
```

Current channel:

```text
in_app
```

Future channels:

```text
sms
email
push
telegram
```

## Event Types

```text
order.created
order.status_changed

payment.created
payment.succeeded
payment.failed
payment.receipt_uploaded

verification.submitted
verification.approved
verification.rejected

media.quarantined
media.deleted

store.approved
store.rejected

product.approved
product.rejected

system.message
```

## Implemented Integrations

```text
Orders:
- order.created
- order.status_changed

Payments:
- payment.created
- payment.succeeded
- payment.failed

Verifications:
- verification.submitted
- verification.approved
- verification.rejected

Media:
- media.quarantined
- media.deleted

Admin:
- system.message
```

## Defined but not fully wired yet

```text
payment.receipt_uploaded
store.approved
store.rejected
product.approved
product.rejected
```

## Rule

Application modules must not insert notifications directly.

They must use:

```text
NotificationService
```

Core methods:

```text
create_event
notify_user
notify_many
create_system_message
create_event_and_notify_user
create_event_and_notify_many
```

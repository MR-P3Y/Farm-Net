# Farm Net Notifications API

## Purpose

Notifications provides an in-app inbox plus user-controlled channel routing.

Default channel:

```text
in_app
```

Opt-in queued channels (verified destination required):

```text
sms
email
```

Reserved destination integrations:

```text
push
telegram
```

## Core Concepts

### Notification Event

A notification event records what happened in the system.

Examples:

```text
order.created
order.status_changed
payment.succeeded
verification.approved
media.quarantined
system.message
```

### Notification

A notification is the message shown to a recipient user.

Each notification has:

```text
recipient_user_id
channel
title
body
action_url
priority
status
```

### Delivery Log

Delivery logs track channel delivery state.

For now, `in_app` delivery is marked as `sent`.

---

## Event Types

Supported event types:

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

expert_answer_created

system.message
```

Note:

```text
payment.receipt_uploaded is defined but currently skipped if no card-to-card receipt upload flow exists.
```

---

## Statuses

Notification statuses:

```text
unread
read
archived
deleted
```

Only non-deleted notifications are returned in the normal user inbox.

---

## Priorities

```text
low
normal
high
urgent
```

---

## User APIs

### List my explicit preferences

```http
GET /api/v1/notifications/preferences
```

The list contains saved overrides. With no override, `in_app` is enabled and
all external channels are disabled.

### Set a preference

```http
PUT /api/v1/notifications/preferences
```

```json
{
  "event_type": "*",
  "channel": "email",
  "is_enabled": true
}
```

Use `*` for a global channel preference or a real notification event type for
an override. Event-specific settings take precedence. Email and SMS route only
to verified AuthUser destinations. Push and Telegram settings can be stored but
do not route until their destination registries exist.

System messages remain mandatory in-app messages and bypass user routing.

---

### List my notifications

```http
GET /api/v1/notifications/me
```

Required permission:

```text
notifications.read
```

Query parameters:

| Name      | Type   | Description          |
| --------- | ------ | -------------------- |
| page      | int    | Default 1            |
| page_size | int    | Default 20, max 100  |
| status    | string | unread/read/archived |
| channel   | string | Default in_app       |

Response:

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "event_id": 1,
      "recipient_user_id": 2,
      "channel": "in_app",
      "title": "سفارش شما ثبت شد",
      "body": "سفارش شماره 15 با موفقیت ثبت شد.",
      "action_url": "/orders/15",
      "priority": "normal",
      "status": "unread",
      "read_at": null,
      "created_at": "...",
      "updated_at": "...",
      "deleted_at": null
    }
  ],
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 1,
    "total_pages": 1,
    "trace_id": "..."
  }
}
```

---

### My unread count

```http
GET /api/v1/notifications/me/unread-count
```

Required permission:

```text
notifications.read
```

Response:

```json
{
  "success": true,
  "data": {
    "unread_count": 3
  }
}
```

---

### Mark notification as read

```http
PATCH /api/v1/notifications/{notification_id}/read
```

Required permission:

```text
notifications.manage
```

Rules:

```text
Only owner can mark own notification as read.
Non-owner access returns not found style validation error.
```

---

### Mark all as read

```http
PATCH /api/v1/notifications/read-all
```

Required permission:

```text
notifications.manage
```

Response:

```json
{
  "success": true,
  "data": {
    "updated_count": 4
  }
}
```

---

### Delete notification

```http
DELETE /api/v1/notifications/{notification_id}
```

Required permission:

```text
notifications.manage
```

This is a soft delete.

---

## Admin APIs

### List notifications

```http
GET /api/v1/admin/notifications
```

Required permission:

```text
notifications.admin_read
```

Query parameters:

| Name              | Type   | Description                    |
| ----------------- | ------ | ------------------------------ |
| page              | int    | Default 1                      |
| page_size         | int    | Default 20, max 100            |
| status            | string | unread/read/archived/deleted   |
| channel           | string | in_app/sms/email/push/telegram |
| recipient_user_id | int    | Filter by recipient            |

---

### Get notification detail

```http
GET /api/v1/admin/notifications/{notification_id}
```

Required permission:

```text
notifications.admin_read
```

---

### Create system message

```http
POST /api/v1/admin/notifications/system-message
```

Required permission:

```text
notifications.system_message
```

Body:

```json
{
  "recipient_user_id": 2,
  "title": "پیام سیستمی",
  "body": "متن پیام سیستمی",
  "action_url": "/notifications",
  "priority": "normal"
}
```

Rules:

```text
Current MVP supports sending system message to one specific user.
Mass/broadcast send is intentionally not enabled yet.
```

### Delivery operations

```http
GET  /api/v1/admin/notifications/deliveries
GET  /api/v1/admin/notifications/deliveries/{delivery_log_id}
POST /api/v1/admin/notifications/deliveries/{delivery_log_id}/retry
```

Read operations require `notifications.admin_read`; retry requires
`notifications.admin_manage`. Detail includes the ordered, immutable attempt
history. Manual retry is rejected for in-app, processing, sent, or delivered
records.

Workers claim ready external deliveries using row locks with `SKIP LOCKED`.
Each claim creates a monotonically numbered attempt and a time-limited lease.
Retryable failures return to `pending` with capped exponential backoff; reaching
`max_attempts` produces terminal `failed`. An expired lease closes the abandoned
attempt as failed before a new claim.

---

## Integrated Events

### Orders

Emitted events:

```text
order.created
order.status_changed
```

Target:

```text
order owner / customer user
```

Typical action URL:

```text
/orders/{order_id}
```

---

### Payments

Emitted events:

```text
payment.created
payment.succeeded
payment.failed
```

Defined but currently skipped if flow does not exist:

```text
payment.receipt_uploaded
```

Target:

```text
payment/order owner
```

Typical action URL:

```text
/orders/{order_id}
```

---

### Verifications / User Documents

Emitted events:

```text
verification.submitted
verification.approved
verification.rejected
```

Target:

```text
document owner
```

Typical action URL:

```text
/verification
```

---

### Expert Answers

Emitted event:

```text
expert_answer_created
```

Target:

```text
social post owner
```

Typical action URL:

```text
/social/posts/{post_id}
```

Rules:

```text
Only published expert answers emit this event.
No notification is emitted when the expert/admin is also the post owner.
Hide/delete/republish moderation does not emit duplicate expert answer notifications.
The notifications API currently exposes event_id on notifications, but it does not provide an event_type query filter.
```

---

### Media

Emitted events:

```text
media.quarantined
media.deleted
```

Target:

```text
media owner
```

Typical action URL:

```text
/media
```

---

## Permissions

```text
notifications.read
notifications.manage
notifications.admin_read
notifications.admin_manage
notifications.system_message
```

Role mapping:

```text
user: read/manage
shop_owner: read/manage
consultant: read/manage
lessor: read/manage
support: read/manage/admin_read
admin: all 5
super_admin: all 5
```

---

## Security Notes

* Users can only access their own notifications.
* Non-owner notification access does not expose existence.
* Admin access is permission-protected.
* System messages require explicit permission.
* Broadcast/mass messaging is intentionally not enabled in this foundation.
* Email/SMS preferences create pending delivery work only for verified contact
  details; real providers are not connected yet.
* Admin retry only schedules work; it never calls a provider synchronously.

## Email Worker

Email delivery is processed out of request scope:

```powershell
python scripts/process_email_notifications.py --limit 50
```

The command is fail-closed. Unless `EMAIL_ENABLED=true`, provider is `smtp`,
and host/from are configured, it returns `disabled=true` without claiming any
queue row. SMTP credentials must be supplied only through runtime environment.

## SMS Worker

```powershell
python scripts/process_sms_notifications.py --limit 50
```

SMS is also fail-closed and requires explicit enablement, `http_json`, an HTTPS
API URL, API key, and sender. It processes only SMS queue rows and never exposes
credentials in output.

## Push Devices and Worker

```http
POST   /api/v1/notifications/devices
DELETE /api/v1/notifications/devices/{device_id}
```

Registration accepts `{token, platform}` where platform is android, ios, or
web. Token values are never returned. Push routing requires an active device.
The fail-closed worker is:

```powershell
python scripts/process_push_notifications.py --limit 50
```

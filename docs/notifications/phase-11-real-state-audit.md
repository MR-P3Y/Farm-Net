# Phase 11 Notifications Real-State Audit

Audit date: 2026-07-17
Scope: Step 11.1, read-only implementation audit

## Executive Result

Farm-Net already has a usable in-app notification foundation. It is not yet a
multi-channel delivery system. Email, SMS, push, and Telegram are enum/config
placeholders with pending delivery rows; no dispatcher, provider adapter,
retry worker, device-token registry, or user delivery preference exists.

## Implemented Contracts

### Database

- `notification_events` stores a unique event key, type, actor, source, and
  payload.
- `notifications` stores recipient, channel, content, action URL, priority,
  read state, and soft deletion.
- `notification_delivery_logs` stores channel/provider state and provider
  message identifiers.
- Event keys are unique and provider message IDs are unique per provider.
- Recipient/status/date and recipient/channel/date list indexes exist.

### Backend and permissions

- User list, unread count, mark-one read, mark-all read, and soft-delete APIs
  enforce recipient ownership.
- Admin list/detail and targeted system-message APIs are permission protected.
- `NotificationService` is used by Orders, Payments, Verification, Media,
  Weather, Social, Expert, Consultants, and Services producers.
- Services request events use stable keys, remove the actor from recipient
  lists, and reuse an existing in-app notification at service level.

### Clients

- Mobile has typed list/read/read-all/delete APIs, inbox state, unread badge,
  loading/error/empty handling, and notification navigation.
- Admin has typed list/detail/system-message APIs and notification operations
  UI.
- Notification API and Postman documentation already exist.

## Exact Gaps and Risks

### P0 contract gaps for Step 11.2

1. `notifications` has no database uniqueness constraint for
   `(event_id, recipient_user_id, channel)`. The current check-then-insert can
   duplicate under concurrent requests.
2. Stable producer idempotency is inconsistent. Services and Expert provide
   deterministic event keys, while most producers rely on generated random
   keys.
3. Self-notification has no platform policy. Some flows intentionally notify
   the actor (order/payment and verification submission), while Services and
   Social suppress it locally.
4. Non-in-app delivery logs remain `pending`; no process owns their lifecycle.
5. Delivery logs have no attempt number, retry schedule, lock/lease fields, or
   terminal failure contract.

### Deferred delivery gaps

- No user channel preferences, opt-in/opt-out rules, quiet hours, locale, or
  per-event routing.
- No email, SMS, push, or Telegram provider adapter.
- No push device-token/subscription model.
- No retry queue/worker, backoff policy, dead-letter workflow, or operator
  replay action.
- No provider webhook/delivery-receipt ingestion.
- Admin APIs do not expose delivery attempts or operational retry state.
- No standalone notification contract test suite; current notification tests
  are primarily embedded in Services workflow coverage.

## Step 11.2 Boundary

Step 11.2 should harden provider-neutral delivery contracts without connecting
or claiming a real external provider:

1. Add database-enforced exact-once notification identity.
2. Define deterministic event-key requirements and update active producers.
3. Define explicit self-notification policy with allow/suppress behavior.
4. Add durable delivery attempt/retry lifecycle fields and transition rules.
5. Add focused concurrency, idempotency, ownership, and migration tests.
6. Preserve all current API, Mobile, and Admin behavior unless a contract fix
   requires a backward-compatible field addition.

Preferences/routing belong to Step 11.3; queue execution and retry operations
to 11.4; actual email, SMS, and push adapters to 11.5 through 11.7.

## Step 11.1 Closure Criteria

- Existing DB/API/client contracts identified from source: OK
- Producers and event-key behavior audited: OK
- Self-notification behavior classified: OK
- Provider and retry implementation status verified: OK
- Risks separated from later provider work: OK
- Step 11.2 scope defined without adding features: OK

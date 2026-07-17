# Phase 11.6 SMS Provider Foundation

Completion date: 2026-07-18

## Implemented

- Provider-neutral SMS message and transport contracts.
- Configurable HTTPS JSON adapter with Bearer authentication.
- Verified-phone recheck, safe action URL filtering, and 480-character cap.
- Queue claim, attempt history, success ID, retryable network/429/timeout
  failures, and terminal non-retryable 4xx failures.
- Fail-closed one-batch CLI worker:
  `python scripts/process_sms_notifications.py --limit 50`.

## Configuration

```text
SMS_ENABLED=false
SMS_PROVIDER=http_json
SMS_API_URL=
SMS_API_KEY=
SMS_SENDER=
SMS_TIMEOUT_SECONDS=15
```

The adapter requires an HTTPS endpoint. API credentials are runtime secrets.
Provider-specific request/response mapping may be added after a vendor is
selected; the current generic response accepts `message_id` or `id`.

## Verification

- Backend Ruff and compileall: OK.
- Full Backend suite: 46 passed with 16 existing UTC warnings.
- Fake-transport verified-phone delivery and safe rendering: OK.
- Docker disabled runtime: zero claimed/sent, `disabled=true`.
- No real SMS request or credential was used.

## Deferred

- Vendor-specific adapter and delivery receipt webhook.
- Production sender registration and credential provisioning.
- Push Notification Foundation: Step 11.7.

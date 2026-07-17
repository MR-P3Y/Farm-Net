# Phase 11.5 Email Provider Foundation

Completion date: 2026-07-18

## Implemented

- Provider-neutral Email envelope with plain-text and escaped HTML alternatives.
- SMTP transport using the Python standard library.
- Configurable STARTTLS or implicit SSL, authentication, timeout, and sender.
- Email-only dispatcher integrated with queue claim, success, retryable failure,
  terminal recipient rejection, provider message ID, and attempt history.
- Verified recipient Email is checked again at dispatch time.
- One-batch CLI worker: `python scripts/process_email_notifications.py`.
- Fail-closed activation: the worker does not claim work unless Email is
  explicitly enabled and required SMTP settings are complete.

## Configuration

```text
EMAIL_ENABLED=false
EMAIL_PROVIDER=smtp
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_USER=
EMAIL_PASSWORD=
EMAIL_FROM=
EMAIL_STARTTLS=true
EMAIL_USE_SSL=false
EMAIL_TIMEOUT_SECONDS=15
```

STARTTLS and implicit SSL cannot both be enabled. Credentials remain runtime
secrets and must never be committed.

## Verification

- Backend Ruff and compileall: OK.
- Full Backend suite: 43 passed with 16 existing UTC deprecation warnings.
- HTML escaping and verified-recipient dispatch: OK.
- Disabled configuration claims zero deliveries: OK in Docker runtime.
- Runtime health application/database/Redis: OK.

No live SMTP credentials were supplied and no real Email was sent. Scheduling
or supervising the one-batch worker belongs to deployment hardening.

## Deferred

- Provider-specific webhook/delivery receipt handling.
- Production credential provisioning and deliverability setup (SPF/DKIM/DMARC).
- SMS Provider Foundation: Step 11.6.

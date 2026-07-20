# Phase 20.11 Financial Notifications, Privacy and Audit Hardening

## Events and Ownership

Refund requested/completed goes only to the invoice buyer. Settlement lifecycle
goes only to the requesting provider. Wallet Adjustment goes only to the
affected wallet owner. Events use existing preferences, delivery logs and
event-key duplicate prevention.

## Privacy Contract

Payloads contain only safe owned-resource IDs, state, direction and `TOMAN`
currency. A recursive guard rejects Merchant ID, Authority, card PAN/hash,
tokens/secrets, idempotency keys, provider references, raw Callback/Verify
payloads, reasons and Admin notes. Settlement and Adjustment notification
payloads omit amount.

## Audit Contract

Settlement decision and simulated clearing actions store exact-once Admin Audit
records with actor, target, state, IP, user agent and trace. Audit does not copy
Admin notes or gateway secrets. Refund completion Audit no longer copies the
provider reference.

## Boundary

External Email/SMS/Push transports retain their existing disabled-by-default
configuration. This step does not claim production delivery or bank settlement.

## Verification

- Ruff and Python compileall: passed.
- Focused financial notification/privacy regression: 45 passed.
- Full Backend regression: 128 passed, 17 existing UTC warnings.
- Alembic: `fdcb2ab80c12 (head)`; no schema change required.
- Runtime health: app/database/Redis all `ok`.
- OpenAPI: 249 paths.
- Notification Postman: valid JSON, 21 requests.

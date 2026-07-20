# Phase 20.10 Zarinpal Gateway Adapter and Callback Verification

## Provider Contract

The adapter implements Zarinpal payment v4 Request and Verify. Project money is
canonical `TOMAN`; the provider request explicitly uses `currency=IRT`, so no
implicit rial conversion occurs. Request success requires code 100 and an
Authority. Verify accepts code 100 and code 101, which Zarinpal defines as an
already-verified successful transaction.

Official references:

- https://www.zarinpal.com/docs/paymentGateway/connectToGateway
- https://www.zarinpal.com/docs/paymentGateway/sandBox
- https://www.zarinpal.com/docs/paymentGateway/moreFeatures/currency

## Security and Idempotency

- Adapter is disabled by default.
- Merchant ID is environment-only and is not persisted or returned.
- Provider endpoints are fixed HTTPS Zarinpal hosts; callers cannot supply a
  URL, preventing SSRF through gateway configuration.
- Callback `OK` is not proof of payment. Authority must match a locked attempt,
  then Verify runs server-to-server with the stored amount.
- Existing successful attempts return exact-once without another Ledger entry.
- Request uses `metadata.auto_verify=false`, keeping Farm-Net in control of the
  final state transition.
- Network failures remain retryable; terminal provider rejection is recorded.

## Configuration

```text
PAYMENT_GATEWAY_ENABLED=false
PAYMENT_GATEWAY=zarinpal
PAYMENT_MERCHANT_ID=
PAYMENT_CALLBACK_BASE_URL=https://example.com/api/v1/payments/callback/zarinpal
PAYMENT_ZARINPAL_SANDBOX=true
PAYMENT_GATEWAY_TIMEOUT_SECONDS=15
```

## Operational Boundary

No Merchant ID was available during implementation. Unit/contract validation
uses injected provider responses; it does not claim an actual Sandbox or bank
transaction. Credentialed Sandbox smoke and production activation require an
approved Merchant ID, public HTTPS callback, provider panel configuration, and
operational authorization.

## Verification

- Ruff and Python compileall: passed.
- Full Backend regression: 119 passed, 17 existing UTC warnings.
- Alembic: `fdcb2ab80c12 (head)`; no schema change required.
- Runtime: app/database/Redis `ok`; Gateway disabled; Merchant absent; Sandbox
  mode selected.
- OpenAPI: 249 paths; public Zarinpal Callback registered.
- Postman: valid JSON, 44 requests including Checkout and Callback examples.
- Credentialed Sandbox smoke: skipped because no Merchant ID/public HTTPS
  callback was supplied; exact reason recorded rather than claiming payment.

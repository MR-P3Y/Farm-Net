# Step 22.10 — Credentialed Staging Provider Verification

Status: blocked on external provisioning
Last audited: 2026-07-25

## Safe gate implemented

`backend/scripts/verify_staging_providers.py` provides a redacted verification
gate for Email, SMS, Push, and Zarinpal. It has two modes:

- preflight validates enabled-provider configuration without delivery;
- execute performs an external staging operation only when `APP_ENV=staging`,
  the exact confirmation phrase is supplied, and a provider-specific test
  destination exists outside Git.

The script prints only provider, mode, status, stable code, and timestamp. It
never prints credentials, recipient/token values, response bodies, provider
IDs, URLs, or exception messages. `--require-verified` returns non-zero unless
every selected provider received external acceptance.

Execution command after secure provisioning:

```powershell
backend\.venv\Scripts\python.exe backend\scripts\verify_staging_providers.py `
  --provider all `
  --execute `
  --confirm LIVE-STAGING-DELIVERY `
  --require-verified
```

`infra/staging-providers.env.example` lists non-secret switches and required
fields. Real values must be supplied through the staging secret manager or
ignored external files.

## Actual environment audit

The repository and current local environment were inspected without printing
values:

| Provider | Enabled | Credential | Test destination | External result |
|---|---:|---:|---:|---|
| SMTP Email | No | No | No | Not attempted |
| HTTP JSON SMS | No | No | No | Not attempted |
| HTTP JSON Push | No | No | No | Not attempted |
| Zarinpal | No | No merchant | N/A | Not attempted |

The real preflight returned `PROVIDER_DISABLED` for all four providers. This is
the correct safe result and is not a successful credentialed verification.

## Required provisioning decisions

### Email

- staging SMTP hostname/port and TLS mode;
- authenticated user/password file when required;
- verified sender and owner-approved staging recipient;
- provider-side sender/domain configuration.

### SMS

- selected Iranian SMS vendor, staging endpoint/key/sender, and owner-approved
  test number;
- confirmation that the vendor accepts the current Bearer-auth JSON contract
  and returns `message_id` or `id`;
- otherwise a vendor-specific adapter and contract tests are required before
  delivery.

### Push

- selected Push vendor, staging endpoint/key, and disposable test-device token;
- confirmation that the vendor accepts the current multi-token Bearer-auth JSON
  contract and returns `message_id` or `id`;
- otherwise a vendor-specific adapter is required.

### Zarinpal

- sandbox merchant ID delivered through `PAYMENT_MERCHANT_ID_FILE`;
- reachable HTTPS staging callback;
- sandbox must remain enabled;
- the gate requests exactly `1000` whole toman (`IRT`) and does not verify or
  settle a payment without the returned authority and explicit user action.

## Completion gate

Step 22.10 must remain open until all selected production providers have:

1. valid staging configuration and secrets outside Git;
2. an owner-approved test destination;
3. successful `--execute --require-verified` output;
4. provider dashboard/delivery evidence where applicable;
5. no secret or personal destination in logs, artifacts, shell history, or
   Git;
6. a clean post-verification Backend regression and staging health result.

Current code-level evidence: 31 focused provider/payment tests passed, all 226
Backend tests passed, and the
redacted disabled-mode preflight behaved correctly. This is preparation, not
credentialed provider acceptance.

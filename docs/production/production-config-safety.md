# Phase 22.3 — Production Configuration, Secret + Dev-Switch Safety

Date: 2026-07-24

## Outcome

Farm-Net now validates runtime configuration before application startup.
Development/test retain their current defaults. Staging and production fail
closed with safe error codes when security-critical configuration is missing
or unsafe; validation messages never include secret values.

Run the same gate used by startup:

```powershell
py -3 backend\scripts\validate_runtime_config.py
```

The command prints only non-secret readiness metadata: environment/version,
boolean provider switches, origin/proxy counts, rate-limit state, and whether
the media path is absolute.

## Production-like requirements

Both `staging` and `production` require:

- `APP_DEBUG=false`;
- `AUTH_DEV_OTP_ENABLED=false`;
- a non-placeholder JWT secret of at least 32 characters;
- a non-default Super Admin identity and password of at least 12 characters;
- HTTPS public, Admin, and Media base URLs;
- explicit HTTPS CORS origins with no wildcard;
- enabled rate limiting;
- non-placeholder database credentials;
- authenticated Redis URL;
- an absolute Media storage path.

Production additionally rejects an enabled Zarinpal sandbox.

## Enabled-provider requirements

Disabled providers remain valid and fail closed as before. Once an operator
sets a provider to enabled, startup requires its complete safe contract:

- Email: supported SMTP provider, host/from, and TLS or SSL;
- SMS: supported HTTP JSON provider, HTTPS URL, API key, and sender;
- Push: supported HTTP JSON provider, HTTPS URL, and API key;
- Payment: Zarinpal, a 36-character Merchant ID, and HTTPS callback.

This validation does not claim provider connectivity. Credentialed staging
network verification remains Step 22.10.

## OTP hardening

When Dev OTP is enabled, the explicit development code remains available for
local workflows. When it is disabled, the former static fallback is removed
and a six-digit code is generated with Python's cryptographic random source.
The code is not returned in the API response.

Real OTP delivery is not yet connected to the SMS provider. Operators must not
claim production phone-login readiness until the credentialed OTP delivery
path is implemented and verified in Step 22.10. Email/password authentication
remains independent.

## Media configuration alignment

`MEDIA_STORAGE_DIR` is now the single Backend setting used by local Media
storage. The old `.env.example` `STORAGE_PATH` name was unused and has been
replaced. Production-like environments require an absolute path; persistence,
permissions, backup, and restore remain Step 22.4/22.8 concerns.

## Verified boundaries

- Development defaults pass runtime validation.
- Unsafe production defaults fail with stable codes and no secret echo.
- A complete production configuration contract passes unit validation.
- Incomplete/insecure enabled providers fail closed.
- Production payment sandbox is rejected.
- Disabled Dev OTP uses the cryptographic random source.
- Ruff, compileall, and all 193 Backend tests pass.
- Local Docker development health remains app/database/Redis `ok`.

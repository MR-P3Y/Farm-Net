# Phase 21.7 — Barzegar Model Gateway, Prompt/Policy Registry + Routing

Verified: 2026-07-27  
Branch: `develop`  
Alembic head: `g21c4a18d6e5`

## Implemented boundary

- Added a Provider-neutral gateway and an OpenAI Responses API adapter.
- Provider credentials remain server-side in ignored environment configuration;
  no secret is stored in MySQL, request rows, logs, or response contracts.
- Added immutable/versioned registries for:
  - six Barzegar prompt/policy variants;
  - three enabled model configurations;
  - six feature/request routing policies.
- Every new request pins both `prompt_policy_version` and
  `routing_policy_version`; worker attempts retain the chosen model
  configuration and route version.
- Active routes are unique per `feature_code:request_kind`.
- Fallback is bounded to one alternate model and occurs only for transient
  Provider/network failures. Invalid requests, missing quota, invalid keys,
  unsupported values, and missing models do not trigger fallback.

## Initial routing

| Feature | Primary | Transient fallback |
|---|---|---|
| text chat | `gpt-5.6-luna` | `gpt-5.6-terra` |
| selected Farm context | `gpt-5.6-terra` | `gpt-5.6-sol` |
| deep analysis | `gpt-5.6-terra` | `gpt-5.6-sol` |
| image analysis | `gpt-5.6-terra` | `gpt-5.6-sol` |
| smart diary | `gpt-5.6-luna` | `gpt-5.6-terra` |
| report | `gpt-5.6-terra` | `gpt-5.6-sol` |

This preserves a cost/latency/quality hierarchy instead of sending every farmer
request to the most expensive model. The values are versioned configuration,
not client-controlled model selection.

## Prompt and privacy policy

The activated `barzegar-v1` policy:

- answers in clear Persian;
- treats retrieved and Farm free text as untrusted data;
- requires uncertainty and missing-context disclosure;
- forbids guaranteed diagnosis;
- blocks unsupported high-risk chemical prescriptions;
- prevents disclosure of system instructions, secrets, and context outside the
  selected Farm scope.

The gateway sends `store=false` and a stable privacy-preserving hashed
`safety_identifier`. Raw Provider error bodies and credentials are not exposed
through domain errors.

## Verification

- Ruff: passed.
- compileall: passed.
- Backend tests: `353 passed`.
- focused gateway/registry/routing tests: passed.
- Alembic upgrade: passed at `g21c4a18d6e5`.
- runtime registry: 3 models, 6 prompts, 6 routes.
- app/database/Redis health: OK.
- real OpenAI network/auth path: reached the Responses API.

## Deferred operational activation

The live content smoke returned:

```text
HTTP 429
error_type: insufficient_quota
error_code: insufficient_quota
```

The key and network path are configured, but the selected OpenAI Platform
project currently has no usable API quota/credit. The project owner explicitly
approved closing Step 21.7 without Billing activation because an international
payment card is not currently available.

This is an operational activation gap, not an untested code path: Provider
success, response parsing, token usage, transient/permanent failures, and
fallback behavior are covered with deterministic HTTP mocks. Production
activation remains disabled by `AI_PROVIDER_ENABLED=false`.

After quota becomes available, enable the Provider only in the target
environment and rerun the minimal live smoke before serving real users.
Step 21.8 Subscription Quota, Technical Usage/Cost + Reconciliation is next.

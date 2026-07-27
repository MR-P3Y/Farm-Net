# Phase 21.13 — Admin Knowledge, Runs, Feedback + Safety Operations

Status: completed

## Backend

Ten permission-scoped Admin Barzegar paths now cover:

- operational overview and reconciliation issue count;
- privacy-safe request/run metadata;
- technical token, latency, Provider model, and TOMAN cost usage;
- user feedback;
- governed knowledge source list/create/submit/review;
- safe audit events;
- prompt-policy registry metadata;
- Provider/model registry metadata without credentials.

Admin request contracts intentionally exclude message content, selected-Farm
context manifests, request fingerprints, and idempotency keys. Model contracts
never expose an API key or secret reference.

Knowledge sources follow the enforced lifecycle:

`draft -> in_review -> approved | rejected`

Creation, submission, approval, and rejection are audited. Review requires a
reason and the reviewing Admin identity.

## Admin Flutter

The permission-protected `/ai` page and sidebar entry provide:

- overview cards for request state, safety blocks, negative feedback,
  reconciliation issues, pending sources, and Provider cost in TOMAN;
- privacy-safe run monitoring;
- governed knowledge source create/submit/approve/reject actions;
- technical usage rows;
- prompt policy registry status.

## Verification

- Backend Ruff and compileall: passed
- Backend tests: 372 passed
- Admin analyze: passed
- Admin tests: 30 passed
- Admin Web build and Wasm dry run: passed
- Runtime health: app/database/Redis OK
- OpenAPI: 10 Admin Barzegar paths
- No schema migration was required.

Next: Step 21.14 Evaluation, Observability, Abuse + Concurrency Hardening.

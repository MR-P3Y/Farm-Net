# Phase 25.11 — Docs, Postman + Runtime Regression

Status: complete.

## Delivered

- `docs/api/billing.md` is the canonical Phase 25 API and lifecycle contract.
- `postman/collections/subscriptions.postman_collection.json` contains 30
  requests: every one of the 23 runtime Billing operations plus seven focused
  authentication, permission, privacy, validation, and replay cases.
- Automated contract tests prove that collection bodies remain valid JSON
  after variable resolution, obvious secrets are absent, and every runtime
  operation is represented.
- Legacy roadmap, database, permission, and Postman indexes now point to the
  deployed ten-table and 15-permission implementation.

## Read-only Runtime Regression

Against the current development stack:

```text
public plans: 1; active plan detail: free
owner current subscription: present
owner entitlements: 15; owner usage rows: 5
Admin plans: 1; Admin subscriptions: 2; Audit rows: 0
reconciliation: clean; issues: 0
unauthenticated owner request: 401
unknown callback authority: 404
OpenAPI Billing paths: 22; operations: 23
health: app ok; database ok; redis ok
```

The Audit count of zero is expected: Audit is intentionally append-only from
migration `e17c4b82a6d9` onward and no lifecycle transition has occurred since
that migration. Historical events were not fabricated.

The reconciliation CLI independently checked 2 Subscriptions, 2 Periods, 30
Entitlements, 10 Usage rows, and zero Payment Attempts. It reported a clean
state with zero issues.

## Execution Boundary

The full state-changing Postman sequence was not run against the shared
development database because it creates plans, subscriptions, payment state,
and cancellations. Those mutation and replay contracts are covered by the
Backend automated tests; end-to-end Postman mutation execution belongs in an
isolated non-production database with synthetic users and mock payment only.

Mobile and Admin Flutter validation was not repeated in this documentation-only
step because no client source was changed. Admin analyze, tests, and web build
passed in Step 25.10. Concurrent owner-authored Mobile changes remained
untouched and outside this step.

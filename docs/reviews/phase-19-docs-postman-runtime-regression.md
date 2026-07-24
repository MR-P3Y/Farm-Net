# Phase 19 — Step 19.10 Docs, Postman + Runtime Regression

Date: 2026-07-24

Branch: `develop`

Baseline commit: `cd9eabf`

## Scope

This step adds no Review feature, migration, permission, Mobile behavior, Admin
behavior, or API route. It consolidates the final Phase 19 documentation,
brings the Review Postman metadata up to the implemented contract, and adds a
reusable read-only Runtime regression.

## Documentation and Postman

- The Review API documentation now includes the exact regression command and
  its non-mutating boundary.
- The Postman collection describes the complete owner, public, reporting,
  Admin moderation, and audit-log surface.
- `review_report_id` replaces the hard-coded report ID in the Admin resolution
  request.
- The Review collection contains 12 requests covering every implemented
  operation.

## Runtime regression

Run:

```powershell
py -3 backend\scripts\reviews_runtime_regression.py --base-url http://localhost:8000
```

The script verifies:

- app/database/Redis health;
- all ten Review OpenAPI path groups and their methods;
- seven Review subject types and four source types;
- owner, public, and Admin typed response references;
- the privacy-minimized public Review schema;
- seven unauthenticated owner/Admin boundaries;
- the public missing-subject 404 contract;
- zero successful mutations.

## Verified results

| Area | Result |
| --- | --- |
| Backend Ruff / compileall | OK |
| Backend pytest | OK — 186 passed; 18 known warnings |
| Alembic | OK — `a7c9e1f30d13 (head)` |
| Auth seed idempotency | OK — two runs; 12 roles / 257 permissions |
| Health | OK — app, database, Redis |
| OpenAPI | OK — 264 paths / ten Review paths |
| Runtime Review regression | OK — ten contracts / zero mutations |
| Privacy | OK — six-field public Review and display-name-only author |
| Mobile | OK — analyze, 54 tests, Web/Wasm build |
| Admin | OK — analyze, 20 tests, Web/Wasm build |
| Review Postman | OK — 12 requests |
| All Postman | OK — 14 collections / 325 requests / 130 raw bodies |

## Runtime data boundary

The regression does not fabricate a delivered/completed source, Review, report,
or moderation event. It proves the live public missing-subject boundary and
unauthenticated private routes. Populated eligibility, exact-once aggregate,
notification, and moderation behavior remains covered by focused Backend
tests and the earlier rollback-only Runtime smoke.

## Conclusion

Step 19.10 passes. Phase 19 implementation and documentation are complete and
may proceed to Step 19.11 Release Gate + Tag only after a fresh clean-tree,
upstream, full verification, and tag audit.

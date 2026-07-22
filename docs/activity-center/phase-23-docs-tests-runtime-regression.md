# Phase 23.10 — Docs, Tests, and Runtime Regression

Date: 2026-07-22

Branch: `develop`

Baseline commit: `0ca385b`

## Delivered scope

The Mobile `/activity` route is the authenticated, role-aware entry point for
personal activity and professional work. It derives visible destinations from
the signed-in user's typed roles and permissions; every destination API retains
its own Backend authorization as the final authority.

Personal activity covers identity/Profile, Verification, Notifications,
Finance, Buyer Orders, and the user's Service, Rental, and Consultation
requests. Professional sections cover Shop Owner Store/Products/Seller Orders,
Service Provider Profile/Offers/assigned requests, Lessor Profile/Equipment/
assigned requests, and Consultant Profile/assigned requests. Multi-role users
receive independent ordered sections without role switching or permission
merging.

This step adds no API, database, Mobile workflow, or Admin behavior. It adds a
reusable read-only Runtime regression script and consolidates verification.

## Verified results

| Area | Result |
| --- | --- |
| Backend Ruff / compileall | OK |
| Backend pytest | OK — 164 passed; 18 known warnings |
| Alembic | OK — `fdcb2ab80c12 (head)` |
| Auth seed idempotency | OK — two runs; 12 roles / 249 permissions |
| Runtime health | OK — app, database, Redis |
| OpenAPI | OK — 254 paths; 16 Activity Center contract groups |
| Private auth boundary | OK — nine representative unauthenticated reads return 401 |
| Runtime mutations | None |
| Mobile | OK — analyze, 52 tests, Web/Wasm build |
| Admin | OK — analyze, 17 tests, Web/Wasm build |
| Postman | OK — 13 collections / 313 requests / 125 normalized raw JSON bodies |

## Runtime command

From `backend`:

```powershell
.\.venv\Scripts\python.exe scripts\activity_center_runtime_regression.py
```

The script verifies health, required OpenAPI methods, and unauthenticated
privacy boundaries. It performs zero mutations and requires no credentials.

## Explicit boundary

The Runtime environment has no authenticated fixture matrix for all four
professional roles. Therefore this step does not claim live authenticated
Seller/Provider/Lessor/Consultant mutations. Typed Mobile tests, Backend tests,
OpenAPI method checks, and 401 privacy checks cover the available deterministic
contract boundary. Production external notification and payment providers
remain outside Phase 23.

## Conclusion

Step 23.10 passes. Phase 23 may proceed to Step 23.11 Release Gate + Tag after
an independent clean-tree/upstream audit and complete release verification.

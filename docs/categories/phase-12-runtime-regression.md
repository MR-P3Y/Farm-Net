# Phase 12.7 — Category Management Docs/Postman + Runtime Regression

## Scope

This regression reconciles the implemented Product, Services, Social, and
Consultant taxonomy contracts. The four domains remain independent; this step
does not merge their tables, change API behavior, or introduce new business
categories.

## Contract inventory

| Domain | Public discovery | Admin management | Runtime reference rows |
|---|---|---|---:|
| Product | `/api/v1/public/product-categories` | `/api/v1/admin/products/categories` | 24 active |
| Services | `/api/v1/services/categories` | `/api/v1/admin/services/categories` | 8 |
| Social | `/api/v1/social/categories` | `/api/v1/admin/social/categories` | 6 |
| Consultants | `/api/v1/consultants/specialties` | `/api/v1/admin/consultants/specialties` | 0 |

All 12 collection/detail taxonomy paths are present in runtime OpenAPI. Admin
contracts provide typed management, search, lifecycle controls, and domain
usage counts. Product and Services additionally support hierarchy governance.

Consultant specialties intentionally remain empty. No authoritative default
specialty taxonomy has been approved, so the project does not invent synthetic
business reference data. Admins can manage specialties through the implemented
contract when that taxonomy is approved.

## Postman validation

The canonical JSON collections parse successfully:

| Collection | Requests |
|---|---:|
| Products | 23 |
| Services | 30 |
| Social + Expert | 22 |
| Consultants | 31 |

Together they cover public discovery and the permission-protected Admin
category/specialty operations used by Phase 12.

## Runtime verification

```text
Backend Ruff: OK
Backend compileall: OK
Backend pytest: 59 passed, 16 existing datetime.utcnow deprecation warnings
Alembic upgrade/current: b27e8d5f64c1 (head)
Auth seed: 12 roles, 221 permissions
Product seed twice: total=24, active=24, created=0, updated=0
Services seed twice: total=8
Social seed twice: total=6
Health: app=ok, database=ok, redis=ok
OpenAPI taxonomy paths: 12/12

Mobile analyze: OK
Mobile tests: 28 passed
Mobile Web build/Wasm dry run: OK

Admin analyze: OK
Admin tests: 12 passed
Admin Web build/Wasm dry run: OK

Postman JSON: OK
```

The repeated seed results confirm the approved Product, Services, and Social
reference seeds are idempotent and non-destructive.

## Result

Step 12.7 is complete. Phase 12.8 is the independent Category Management
release gate and tag; it must reverify clean, pushed Git state before release.

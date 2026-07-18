# Phase 12.6 — Unified Admin Taxonomy Navigation + UX Consistency

## Completed

- Added one permission-aware `مدیریت دسته‌بندی‌ها` entry to the Admin sidebar.
- Added a central taxonomy hub for Products, Services, Consultant specialties,
  and Social categories.
- Each card explains its domain-specific usage and opens the existing typed
  management surface; no database domains were merged.
- Users only see destinations allowed by their actual permission set.
- Added a dedicated Consultant specialties route that opens the correct tab.
- Direct access without taxonomy permissions shows an empty-access state while
  all destination routes retain their existing permission guards.

No Backend API, permission seed, database schema, or Mobile behavior changed.

## Verification

```text
Admin analyze: OK
Admin tests: 12 passed
Admin Web build/Wasm dry run: OK
Unique taxonomy permissions: 4/4
Unique taxonomy destinations: 4/4
```

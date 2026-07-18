# Phase 12.1 — Product Category Management

## Outcome

The existing `product_categories` hierarchy remains domain-owned and is now
manageable without editing seeds or merging unrelated category domains.

- Public active-category discovery API
- Permission-protected Admin list/create/update APIs
- Parent/child hierarchy with cycle and self-parent prevention
- Stable lowercase slug uniqueness
- Search, sort order, active/inactive state
- Product and direct-child usage counters
- Typed Admin Panel management UI
- Postman coverage for all four new operations
- Bootstrap seed creates missing defaults but never overwrites later Admin edits

Destructive delete is intentionally excluded. Deactivation preserves existing
product relationships and enables safe future reorganization.

## Verification

```text
Backend Ruff: OK
Backend compileall: OK
Backend tests: 51 passed
Admin analyze: OK
Admin tests: 8 passed
Admin Web build/Wasm dry run: OK
```

Services categories, consultant specialties, and social categories remain
separate bounded contexts. A later step can align their Admin experience while
preserving their distinct rules.

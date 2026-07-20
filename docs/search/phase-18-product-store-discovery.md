# Phase 18.3 — Product + Store Discovery Hardening

## Outcome

Products and Stores are the first real domain providers connected to the shared
Farm-Net search engine. Existing public endpoints remain available and backward
compatible while exposing hardened optional filters.

## Product discovery

`GET /api/v1/public/products` retains its existing filters and adds:

```text
min_price
max_price
sort = relevance | newest | price_asc | price_desc
```

- Search covers product name, slug, short/full description, and Store name.
- Query and SQL fields use the same Persian/Arabic normalization boundary.
- Category selection includes active descendants, so selecting a parent finds
  products in its active subtree.
- Price filtering is nonnegative, ordered, and canonical `TOMAN` only.
- Explicit relevance uses exact-title, title-prefix, title-contains, then
  secondary-field tiers. Stable featured/newest/id tie-breakers are retained.
- Omitting `sort` preserves the previous featured/newest ordering.

## Store discovery

`GET /api/v1/public/stores` adds:

```text
sort = relevance | newest
```

Search covers Store name, slug, and description with the shared normalizer.
Omitting sort preserves newest-first behavior. Unsupported cross-domain price
or rating sorts fall back to Store relevance inside the unified provider.

## Privacy and compatibility

- Product results still require published, active, non-deleted Product and an
  approved, non-deleted Store.
- Store results still require approved and non-deleted Store rows.
- No draft, rejected, suspended, inactive, deleted, admin-note, owner-only, or
  moderation data becomes searchable.
- Existing response bodies and pagination metadata are unchanged.
- No schema, migration, permission, or seed change was required.

## Verification

- Shared/Product discovery focused tests: 16 passed.
- Full Backend: Ruff and compileall passed; 145 tests passed with 17 existing
  UTC deprecation warnings.
- Mobile: analyze passed; 38 tests passed.
- Runtime: Arabic-variant Product and Store relevance queries returned HTTP 200
  with valid empty paginated responses; no matching public rows existed.
- OpenAPI: Product price/sort and Store sort parameters are present and typed.
- Postman: Product and Store collections remain valid JSON.

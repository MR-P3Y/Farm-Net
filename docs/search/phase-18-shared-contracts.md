# Phase 18.2 — Shared Search Contracts + Persian Query Normalization

## Outcome

Farm-Net now has one central, provider-based search engine boundary. Product,
Store, Service, Rental Equipment, Consultant, and Social Post adapters will be
registered with this engine in later steps. Existing domain routes remain
unchanged until their dedicated hardening steps and the unified API step.

## Shared contracts

- `UnifiedSearchQuery`: normalized query, selected result types, filters, sort,
  and bounded pagination.
- `UnifiedSearchFilters`: shared geo, domain category/specialty IDs, canonical
  `TOMAN` price range, and range validation.
- `UnifiedSearchResult`: typed public result with internal route, optional
  public image/geo/money/rating fields, and nonnegative relevance score.
- `UnifiedSearchGroup`: one domain's typed items and pagination totals.
- `UnifiedSearchResponse`: normalized query, ordered groups, and combined total.
- `SearchProvider`: the single adapter interface implemented by every domain.
- `UnifiedSearchEngine`: provider registration, selected-provider orchestration,
  duplicate-provider rejection, result-type isolation, and grouped aggregation.

## Persian normalization

The canonical normalizer applies Unicode compatibility normalization, removes
diacritics and tatweel, maps Arabic Yeh/Kaf and selected Heh variants to Persian
forms, treats joiners/non-breaking spaces as whitespace, collapses whitespace,
case-folds Latin text, and maps Persian/Arabic digits to ASCII digits.

Examples:

```text
كِشت‌يـار ۱۲۳  -> کشت یار 123
خدمات   كشاورزي -> خدمات کشاورزی
```

This function is deterministic and shared. Domain repositories will adopt it
without weakening their existing publication, approval, activity, deletion,
ownership, or privacy filters.

## Safety boundaries

- Query length is 2–100 characters after normalization.
- Result types must be unique and allow-listed.
- Pagination is bounded to 50 items per group.
- Price filters are nonnegative, ordered, and `TOMAN` only.
- Result routes must be internal absolute paths; external or protocol-relative
  navigation is rejected.
- Price and currency must appear together.
- Unknown request/result fields are rejected.
- A provider cannot return another provider's result type.

## Verification

- Focused Ruff: passed.
- Focused compileall: passed.
- Shared search contracts: 11 tests passed.
- Full Backend regression: 140 tests passed with 17 existing UTC deprecation
  warnings.
- Database/Alembic: not applicable; no schema change.
- Permissions/seed: not applicable; no route or permission change.
- Postman/OpenAPI: not applicable; unified API is owned by Step 18.8.

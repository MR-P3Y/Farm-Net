# Phase 18.4 — Services Discovery Hardening

## Outcome

Approved Service Offers now implement the shared search-provider contract and
can participate in the single Farm-Net search engine. The existing public list
route remains backward compatible and gains optional hardened filters.

## Public contract

`GET /api/v1/services/offers` adds:

```text
min_price
max_price
sort = relevance | newest | price_asc | price_desc | rating
```

Existing query, category, provider, pricing-type, geo, and pagination filters
remain available. Mobile data layers carry the new parameters; the unified
cross-domain Mobile surface remains owned by Step 18.9.

## Search and ranking

- Shared normalization covers Offer title/slug/descriptions, service area,
  province/city names, Provider display name/title, and Category title.
- Relevance tiers exact Offer title, title prefix, title contains, then matches
  in secondary public fields; featured/newest/id provide stable tie-breakers.
- Rating sort uses approved Provider rating and review count.
- Price sort places null negotiable prices after priced Offers.
- Selecting a parent Category includes its active descendant subtree.

## Money and privacy

- Price range is nonnegative, ordered, and canonical `TOMAN` only.
- Negotiable Offers with no amount are excluded by a price range and expose no
  invented price/currency pair in unified results.
- Search still requires approved, active, non-deleted Offer and approved,
  non-deleted Provider. Private contacts, moderation notes, exact coordinates,
  rejected/draft/suspended data, and owner contracts are not exposed.
- No schema, migration, permission, or seed change was required.

## Verification

- Focused shared/Service search tests: 15 passed.
- Backend Ruff/compileall passed; all 149 tests passed with 17 existing UTC
  deprecation warnings.
- Mobile analyze passed; all 38 tests passed.
- Runtime normalized Arabic-variant query with price/rating filters returned
  HTTP 200 and a valid empty page; no matching public row existed.
- Health: application, database, and Redis `ok`.
- OpenAPI: 253 paths; Service price/sort parameters present and typed.
- Services Postman collection JSON: valid.

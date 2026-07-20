# Phase 18.1 — Search/Filters/Discovery Real-State Audit

Date: 2026-07-20

Baseline: `v0.22.0-wallet-settlement-accounting-foundation`

## Result

Farm-Net already has five separate public discovery implementations. Phase 18
must harden and unify them; it must not replace working domain APIs or invent a
search-engine dependency before scale evidence requires one.

## Existing contracts

| Domain | Backend search and filters | Current ordering | Mobile exposure |
| --- | --- | --- | --- |
| Products | `q`, store, category, province, county, city, store type | featured, newest | Search only on the public list; API client supports the other filters |
| Services | `q`, category, provider, pricing type, province, city | featured, newest | Search, category, province/city, pricing type |
| Rentals | `q`, category, province/city, operator mode | newest | Search, category, province/city, operator mode |
| Consultants | `q`, specialty, province/city | featured, rating, review count, newest | Search and specialty; geo filters are not exposed |
| Social | `q`, category, post type | publication time | Category only; Backend search/post type are not exposed |

All public queries retain their existing approval, publication, activity,
visibility, and soft-delete boundaries. Pagination metadata exists in Backend
responses, but several Mobile repositories reduce responses to a plain list.

## Confirmed gaps

- No cross-domain endpoint, typed unified result, or Mobile discovery hub.
- No common query length, trimming, sort, filter, or pagination contract.
- No Persian/Arabic character normalization (`ی/ي`, `ک/ك`), diacritic cleanup,
  whitespace normalization, or normalized searchable field.
- Query matching uses leading-wildcard `LIKE/ILIKE`; there is no MySQL FULLTEXT,
  dedicated search index, relevance score, typo tolerance, or synonym model.
- Sort order is fixed inside repositories and cannot be selected by clients.
- Public Product/Service/Rental lists have no minimum/maximum price filters.
- Category filters match one ID and do not include descendants.
- Rental discovery cannot filter the list by a requested availability interval.
- Mobile Products omit existing category/geo/store filters; Consultants omit
  existing geo filters; Social omits existing query and post-type filters.
- No suggestion, recent-search, popular-query, saved-search, or search analytics
  contract exists.

## Contract boundary

- Preserve all current domain list/detail routes and response privacy.
- Canonical commercial currency remains `TOMAN`; price filters must never infer
  or convert another currency.
- Unified results expose only fields already public in each domain contract.
- Search must never reveal draft, rejected, private, deleted, inactive, or
  unapproved records.
- Sorting and filter enums must be allow-listed; raw column/order expressions
  are forbidden.
- Start with MySQL and measured indexes. Elasticsearch/OpenSearch/Meilisearch is
  deferred until data volume, latency, language quality, or operations justify
  it.
- Suggestions/history/analytics require an explicit privacy and retention
  design; they are not silently collected.

## Delivery plan

1. **18.1 — Real-State Audit + Contract Boundary** (completed)
2. **18.2 — Shared Search Contracts + Persian Query Normalization**
3. **18.3 — Product Discovery Hardening**
4. **18.4 — Services Discovery Hardening**
5. **18.5 — Equipment Rental Discovery Hardening**
6. **18.6 — Consultant Discovery Hardening**
7. **18.7 — Social Discovery Hardening**
8. **18.8 — Unified Cross-Domain Search API + Ranking Boundary**
9. **18.9 — Mobile Unified Discovery Hub**
10. **18.10 — Performance, Privacy, and Abuse Hardening**
11. **18.11 — Docs/Postman + Runtime Search Regression**
12. **18.12 — Search/Filters/Discovery Release Gate + Tag**

## Step 18.2 entry criteria

Step 18.2 may introduce shared typed utilities and schemas, but must not change
the meaning of existing public status/privacy filters. It must prove normalized
Persian queries are deterministic, bounded, safe for empty input, and covered
by unit tests before domain repositories adopt them.

# Unified Search API

```http
POST /api/v1/search
Content-Type: application/json
```

This public, read-only endpoint runs one normalized query through the registered
Product, Store, Service, Rental Equipment, Consultant, and Social Post
providers. It stores no search history or analytics.

```json
{
  "q": "خدمات کشاورزی",
  "types": ["product", "service", "rental_equipment", "consultant"],
  "filters": {
    "province_id": 1,
    "city_id": 1,
    "product_category_id": 2,
    "service_category_id": 3,
    "rental_category_id": 4,
    "consultant_specialty_id": 5,
    "social_category_id": 6,
    "social_post_type": "guide",
    "service_pricing_type": "fixed",
    "rental_operator_mode": "either",
    "min_price": 0,
    "max_price": 50000000,
    "currency": "TOMAN"
  },
  "sort": "relevance",
  "page": 1,
  "page_size": 20
}
```

`q` is normalized for Persian/Arabic letter, diacritic, joiner, whitespace, and
digit variants. It must contain 2–100 normalized characters. `types` is unique,
ordered, and limited to the six public domains. Omitting it searches all six.

The response contains one group per requested type in the same order. Each
group has independent `items`, `total`, `page`, and `page_size`; the response
`total` is the sum of group totals. Results are not merged into a misleading
global score because relevance and commercial fields have different meanings
across domains.

Allowed shared sorts are `relevance`, `newest`, `price_asc`, `price_desc`, and
`rating`. A provider applies a sort when meaningful; otherwise it uses its safe
relevance/default ordering. Money filters and results are `TOMAN` only.

Every provider retains its existing public visibility and privacy rules. Result
routes are internal Mobile routes, and private contact, ownership, moderation,
request, and accounting fields are excluded.

## Performance, privacy, and abuse boundary

- A request may return at most 120 grouped items (`page_size × selected types`).
- Search has a dedicated default limit of 30 requests per 60 seconds per client,
  inside the broader API limit. A rejected request returns `429`, code
  `RATE_LIMITED`, and `Retry-After`.
- Search responses set `Cache-Control: no-store` and
  `X-Robots-Tag: noindex, nofollow`.
- Query text is not persisted, analyzed, personalized, or explicitly logged.
- `X-Forwarded-For` is ignored unless the immediate proxy IP is explicitly in
  `TRUSTED_PROXY_HOSTS`; never expose a trusted-proxy Backend directly.
- The in-process limiter has a bounded client-key set. Multi-instance production
  deployment still requires an edge or shared distributed rate limiter.
- Existing public/status/geo/price indexes are retained. Shared normalized
  substring matching is scan-based; no FULLTEXT/external engine is claimed
  without representative production volume and measured query plans.

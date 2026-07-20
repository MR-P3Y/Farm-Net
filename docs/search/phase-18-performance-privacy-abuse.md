# Phase 18.10 — Performance, Privacy, and Abuse Hardening

## Outcome

Unified Search now has bounded response work, a tighter abuse limit, safe proxy
identity handling, bounded limiter memory, and explicit no-cache/no-index privacy
headers without collecting search terms.

## Controls

- Maximum response budget: 120 grouped items.
- Search default: 30 requests per 60 seconds per client.
- Global API limit remains an outer boundary.
- 429 includes `Retry-After` and the standard error envelope.
- Limiter keeps at most 10,000 recently used client keys.
- Forwarded client identity is accepted only from `TRUSTED_PROXY_HOSTS`.
- Search responses are `no-store`, `noindex`, and `nofollow`.

## Explicit boundaries

The limiter is process-local and is appropriate for the current single Backend
instance. Horizontal production deployment requires a shared/edge limiter. Text
normalization uses SQL substring expressions, so representative production data
and query-plan evidence are required before introducing FULLTEXT or an external
search service. No search history, analytics, suggestions, or personalization is
stored in this step.

## Verification

Focused tests cover bounded limiter keys, untrusted/trusted proxy behavior,
Search-specific limiting, `Retry-After`, privacy headers, and response-budget
rejection. The full 164-test Backend suite and live 30/31 request boundary passed.

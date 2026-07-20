# Phase 18.9 — Mobile Unified Discovery Hub

## Outcome

Mobile now has one `/search` screen and one Home entry for discovery across all
six public Farm-Net domains.

## Contract

- A typed API/Repository sends one request to the unified Backend endpoint.
- Users may select any non-empty subset of result domains and one shared sort.
- Results remain grouped by domain with group and overall totals.
- Result cards render public title/summary, optional `TOMAN` price and rating,
  and navigate through the safe internal route supplied by Backend.
- The client does not recreate domain visibility, ranking, or filtering logic.

## UX and verification

The responsive screen covers untouched, loading, result, empty, error, and
retry states. Safe parsers handle decimal strings and optional fields. Flutter
analyze, all 40 tests, and the Web/Wasm build passed.

# Phase 21.6 — Selected Farm Context, Consent, Freshness and Privacy

Verified: 2026-07-27

## Outcome

Barzegar can use only the Farm context explicitly selected by its owner through
a versioned, expiring consent. Farm, Plot, and Crop Cycle ownership is verified
as one real hierarchy before consent creation and again when a request captures
its immutable context snapshot.

Barzegar never silently loads every Farm owned by a user.

## Owner APIs

| Method | Path |
|---|---|
| POST | `/api/v1/ai/context-consents` |
| GET | `/api/v1/ai/context-consents` |
| POST | `/api/v1/ai/context-consents/{id}/revoke` |

All three operations require `ai.context.use_own`. Consent output excludes the
user ID, idempotency key, selection fingerprint, active-scope key, and private
revocation reason.

## Consent contract

- consent uses `barzegar-farm-context-v1`;
- `user_id + idempotency_key` is unique;
- the selected user/Farm/Plot/Cycle/purpose has a stable SHA-256 fingerprint;
- only one consent for that selection may be active;
- a Crop Cycle cannot be selected without its owning Plot;
- expiry is limited to 1–168 hours;
- revocation is owner-scoped and prevents future context capture;
- archived Farms/Plots and cancelled cycles cannot be newly selected.

Migration: `e21a8f26e0c4`.

## Minimal snapshot

The request snapshot contains IDs, display names, lifecycle status, declared
area, limited geographic reference IDs, crop/variety IDs, planned dates, entity
update timestamps, consent version/purpose, and a freshness checksum.

It does not include Farm/Plot descriptions, Cycle notes, plot boundaries,
precise coordinates, media, diaries, laboratory history, or all other Farms by
default. Those require later purpose-specific context policies.

## Freshness

Before a worker may run, the selected hierarchy and consent are revalidated.
If ownership, status, consent, expiry, or any captured entity timestamp changed,
the request becomes `blocked` with `AI_CONTEXT_STALE` and
`CONTEXT_REFRESH_REQUIRED`. The old snapshot is never silently refreshed under
the same request.

## Verification

- all 349 Backend tests, Ruff, and compileall passed;
- MySQL migration and Alembic no-drift passed;
- real Farm-only consent, context request, revocation, worker-time stale block,
  and cleanup passed;
- OpenAPI exposes seven AI paths and nine typed operations;
- application, database, and Redis health remained `ok`.

## Next

Step 21.7 — Model Gateway, Prompt/Policy Registry + Routing.

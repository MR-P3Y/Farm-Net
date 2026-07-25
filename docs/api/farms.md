# Farm Management API

Phase 24 provides private multi-Farm profiles for authenticated farmers. A Farm
owns Plots; a Plot owns crop cycles; diary operations, inputs, harvests, media,
soil, irrigation, laboratory observations, and contextual weather attach to
that hierarchy.

## Authorization and privacy

- Owner reads require `farms.read_own`; owner changes require
  `farms.manage_own`.
- Restricted support reads require `farms.admin_read`.
- Every owner resource is checked against the authenticated owner.
- Admin support exposes summaries and audit history only. Exact coordinates,
  boundaries, laboratory values, diary notes, and media/storage details are
  excluded.
- Archive/restore is used instead of destructive Farm and Plot deletion.

## Endpoint groups

| Group | Prefix / purpose |
| --- | --- |
| Farms | `/farms` — create, list, detail, update, archive, restore |
| Plots | `/farms/{farm_id}/plots` — geo-aware Plot lifecycle |
| Cycles | `.../plots/{plot_id}/cycles` — crop-cycle lifecycle |
| Environment | soil profile, irrigation profile, water sources, lab observations |
| Diary | operations, operation inputs, harvests, Farm media |
| Weather | Plot context, explicit refresh, private alerts |
| References | `/farm-references/measurement-units?is_active=true` |
| Admin support | `/admin/farms` — read-only list/detail/audit |

The exact field names, enums, validation limits, request bodies, and response
schemas are authoritative in `/openapi.json`. All API responses use the common
`success`, `data`, `message`, and `meta` envelope.

## Lifecycle rules

- Farm and Plot: `active` ↔ `archived`.
- Crop cycle: `planned` → `active` → `completed`; planned/active cycles may be
  cancelled according to the Backend transition contract.
- Optimistic concurrency uses the current `version` where the schema requires
  it.
- Farm contextual Weather is private and does not replace public Weather
  locations.

## Postman and runtime verification

- Collection: `postman/collections/farms.postman_collection.json`
- Read-only regression:
  `backend/.venv/Scripts/python.exe backend/scripts/farms_runtime_regression.py`

The collection contains the complete owner, reference, Weather, and restricted
Admin workflow. Mutation bodies intentionally start empty so operators must use
the current OpenAPI contract rather than stale copied payloads.

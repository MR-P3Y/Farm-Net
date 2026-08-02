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
| Toolbox | `/farms/{farm_id}/toolbox` — saved calculations, finances, operation plans |
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
- Toolbox calculations are performed offline by Mobile for immediate feedback.
  When a result is saved, Backend version `1.0` recalculates it authoritatively
  and stores an immutable input/result snapshot.
- Financial entries are retained; mistakes are voided with a required reason.
- Plan items move from `planned` to `completed` or `cancelled`. Completing an
  item may also create a real crop-cycle diary operation when a cycle is set.

## Farm toolbox endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/farms/{farm_id}/toolbox/calculations` | Recalculate and save a formula `1.0` result |
| `GET` | `/farms/{farm_id}/toolbox/calculations` | Calculation notebook, optionally filtered by Plot/Cycle |
| `POST` | `/farms/{farm_id}/toolbox/costs` | Add an expense or revenue entry |
| `GET` | `/farms/{farm_id}/toolbox/costs` | Active financial entries |
| `POST` | `/farms/{farm_id}/toolbox/costs/{entry_id}/void` | Auditably void an entry |
| `GET` | `/farms/{farm_id}/toolbox/cost-summary` | Expense, revenue, net, and active count |
| `POST` | `/farms/{farm_id}/toolbox/plans` | Schedule a Farm operation and optional reminder |
| `GET` | `/farms/{farm_id}/toolbox/plans` | Operation plan, optionally filtered by Plot/Cycle |
| `POST` | `/farms/{farm_id}/toolbox/plans/{plan_id}/complete` | Complete and optionally write to the cycle diary |
| `POST` | `/farms/{farm_id}/toolbox/plans/{plan_id}/cancel` | Cancel while retaining history |

The seven calculator contracts are `seed`, `irrigation`, `fertilizer`,
`spraying`, `cost_profit`, `unit_conversion`, and `pump_fuel`. Fertilizer and
spraying inputs are user/label rates only and must not be presented as
agronomic prescriptions.

## Postman and runtime verification

- Collection: `postman/collections/farms.postman_collection.json`
- Read-only regression:
  `backend/.venv/Scripts/python.exe backend/scripts/farms_runtime_regression.py`

The collection contains the complete owner, reference, Weather, and restricted
Admin workflow. Mutation bodies intentionally start empty so operators must use
the current OpenAPI contract rather than stale copied payloads.

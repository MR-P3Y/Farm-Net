# Phase 24.1 — Farm Management / Digital Farm Profiles Real-State Audit

Verified: 2026-07-25
Branch: `develop`

## Owner decision

Farm-Net AI will primarily serve farmers. A farmer must be able to own several
private farm profiles so recommendations can use the correct land, crop,
weather, soil, water, irrigation, and operation context. Phase 24 is therefore
an explicit data prerequisite for resuming Phase 21 AI/RAG.

Phase 22 remains open at credentialed external-provider verification. Starting
this owner-authorized product track does not convert the unfinished Production
gate into a success claim.

## Verified current state

There is no implemented Farm/Farmland/Plot domain in Backend models, Alembic
migrations, permissions, APIs, Mobile, Admin, Postman, or release docs.

Existing adjacent domains are not farm profiles:

- `user_profiles` stores one personal identity/location profile per user;
- Geo provides Province through Village reference tables;
- Weather provides shared/GPS locations, snapshots, forecasts, and alerts;
- Activity Center links personal and business-role workflows;
- Stores, Services, Consultants, Rentals, Wallet, and Reviews are independent
  domains;
- agricultural PDFs under `docs/FARMER` are potential future knowledge sources
  but are not an indexed, approved RAG knowledge base.

No existing table records multiple farms, plots, area, farm boundary, crop
cycles, soil/water tests, irrigation, field operations, inputs, harvest, or
farm-specific media.

## Domain boundary

Phase 24 owns:

- multiple private farms per authenticated user;
- plots/management zones inside a farm;
- an Admin-managed crop/species/variety reference boundary;
- crop cycles per plot;
- soil, water, and irrigation profiles and dated test observations;
- a farm operation diary and harvest observations;
- farm/plot/cycle media through the existing Media domain;
- farm-specific Weather linkage;
- Mobile My Farms and owner-scoped Activity Center access;
- restricted Admin support/audit, not a public farm directory.

Phase 24 does not own:

- AI inference, chat, embeddings, RAG, or image diagnosis;
- land-title legal verification or cadastral authority integration;
- IoT device ingestion, satellite imagery, or drone processing;
- farm marketplace/public discovery;
- accounting mutations, subsidy, insurance, or lending;
- automatic pesticide/fertilizer prescriptions;
- real external Weather/provider activation.

## Core data principles

- Farm, plot, coordinates, boundaries, tests, operations, and production data
  are private owner data by default.
- Every owner API derives ownership from the authenticated user; client-sent
  owner IDs are rejected.
- Admin access requires a dedicated permission and must be auditable.
- Multiple farms and multiple plots per farm are first-class.
- Area is stored canonically in square metres with decimal precision; API/UI
  may present square metres or hectares without changing stored meaning.
- Dates are stored as Gregorian dates/UTC timestamps; Persian calendar is a
  presentation concern.
- Geo reference FKs are validated hierarchically.
- Exact coordinates/boundaries never enter public Search, logs, metrics, or AI
  context without an explicit authorized use.
- Records with dependent history are archived, not destructively deleted.
- AI later receives only a user-selected farm/plot/cycle context and records
  consent, source IDs, prompt version, and audit metadata.

## Proposed aggregate

```text
AuthUser
└── Farm (many)
    ├── FarmPlot (many)
    │   ├── CropCycle (many over time)
    │   │   ├── FarmOperation (many)
    │   │   ├── HarvestObservation (many)
    │   │   └── Media links
    │   ├── SoilProfile / SoilTest
    │   └── IrrigationProfile
    ├── WaterSource / WaterTest
    ├── WeatherLocation link
    └── Media links

CropCatalog
└── CropVariety
```

Exact tables and constraints must be finalized against current model/migration
conventions in Step 24.2; this diagram does not authorize speculative fields.

## Privacy and safety threats

- insecure direct-object access across farmers;
- public exposure of exact land coordinates or production capacity;
- forged Geo hierarchy or impossible area totals;
- plot area exceeding farm area through concurrent writes;
- overlapping/open crop cycles without an explicit intercropping policy;
- destructive deletion of agricultural history;
- unsafe AI advice inferred from stale or incomplete farm data;
- prompt injection through free-text notes or uploaded documents;
- sensitive farm data leaking into provider logs, metrics, Search, or model
  training.

These become regression contracts, not documentation-only warnings.

## Approved Phase 24 sequence

1. **24.1** Real-State Audit + Domain/Privacy Boundary.
2. **24.2** Crop/Measurement References, Permissions + DB Contract.
3. **24.3** Owner-Scoped Farm CRUD + Archive Lifecycle.
4. **24.4** Plot, Geo Point/Boundary + Area Consistency.
5. **24.5** Crop Catalog, Varieties + Crop-Cycle Lifecycle.
6. **24.6** Soil, Water, Irrigation + Laboratory Observations.
7. **24.7** Operation Diary, Inputs, Harvest + Farm Media.
8. **24.8** Privacy, Concurrency, Audit + Retention Hardening.
9. **24.9** Farm Weather Linking + Contextual Alerts.
10. **24.10** Mobile My Farms, Plots, Cycles + Diary.
11. **24.11** Activity Center + Restricted Admin Support.
12. **24.12** Docs, Postman + Runtime Regression.
13. **24.13** Farm Management Release Gate + Tag.

## Completion gate

Phase 24 is complete only when:

- a user can safely manage multiple farms and their nested history;
- ownership and Admin permission tests prevent cross-user access;
- Geo, area, lifecycle, archive, concurrency, and privacy contracts pass;
- Weather linkage is farm-specific without exposing coordinates;
- Mobile provides complete loading/empty/error/edit flows;
- Admin support is permission-protected and typed;
- docs/Postman/runtime regression match real APIs;
- Backend, Mobile, Admin, migration, OpenAPI, health, and Git gates pass;
- an independent release gate and annotated tag succeed.

AI/RAG must not treat Phase 24 as complete merely because tables exist.

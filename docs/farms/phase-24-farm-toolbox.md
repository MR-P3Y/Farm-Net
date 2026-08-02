# Phase 24 — Farm Toolbox

Status: completed, locally activated, and manually accepted on 2026-08-02.

## Product surface

The authenticated `/toolbox` Mobile route is available from Discover. A compact
context selector lets the owner scope records to a Farm and, optionally, a Plot
and crop cycle. The layout adapts from two Mobile columns to three/four
wider-screen columns and provides four focused tabs:

1. offline calculators;
2. expenses/revenue and profit context;
3. operation calendar and reminders;
4. immutable saved-calculation notebook.

Seven offline calculators cover seed/plant count, irrigation, fertilizer,
spraying, profit/break-even, unit conversion, and pump/fuel. Plot or declared
Farm area is prefilled when available. Persian and Arabic digits are accepted.
Fertilizer and spraying screens explicitly state that entered or label rates
are calculated and no agronomic prescription is generated.

The Farm/Plot/Cycle selector is collapsed to one summary row by default and
expands only when the owner wants to change context. All calculator field units,
conversion units, result units, lifecycle labels, and error messages follow the
active Persian/English locale; Persian results also use Persian digits.

## Backend and retention

All APIs use existing `farms.read_own` and `farms.manage_own` authorization and
validate that Plot/Cycle context belongs to the requested Farm.

- Saved calculations are immutable. Backend independently applies formula
  version `1.0`; client-supplied result values are never accepted.
- Financial entries are retained and can only be voided with a reason.
- Plans are retained and support complete/cancel transitions. Completion can
  create the existing crop-cycle operation diary record.
- Due reminders use the existing notification outbox/delivery worker through
  event type `farm.plan_reminder`.

The additive Alembic migration creates `farm_tool_calculations`,
`farm_financial_entries`, and `farm_plan_items`. It was applied to the local
MySQL runtime without stopping or restarting Backend, database, phone,
emulator, or Chrome sessions.

## Verification evidence

- Backend Ruff: passed for every touched Backend/migration/test file.
- Backend focused tests: 13 passed; full Backend suite: 400 passed.
- Alembic head/current: `m26a1b2c3d4e`.
- Local MySQL contains all three new tables.
- Mobile focused analyze: no issues.
- Mobile calculator/model/localization tests: 12 passed; full Mobile suite: 131
  passed.
- Flutter Web release/Wasm dry-run and Android debug APK builds: passed.
- Runtime health: application, database, and Redis are `ok`; real Android phone
  remains connected with `tcp:8000` reverse, and Chrome remains available.

After explicit owner approval, only `farmnet_backend` received one controlled
restart. Application/database/Redis health returned `ok`, all seven Toolbox
paths appeared in runtime OpenAPI, and an unauthenticated Toolbox request
returned the expected `401` instead of the stale-process `404`. MySQL, Redis,
the real phone, Chrome, and Android reverse were not restarted or reconfigured.
Mobile still distinguishes a future server-version `404` from a real
offline/network failure and does not display raw `Not Found` as offline.
The Android emulator was not running during verification; its support is
covered by the successful Android build and no emulator session was launched or
reconfigured.

## Acceptance

On 2026-08-02, the project owner confirmed the manual Toolbox checks passed,
including the compact Farm context selector and the corrected synchronization
state. The automated and runtime evidence above remains the release evidence;
the owner confirmation closes the visual acceptance gate.

# Phase 23.6 Lessor Activity Integration

## Result

The shared Activity Center now renders the Lessor section from the authoritative
role/permission catalog and links the existing complete Rental owner flows:

- own Lessor Profile create/edit/submit and moderation status;
- own Equipment create/edit/submit;
- Equipment media, pricing, and availability management through the existing
  Equipment destinations;
- assigned Rental Request workbench, detail, timeline, and valid transitions.

## Authorization boundary

- Profile requires `rental_lessors.profile_manage`.
- Equipment requires a real create or update permission.
- Workbench requires `rental_requests.manage_assigned`.
- The `lessor` role does not bypass a missing action permission.
- Users without a Lessor role/setup permission receive no empty or misleading
  Lessor section. Role acquisition remains the existing Verification workflow.

The Activity Center does not load or fabricate pricing, availability, booking,
deposit, or profile-status counters. Their owner screens remain authoritative.

## Verification

- Added focused catalog coverage for the exact Profile, Equipment, and
  Workbench action set.
- Mobile format/analyze: passed with no issues.
- Mobile tests: all 48 passed.
- Mobile Web build and Wasm dry-run: passed.
- Runtime health: application, database, and Redis `ok`.
- Runtime OpenAPI: 254 paths; ten key Lessor Profile, Equipment, Pricing,
  Availability, and assigned-request contracts passed method checks.

No Backend, API, database, permission seed, Admin Panel, Rental workflow, or
financial behavior changed.

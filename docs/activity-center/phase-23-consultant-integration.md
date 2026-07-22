# Phase 23.7 Consultant Activity Integration

## Result

The shared Activity Center now renders the Consultant section from the real
role/permission catalog and links:

- own Consultant Profile create/edit/submit, specialties, and moderation state;
- assigned Consultation Request workbench, filters, detail, timeline, and valid
  Consultant transitions.

Requester Consultation activity remains in the common personal section. It is
not mixed with professional assigned work.

## Authorization boundary

- Profile setup requires `consultants.profile_manage`.
- Assigned work requires `consult_requests.manage_assigned`.
- A user with setup permission but without the approved Consultant role sees
  only the setup action and approval guidance.
- The `consultant` role alone does not bypass missing action permissions.
- Profile moderation status and valid request transitions continue to come from
  the existing typed owner/workbench flows.

## Verification

- Added focused catalog coverage for the exact Profile and Workbench action set.
- Mobile format/analyze: passed with no issues.
- Mobile tests: all 49 passed.
- Mobile Web build and Wasm dry-run: passed.
- Runtime health: application, database, and Redis `ok`.
- Runtime OpenAPI: 254 paths; five key Consultant Profile and assigned-request
  contracts passed exact method checks.

No Backend, API, database, permission seed, Admin Panel, Consultation workflow,
final-price, or financial behavior changed.

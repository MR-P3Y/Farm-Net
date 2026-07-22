# Phase 23.5 Service Provider Activity Integration

## Result

The shared Activity Center renderer now exposes the Service Provider section
alongside Shop Owner without duplicating section UI or permission logic.

The section connects the existing real Mobile flows for:

- own provider profile create/edit/submit and moderation status;
- own Service Offers create/edit/media/submit and status;
- assigned Service Request workbench, detail, timeline, and valid transitions.

## Role and setup behavior

- A base user with `service_providers.profile_manage` sees only the provider
  setup action and a `نیازمند تکمیل و تأیید` marker.
- Offers require one of the real create/update/submit permissions.
- The assigned workbench requires `service_requests.manage_assigned`.
- An approved `service_provider` role does not bypass a missing permission.
- Existing workbench 403 behavior continues to explain that provider approval
  is required.

## Verification

- Added a focused catalog test proving the approved provider receives exactly
  Profile, Offers, and Workbench actions.
- Mobile format/analyze: passed with no issues.
- Mobile tests: all 47 passed.
- Mobile Web build and Wasm dry-run: passed.
- Runtime health: application, database, and Redis `ok`.
- Runtime OpenAPI: 254 paths; eight provider profile/offer/assigned-request
  contracts and their exact methods are present.

No Backend, API, database, permission seed, Admin Panel, or Services workflow
behavior changed. The Activity Center does not fabricate provider counters or
moderation status; the destination screens load those values from their real
owner APIs.

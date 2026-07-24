# Phase 19.7 — Mobile Review Creation, History + Public Rendering

## Shared Mobile foundation

One Reviews feature now serves all marketplace domains:

- typed public rating/review, owner Review, and creation-target models;
- shared API/repository for public list, owner history, create, edit, delete;
- reusable public Reviews section with loading, retry, empty, average/count,
  safe author, text, and star rendering;
- authenticated creation form with 1–5 stars, optional 2000-character body,
  saving state, and Backend error display;
- owner history with refresh, lifecycle-aware edit/delete, loading, error, and
  empty states.

## Navigation and domain integration

- `نظرات من` is permission-aware in My Activity Center.
- Delivered Orders expose Store and each purchased Product review actions.
- Completed Service Requests expose Service Offer review creation.
- Completed Rental Requests expose Equipment review creation.
- Completed Consultation Requests expose Consultant review creation.
- Product, Store, Service Offer, Rental Equipment, and Consultant detail
  screens render their public Reviews using the same component.

The shared models retain all seven Backend subject types, including Provider
and Lessor, so later dedicated public profile pages can reuse this foundation.
Eligibility remains entirely server-authoritative; Mobile never decides that a
non-terminal source is reviewable beyond hiding the action.

## Verification

| Check | Result |
| --- | --- |
| Flutter analyze | OK |
| Flutter tests | 54 passed |
| Review model tests | 3 passed |
| Flutter Web build | OK; Wasm dry run passed |

Admin moderation UI remains Step 19.8. Generated Web build output is ignored
and is not committed.

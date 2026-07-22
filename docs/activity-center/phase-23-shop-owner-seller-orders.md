# Phase 23.4 Shop Owner Center + Seller Order Workbench

## Result

The Shop Owner section is now rendered from the shared Activity Catalog and
links to own Store, own Products, and the new Seller Order Mobile workbench only
when their exact permissions are present.

## Seller Order Mobile flow

Mobile now consumes the existing Backend contracts:

- `GET /api/v1/seller/orders` with status filter and pagination;
- `GET /api/v1/seller/orders/{order_id}`;
- `PATCH /api/v1/seller/orders/{order_id}/status`.

The workbench provides loading, refresh, empty, error, denied, filter,
pagination, list, detail, delivery information, item snapshots, status history,
and optional Seller note states. It refreshes list state after a successful
detail update.

Seller actions exactly match the Backend transition matrix and require a paid
payment state:

```text
paid -> confirmed -> processing -> shipped -> delivered
```

No cancel, refund, backward, or skip transition is exposed to Seller.

## Privacy and money

- List responses tolerate the intentionally excluded Buyer delivery fields,
  payments, status history, commission fields, and Admin note.
- Detail displays Buyer delivery fields returned by the owner-scoped Backend
  contract, but never renders commission or Admin note.
- Seller share and order totals use the canonical Iranian `TOMAN` formatter.
- A permission-denied response renders explicit approved Shop Owner guidance.

## Verification

- Mobile format and analyze: passed with no issues.
- Mobile tests: 46 passed, including Seller pagination/privacy parsing and the
  exact transition matrix.
- Mobile Web build and Wasm dry-run: passed.
- Backend full suite: 164 passed with 18 known deprecation warnings.
- Runtime health: application, database, and Redis `ok`.
- Runtime OpenAPI: 254 paths; all three Seller Order paths and methods present.

Runtime had no authenticated Shop Owner order fixture for a safe real status
change. No real Seller transition is claimed; the existing Backend contract and
typed Mobile tests cover that boundary. No Backend/API/database/Admin behavior
changed in this step.

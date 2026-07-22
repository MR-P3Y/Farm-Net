# Phase 23.2 Typed Role/Permission Activity Catalog

## Result

Mobile now has one pure, typed, and testable `ActivityCatalog` that converts the
authenticated `AuthUser.roles` and `AuthUser.permissions` into ordered activity
sections and safe destination contracts.

## Contract

- Common personal activity includes identity and verification, then exposes
  notifications, finance, Buyer Orders, and requester flows only when their
  real permissions are present.
- Shop Owner, Service Provider, Lessor, and Consultant sections are independent,
  so a multi-role user receives every authorized section without role switching.
- Setup access and approved operational access are distinct. A user with a
  profile-management permission may see the corresponding setup action, while
  assigned-request workbenches require their exact manage-assigned permission.
- Actions inside an approved role section remain permission-backed; a role name
  alone does not fabricate an operation.
- Admin/support/data roles do not create Mobile business sections.

## Seller boundary

The catalog reserves the typed `/seller/orders` destination only for
`orders.seller_read`. It is not consumed by a screen in this step. Step 23.4
must register the route and implement the real Seller Order Mobile workbench
before the Activity Center exposes this action to users.

## Verification

- `dart format`: passed.
- `flutter analyze --no-pub`: no issues.
- `flutter test --no-pub`: 44 tests passed, including four catalog tests for
  personal permission filtering, setup-vs-approved behavior, Shop permissions,
  and ordered multi-role composition.

No Backend, database, Admin Panel, API, permission seed, or current UI behavior
changed.

# Phase 23.9 Home Navigation Simplification + Deep-Link/Auth Hardening

## Home result

The long flat Home management menu was replaced with a focused entry surface:

- primary My Activity Center action;
- Unified Search;
- public Store, Product, Service, Rental, Consultant, Social, and Weather
  discovery;
- authenticated Cart;
- Notification badge and logout.

Profile, Verification, Finance, own requests/orders, owner resources, and all
four professional workbenches are no longer duplicated on Home. They are
available through the role/permission-driven Activity Center.

## Deep-link and auth guard

A shared `AuthenticatedRouteGuard` now protects Home and private routes used by
the Activity Center, including identity, Verification, Notifications, Finance,
Cart/Orders, requester flows, Store/Product owner flows, Seller Orders, and
Service Provider/Lessor/Consultant owner workbenches.

On a direct Web/deep-link visit the guard:

1. loads the real current session when auth state is unresolved;
2. renders a loading state while identity is recovered;
3. renders no private child for an unauthenticated/expired session;
4. offers the real root Auth Gate;
5. renders the requested child only for an authenticated user.

Backend permissions remain the final authorization authority. The guard does
not infer a permission or replace API 401/403 handling.

## Verification

- Added two Widget tests proving unauthenticated private-child exclusion and
  authenticated rendering.
- Mobile format/analyze: passed with no issues.
- Mobile tests: all 52 passed.
- Mobile Web build and Wasm dry-run: passed after the final Home guard change.
- Generated Web output remained ignored and was not staged.

No Backend, API, database, permission seed, Admin Panel, or business workflow
behavior changed.

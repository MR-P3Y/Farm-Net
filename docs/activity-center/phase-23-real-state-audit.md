# Phase 23 Role-Based My Activity Center Real-State Audit

## Audit boundary

- Step: 23.1
- Date: 2026-07-22
- Baseline: `v0.23.0-search-discovery-foundation` / `a6e5385`
- Scope: read-only inspection of Mobile navigation, authenticated identity,
  role permissions, owner/requester workbenches, verification, notifications,
  and finance surfaces.

No API behavior, database contract, permission, or client behavior changed in
this step.

## Real identity contract

`AuthUser` already exposes the authoritative `roles` and `permissions` arrays.
The seeded business roles relevant to this center are:

- `user`: common requester/buyer activity;
- `shop_owner`: store, products, seller orders, and provider finance;
- `service_provider`: provider profile, offers, and assigned requests;
- `lessor`: lessor profile, equipment, commercial rules, and assigned rentals;
- `consultant`: consultant profile and assigned consultation requests.

Admin/support/content/finance/verification/data-client roles remain Admin or
specialized operational concerns and must not create fake Mobile business
workbenches.

## Existing Mobile destinations

Common authenticated activity already has screens for profile, verification
requests, notifications/preferences, finance, buyer orders, Service requests,
Rental requests, and Consultation requests.

Owner/provider screens already exist for:

- Shop: own Store and Products;
- Services: provider profile, Offers, and assigned-request workbench;
- Rental: lessor profile, Equipment/commercial management, and workbench;
- Consultant: consultant profile and assigned-request workbench.

These screens are currently reached from a long flat Home page. Home renders
role-specific links without checking the authenticated user's roles or
permissions, so users can enter irrelevant screens and discover authorization
only after an API 403.

## Confirmed gap

Backend already exposes permission-protected Seller Order list, detail, and
status-update APIs under `/api/v1/seller/orders`. Mobile has typed Buyer Order
flows but no Seller Order API/repository/controller/screens or route. A complete
Shop Owner activity center therefore requires a real Mobile Seller Order
workbench; linking only Store and Products would be incomplete.

## Architecture decision

Phase 23 is Mobile-first orchestration over authoritative existing APIs. It
must not add an aggregate endpoint merely to render a menu. A typed, testable
activity catalog will derive visible sections and actions from `AuthUser.roles`
and `AuthUser.permissions`. Backend permissions remain the final authority.

The center will have:

1. common personal activity for every authenticated user;
2. independent role sections for Shop Owner, Service Provider, Lessor, and
   Consultant, allowing one user to hold several roles concurrently;
3. explicit setup/verification guidance instead of silently granting roles;
4. safe navigation only to registered routes;
5. loading/empty/error and 401/403 behavior in every newly added data flow.

Role switching is unnecessary: multi-role users should see all authorized
sections in one center. Admin Panel behavior is outside this Mobile phase.

## Delivery sequence

- 23.2 — Typed Role/Permission Activity Catalog
- 23.3 — Activity Center Shell + Common Personal Activity
- 23.4 — Shop Owner Center + Seller Order Workbench
- 23.5 — Service Provider Activity Integration
- 23.6 — Lessor Activity Integration
- 23.7 — Consultant Activity Integration
- 23.8 — Role Setup/Verification + Multi-Role Hardening
- 23.9 — Home Navigation Simplification + Deep-Link/Auth Hardening
- 23.10 — Docs, Tests, and Runtime Regression
- 23.11 — Release Gate + Tag

## Explicit non-goals

- no review/rating/report behavior from Phase 19;
- no new payment, settlement, or accounting behavior;
- no Admin Panel role workbench duplication;
- no fabricated counters or client-side business status transitions;
- no database migration or new permission unless later repository evidence
  proves it is required.

# Phase 25.8 — Mobile Subscription Center

Status: completed

## Delivered

- Added typed Mobile models for plans, feature values, the current
  subscription, entitlements, usage, and checkout/verification results.
- Added a repository and controller over the real `/api/v1/billing` contracts.
- Added an authenticated Subscription Center that renders:
  - current plan, lifecycle status, expiry, grace, and cancellation state;
  - metered usage with used and reserved quantities;
  - active plans and TOMAN prices;
  - Free activation, paid checkout, grace-period renewal, cancellation,
    and resume actions;
  - loading, empty, validation, authorization, and retry states.
- Added a permission-backed entry to My Activity Center and the protected
  `/subscription` route.
- Added model, widget, and Activity Catalog coverage.
- Added a non-breaking `AuthUser.displayName` fallback required by the current
  Home implementation.

## Payment Boundary

- Local development hosts use the Backend's non-production mock
  checkout/verification path.
- Non-local environments request a Zarinpal checkout and copy the returned
  redirect URL for the user. Activation remains server-authoritative through
  the payment callback; the Mobile screen refreshes the subscription state
  after return.
- No payment credentials or client-side payment authority were added.
- All displayed subscription prices use TOMAN.

## Verification

- Focused Dart analyze: passed with no issues.
- Flutter tests: 68 passed.
- Flutter web build: passed; Wasm dry-run passed.
- Full Flutter analyze: the Subscription scope is clean, but the repository
  remains with two unrelated concurrent warnings:
  - unused `l10n` in `mobile/lib/features/home/home_screen.dart`;
  - duplicate import in
    `mobile/lib/features/social/presentation/social_post_detail_screen.dart`.
- These unrelated user changes were preserved and are not part of this step.

## Next

Phase 25.9 — Admin Plans, Subscriptions, Usage + Manual Operations.

# Phase 11.8 Mobile Notification Center Hardening

Completion date: 2026-07-18

## Implemented

- Typed Mobile preference and device registration API contracts.
- Global channel preference screen for in-app, Email, SMS, and Push.
- Optimistic preference updates with rollback and backend error rendering.
- Settings navigation from the Notification Center.
- Action routing expanded for Social posts, Services, and Consultants while
  preserving Orders, Verification, Profile, and unsupported-route feedback.
- Typed model tests ensure preference parsing and token-free device responses.

## Verified Existing Behavior

- Loading, empty, error, pull-to-refresh, unread count, filters, mark read,
  mark-all-read, delete, badge, and responsive layout remain present.

## Verification

- Flutter analyze: no issues.
- Flutter tests: 28 passed.
- Flutter Web build: passed, including Wasm dry run.
- Backend device/preferences paths remain runtime available and health is OK.

## Exact Gap

No vendor Push SDK is installed, so Mobile cannot acquire/refresh a real FCM or
APNs token yet. The typed register/unregister contracts are ready, but runtime
device registration must wait for vendor selection and platform credentials.
No fake token is generated or registered.

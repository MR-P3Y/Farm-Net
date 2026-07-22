# Phase 23.3 Activity Center Shell + Common Personal Activity

## Result

Mobile now exposes the authenticated `/activity` route and a responsive
`ActivityCenterScreen`, reached through a primary Home action labelled
`مرکز فعالیت‌های من`.

The screen consumes the typed catalog from Step 23.2 and currently renders only
the common personal section:

- Profile;
- Verification requests and documents;
- Notifications;
- Finance Center;
- Buyer Orders;
- own Service requests;
- own Rental requests;
- own Consultation requests.

Every optional action remains permission-driven. The identity card uses only
the authenticated email/phone and a count of active business roles; it does not
invent profile or operational status.

## Auth and navigation boundary

- Loading has an explicit progress state.
- A direct unauthenticated visit shows a signed-out state and returns through
  the real root Auth Gate.
- Destinations come from the typed catalog and use registered existing routes.
- Business-role sections are deliberately not rendered yet. They will be added
  only in Steps 23.4–23.7 after each integration is complete.
- Existing flat Home shortcuts remain temporarily available. Step 23.9 will
  simplify Home only after all role destinations are safely available here.

## Verification

- `dart format`: passed.
- `flutter analyze --no-pub`: no issues.
- `flutter test --no-pub`: all 44 tests passed.
- `flutter build web --no-pub`: passed; Wasm dry-run passed.

No Backend, database, Admin Panel, API, or permission behavior changed.

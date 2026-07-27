# Phase 21.12 — Mobile Barzegar Assistant

Status: completed

The authenticated Flutter application now exposes Barzegar from Home at
`/barzegar`.

## Typed integration

- Conversation list/create/detail and request submission.
- All six backend request kinds:
  text, Farm context, deep analysis, image analysis, smart diary, and report.
- Purpose-matched 24-hour selected-Farm consent.
- Farm, optional Plot, and optional Crop Cycle are loaded from the real Farm
  repository; smart diary requires a selected Crop Cycle.
- JPEG/PNG/WebP evidence is uploaded as private general Media before image
  analysis submission.
- Request state refresh covers queued, running, succeeded, failed, blocked, and
  cancelled outcomes.

## Farmer experience

- Three sections: chat, smart diary, and farmer reports.
- Clear empty, loading, error, permission, entitlement/quota, and pending
  processing states.
- Safety notice explains that Barzegar does not replace a specialist.
- The UI explicitly reports that live Provider processing remains disabled
  until OpenAI billing is activated.
- Smart diary proposals remain pending until the farmer taps accept; the app
  also supports explicit rejection.
- Farmer report cards display real operation, input, and harvest snapshot
  counts and an expandable narrative.

## Verification

- `flutter analyze --no-pub`: passed
- `flutter test --no-pub`: 72 passed
- `flutter build web --no-pub`: passed, including Wasm dry run
- Generated build output was not staged.

Next: Step 21.13 Admin Barzegar Governance.

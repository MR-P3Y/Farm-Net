# Phase 21.11 — Smart Diary Suggestions + Farmer Reports

Status: completed

Barzegar now turns eligible AI results into owner-scoped farmer artifacts.

## Smart diary

- `smart_diary` requests require an active `smart_diary` selected-Farm consent
  containing Farm, Plot, and Crop Cycle.
- Provider output must match the typed operation proposal contract:
  `operation_type`, `title`, `occurred_on`, and optional `notes`.
- A successful request creates one pending `ai_diary_suggestions` row. It does
  not modify the Farm diary.
- The owner explicitly accepts or rejects the suggestion.
- Accept uses the real active-cycle, ownership, operation-date, enum, and Farm
  audit contracts and creates exactly one `farm_operations` row.
- Repeated decisions return the existing terminal state and cannot duplicate
  the Farm operation.

Owner APIs:

- `GET /api/v1/ai/diary-suggestions`
- `POST /api/v1/ai/diary-suggestions/{id}/accept`
- `POST /api/v1/ai/diary-suggestions/{id}/reject`

## Farmer reports

- `report` requests require an active `report` selected-Farm consent.
- Each successful request creates exactly one `ai_farmer_reports` row.
- The immutable source snapshot identifies the selected Farm/Plot/Cycle,
  records the consent-context freshness hash, and counts real operations,
  operation inputs, and harvest observations for the selected cycle.
- Reports are private to their owner through
  `GET /api/v1/ai/farmer-reports`.

## Verification

- Alembic head: `k21g8e5c1029`
- Ruff: passed
- compileall: passed
- backend tests: 368 passed
- database/Redis health: passed
- Provider live generation remains operationally disabled until OpenAI billing
  is activated; this does not weaken the local contracts or test coverage.

Next: Step 21.12 Mobile Barzegar Assistant.

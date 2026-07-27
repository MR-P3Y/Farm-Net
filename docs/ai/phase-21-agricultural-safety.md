# Phase 21.9 — Agricultural Safety, Output Validation + Human Escalation

Verified: 2026-07-28  
Alembic head: `i21e6c3af807`

## Implemented

- Deterministic Persian preflight triage for poisoning/emergency and high-risk
  pesticide/chemical requests.
- Emergency poisoning produces immediate conservative guidance before
  Entitlement/quota reservation; it is marked `blocked` and consumes no quota.
- High-risk chemical output is usable only with at least one immutable
  citation, explicit uncertainty, and a recommendation for human review.
- Validation failure blocks the result, records a stable failure code, creates
  no technical usage, and releases the Billing reservation.
- Owner-visible safety codes remain typed on the AI request and safety labels
  are recorded on emergency messages.
- Added explicit owner-triggered escalation endpoint:
  `POST /api/v1/ai/requests/{request_id}/escalate`.
- Escalation reuses the real Consultant request workflow, status log,
  notification behavior, optional specialty, and TOMAN contract. It never
  creates a commercial request automatically.
- `ai_requests.consult_request_id` provides a unique, auditable `RESTRICT`
  link to the real `consult_requests` row.

## Verification

- Ruff and compileall: passed.
- Backend tests: `360 passed`.
- Alembic head: `i21e6c3af807`.
- Real MySQL emergency request: safe output, blocked status, zero quota
  reservation, and cleanup passed.
- OpenAI live generation remains disabled because Provider Billing credit is
  unavailable.

Step 21.10 Image Analysis Boundary + Evidence-Gated Diagnosis is next.

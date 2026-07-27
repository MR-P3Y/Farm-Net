# Phase 21.2 — Barzegar AI Core Foundation

Status: complete.

Migration: `a21c4b82a6e0`

## Delivered

Nine additive, Provider-neutral tables establish the Barzegar operational
boundary:

- `ai_conversations`;
- `ai_context_consents`;
- `ai_requests`;
- `ai_messages`;
- `ai_execution_attempts`;
- `ai_usage_records`;
- `ai_feedback`;
- `ai_data_deletion_requests`;
- `ai_audit_logs`.

No model Provider, SDK, credential, network request, knowledge ingestion,
embedding, vector store, prompt implementation, or user/Admin API was added.

## Core guarantees

- Every Conversation, Request, Feedback, deletion request, and selected Farm
  context is owner-bound.
- Farm context uses real `farms`, `farm_plots`, and `farm_crop_cycles` FKs.
- Context is absent unless a consent record and a captured manifest/timestamp
  are present together. The manifest is limited to source identifiers,
  versions, and freshness metadata; raw coordinates and Farm values belong
  only in the transient execution context.
- AI Request replay is bounded by `user_id + idempotency_key`.
- Billing quota is linked one-to-one through the existing
  `billing_usage_reservations` contract.
- Provider attempts are numbered exactly once per Request and provider request
  IDs are deduplicated per Provider.
- Technical token/cost usage is one-to-one with the successful Request and
  Attempt; it does not replace commercial Billing usage.
- Retention and deletion are explicit lifecycle states, not destructive
  cascading deletes.
- Audit event keys are unique and Audit metadata is explicitly safe metadata,
  not raw prompts, secrets, or private context.
- All domain FKs use `RESTRICT`.

## Permissions

The default user role receives nine owner-scoped permissions:

```text
ai.conversations.create
ai.conversations.read_own
ai.conversations.manage_own
ai.requests.create
ai.requests.read_own
ai.requests.cancel_own
ai.context.use_own
ai.feedback.create_own
ai.data.delete_own
```

The Admin role receives the existing six restricted AI operations plus:

```text
ai.audit.read
ai.retention.manage
```

Roles remain independent from Subscription Entitlements. Both permission and
Entitlement/quota must pass before future execution.

## Provider-neutral contract

`app.modules.ai.contracts` defines immutable request/result/usage objects and
the `AIModelProvider` Protocol. It deliberately contains no API key field and
adds no third-party dependency. Provider selection, configuration, prompt
policy, and concrete adapters belong to Step 21.7.

## Retention boundary

- Each Conversation has an explicit `retention_until`.
- User deletion requests are idempotent and can target one Conversation or all
  Conversations.
- Conversation status moves through `deletion_pending` before `deleted`.
- Messages may be redacted while immutable technical/Audit records retain only
  the minimum safe operational evidence required by documented policy.
- Processing and purge services are not claimed in this database-only step.

## Verification

```text
Focused tests: 6 passed
Full Backend tests: 322 passed
Ruff: OK
compileall: OK
Alembic head: a21c4b82a6e0
Alembic no-drift: OK
Offline migration SQL: 9 AI CREATE TABLE statements
Real MySQL migration: OK
Runtime AI tables: 9
Auth seed twice: 12 roles / 281 permissions
User AI permissions: 9
Admin AI permissions: 8
Health: app ok / database ok / redis ok
```

## Next

Step 21.3 — Knowledge Source Governance, Ingestion + Persian Extraction.

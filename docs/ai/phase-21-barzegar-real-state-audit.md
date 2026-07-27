# Phase 21.1 — Barzegar AI/RAG Real-State Audit

Verified: 2026-07-27  
Branch: `develop`  
Baseline: `v0.27.0-subscriptions-foundation`

## Product identity

The official Farm-Net agricultural AI assistant is:

```text
Barzegar (برزگر)
```

`برزگر` means farmer/cultivator. Barzegar is primarily a farmer-facing
agricultural assistant, not a generic chatbot attached to every module.

## Verified current state

There is no implemented AI runtime in the repository:

- no Backend `ai` module, models, migration, repository, service, router, or
  worker;
- no `ai_*` database implementation in Alembic;
- no owner or Admin AI UI;
- no AI Postman collection;
- no LLM/provider SDK or HTTP adapter;
- no embedding pipeline, vector index, reranker, or retrieval service;
- no approved RAG source registry, chunk store, citation contract, prompt
  registry, model registry, technical usage/cost log, or feedback workflow.

The six existing `ai.*` permissions are legacy Admin placeholders only:

- `ai.requests.read`;
- `ai.feedback.read`;
- `ai.knowledge_sources.read`;
- `ai.knowledge_sources.create`;
- `ai.knowledge_sources.update`;
- `ai.usage.read`.

They do not prove an AI feature exists. Owner permissions and operational
permissions must be designed in Step 21.2.

The 30 agricultural PDFs under `docs/FARMER` are candidate materials only.
They currently have no verified publisher, edition, effective date, licensing,
approval status, checksum, extraction result, chunking, embedding, or
revocation lifecycle. Barzegar must not cite them as trusted knowledge merely
because the files exist.

## Implemented prerequisites

### Private farm context

Phase 24 provides real owner-scoped data for multiple Farms, Plots, Crop
Cycles, soil/water/irrigation profiles, laboratory observations, operations,
inputs, harvests, Media, and contextual Weather. Exact coordinates, boundaries,
production data, laboratory values, and notes remain private.

AI may receive only the user-selected Farm/Plot/Cycle scope. It must record
consent, context source IDs and versions, context timestamp/freshness, and the
prompt-policy version. It must never silently sweep every Farm owned by a user.

### Commercial Entitlement and quota

Phase 25 provides these typed AI features:

- `ai.text_chat`;
- `ai.farm_context`;
- `ai.deep_analysis`;
- `ai.image_analysis`;
- `ai.smart_diary`;
- `ai.report_export`;
- `ai.processing_priority`.

The Free plan currently grants 20 text requests, 8 farm-context requests, one
image analysis, no deep analysis, no smart diary, no AI report export, and
standard priority. Commercial Farmer Plus/Professional prices and final limits
remain an Admin/product decision; Barzegar must consume the existing Billing
Entitlement rather than introduce a second subscription table.

Each metered run must follow:

```text
authorize permission
→ validate safety/privacy and selected context
→ estimate quota
→ reserve quota atomically with idempotency
→ execute Provider/RAG workflow
→ finalize only for a usable answer
→ release on rejection, timeout, Provider, validation, or internal failure
```

Technical Provider/model/token/cost usage belongs in AI usage records. It must
reconcile with Billing usage but must not replace the commercial quota ledger.

## Approved Barzegar boundary

Barzegar v1 owns:

- Persian agricultural questions and cited answers;
- optional, explicit Farm/Plot/Cycle-aware assistance;
- governed agricultural knowledge retrieval;
- conversation/request history owned by the user;
- answer citations, confidence limitations, and source freshness;
- user feedback and unsafe/incorrect-answer reporting;
- Entitlement/quota enforcement and technical cost accounting;
- safety triage and escalation to a human Consultant;
- Mobile farmer experience and restricted Admin operations.

Barzegar v1 does not own:

- autonomous pesticide, fertilizer, irrigation, veterinary, financial, or
  legal decisions;
- guaranteed disease diagnosis from text or image;
- automatic execution of Farm diary or marketplace mutations;
- background access to all private Farms;
- training Providers on Farm-Net user data;
- public exposure of private Farm context;
- unrestricted web search or ingestion of unknown documents;
- local hosting of a large model or GPU infrastructure by default.

Using a managed Provider does not require heavy Farm-Net GPU hardware. The
main local workload is API orchestration, document extraction, retrieval,
queues, storage, and monitoring. Self-hosting generation or large embedding
models is a separate future infrastructure decision and is not assumed.

## Provider-neutral architecture

```text
Mobile Barzegar
  → Auth + permission
  → Safety/privacy/context validation
  → Billing quota reservation
  → AI request + immutable execution attempt
  → Intent/policy router
      → governed RAG retrieval
      → selected private Farm context builder
      → Provider-neutral model gateway
  → citation/safety/output validation
  → usable answer + technical usage
  → Billing finalize (or release on failure)
  → feedback / Consultant escalation / notification
```

Provider credentials are server-side secrets. Provider name, model, prompt
version, retrieval version, token counts, latency, cost, and outcome are
auditable; secret keys, raw private context, and full prompts must not enter
ordinary logs or metrics.

## Minimum data contracts to finalize in Step 21.2

The exact schema must be reviewed against current SQLAlchemy conventions before
migration, but the runtime needs distinct boundaries for:

- conversations and messages;
- requests/runs and immutable execution attempts;
- user-selected Farm context/consent snapshots;
- technical model usage and cost;
- feedback and safety reports;
- governed knowledge sources, source versions, documents, chunks, and
  ingestion jobs;
- citations connecting an answer to immutable source versions/chunks;
- prompt/policy/model configuration versions;
- Admin Audit and retention/deletion jobs.

Embeddings must not be placed in MySQL JSON by default. Step 21.3 must choose a
retrieval store from measured scale, Persian retrieval quality, operational
cost, deletion support, and deployment topology. The choice is not guessed in
this audit.

## Safety, privacy, and quality gates

- Agricultural advice must state uncertainty and missing context.
- High-risk chemical recommendations require source citation, crop/pest/context
  validation, label/legal caveats, and human escalation.
- Emergency poisoning and immediate safety guidance is never paywalled.
- Retrieved text and Farm free-text are untrusted data, not system
  instructions; prompt injection is explicitly tested.
- Citations point to immutable, approved source versions and support source
  withdrawal.
- Cross-user Farm/context/conversation access is impossible by contract.
- A user can delete conversations and revoke future Farm-context use subject to
  documented Audit/financial retention boundaries.
- Safety blocks do not consume quota.
- A partial, empty, uncited-required, or validation-failed answer is not a
  billable success.
- Model answers are evaluated on a curated Persian agricultural test set before
  release; unit tests alone are insufficient.

## Approved Phase 21 sequence

1. **21.1 — Real-State Audit + Barzegar Product/Privacy Boundary**.
2. **21.2 — AI Core DB, Permissions, Retention + Provider-Neutral Contracts**.
3. **21.3 — Knowledge Source Governance, Ingestion + Persian Extraction**.
4. **21.4 — Retrieval Store, Chunking, Embeddings + Citation Contracts**.
5. **21.5 — Conversation, Request/Run + Idempotent Async Workflow**.
6. **21.6 — Selected Farm Context, Consent, Freshness + Privacy Hardening**.
7. **21.7 — Model Gateway, Prompt/Policy Registry + Routing**.
8. **21.8 — Subscription Quota, Technical Usage/Cost + Reconciliation**.
9. **21.9 — Agricultural Safety, Output Validation + Human Escalation**.
10. **21.10 — Image Analysis Boundary + Evidence-Gated Diagnosis**.
11. **21.11 — Smart Diary Suggestions + Farmer Reports**.
12. **21.12 — Mobile Barzegar Assistant**.
13. **21.13 — Admin Knowledge, Runs, Feedback + Safety Operations**.
14. **21.14 — Evaluation, Observability, Abuse + Concurrency Hardening**.
15. **21.15 — Docs, Postman + Runtime Regression**.
16. **21.16 — Barzegar Release Gate + Tag**.

## Step 21.1 completion

This audit authorizes architecture and sequencing only. It does not authorize
inventing an AI Provider, uploading private data, purchasing infrastructure,
ingesting unapproved PDFs, or enabling a production model.

Step 21.2 is next.

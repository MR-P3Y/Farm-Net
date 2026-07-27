# Codex Bootstrap for Farm-Net

Use this checklist whenever a new Codex task starts without previous chat
history.

## Repository

The authoritative project is:

```text
E:\Farm-Net
```

Do not confuse it with similarly named folders or empty repositories on drive C.

## Mandatory First Read

Before proposing or changing code, read:

1. `PROJECT_CONTEXT.md`
2. `docs/PROJECT_PROGRESS.md`
3. `README.md`
4. relevant module documentation and source files

Then inspect:

```powershell
git status --short --branch
git log --oneline --decorate -20
git tag --list
```

Also inspect relevant models, migrations, permission seed, schemas, repository,
service, routers, notification events, mobile/admin features, API docs, and
Postman collections.

## Before Editing

Report:

- repository path;
- current branch and HEAD;
- tracked and untracked Git status;
- latest relevant commits and tags;
- files that already implement the requested feature;
- the exact current step;
- proposed scope and verification plan.

Do not assume the latest chat handoff is current when repository evidence says
otherwise.

## Current Handoff

As of 2026-07-16:

```text
Windows environment recovery: completed
Step 17.1 Services DB + Permissions: completed (3b8af10)
Step 17.2 Categories + Provider Profiles: completed (0f3a07d)
Step 17.3 Service Offers backend: completed (c247d9d)
Step 17.4 Services Request Flow: completed (f1adaf5)
Step 17.5 Request Notifications + Contract Hardening: completed
Step 17.6 Mobile Service Discovery + Detail: completed
Step 17.7 Mobile Service Request Flow: completed
Step 17.8 Provider Profile + Offer Management Mobile: completed
Step 17.9 Provider Request Workbench: completed
Step 17.10 Admin Panel Services: completed (bda9699)
Step 17.11 Docs/Postman + Runtime Regression: completed
Step 17.12 Services Release Gate + Tag: completed (v0.17.0-services-foundation)
Phase 9.1 Orders/Payments audit: completed
Phase 9.2 Financial Contracts + DB Hardening: completed
Phase 9.3 Atomic Checkout + Inventory Reservation: completed
Phase 9.4 Checkout Idempotency + Contract Hardening: completed
Phase 9.5 Payment Orchestration + Idempotent Verify: completed
Phase 9.6 Refund Request + Idempotent Processing: completed
Phase 9.7 Admin Finance Read Models + Audit: completed
Phase 9.8 Admin Finance UI: completed
Phase 9.9 Mobile Payment UX + Contract Migration: completed
Phase 9.10 Docs/Postman + Release Regression: completed
Phase 9.11 Release Gate + Tag: completed (v0.18.0-orders-finance-foundation)
Phase 11.1 Notifications real-state audit: completed
Phase 11.2 Delivery Contracts + DB Hardening: completed (e72b9f4c31a6)
Phase 11.3 User Preferences + Channel Routing: completed (f84c2a1d9037)
Phase 11.4 Retry Queue + Failure/Delivery Logs: completed (a16d7c4e52b9)
Phase 11.5 Email Provider Foundation: completed
Phase 11.6 SMS Provider Foundation: completed
Phase 11.7 Push Notification Foundation: completed (b27e8d5f64c1)
Phase 11.8 Mobile Notification Center Hardening: completed
Phase 11.9 Admin Notification Operations: completed
Phase 11.10 Docs/Postman + Runtime Regression: completed
Phase 11.11 Notifications Release Gate + Tag: completed (v0.19.0-notifications-delivery-foundation)
Phase 12.1 Product Category Management: completed
Phase 12.2 Category Governance Alignment Audit: completed
Phase 12.3 Services Category Contract Hardening: completed
Phase 12.4 Social Category Management: completed
Phase 12.5 Consultant Specialty Usage + Admin Search Hardening: completed
Phase 12.6 Unified Admin Taxonomy Navigation + UX Consistency: completed
Phase 12.7 Docs/Postman + Runtime Regression: completed
Phase 12.8 Category Management Release Gate + Tag: completed (v0.20.0-category-management-foundation)
Phase 16.1 Equipment Rental Real-State Audit + Contract Boundary: completed
Phase 16.2 Rental DB + Permission Foundation: completed (104ae669cc1a)
Phase 16.3 Categories + Lessor Profile APIs: completed
Phase 16.4 Equipment Listing + Media APIs: completed
Phase 16.5 Availability + Pricing Rules: completed
Phase 16.6 Rental Request/Booking Workflow: completed
Phase 16.7 Notifications + Privacy/Concurrency Hardening: completed
Phase 16.8 Mobile Equipment Discovery + Detail: completed
Phase 16.9 Mobile Rental Request Flow: completed
Phase 16.10 Mobile Lessor Management + Request Workbench: completed
Phase 16.11 Admin Panel Equipment Rental: completed
Phase 16.12 Docs/Postman + Runtime Regression: completed
Phase 16.13 Equipment Rental Release Gate + Tag: completed (v0.21.0-equipment-rental-foundation)
Phase 20.1 Wallet/Settlement/Accounting Real-State Audit + Contract Boundary: completed
Phase 20.2 Canonical Money + Billable Source Contracts: completed (4c9a2f20b102)
Phase 20.3 Wallet Accounts + Double-Entry Ledger DB/Permissions: completed (c7e8a1f20303)
Phase 20.4 Order Finance Ledger Bridge + Reconciliation: completed (d9a4b2f20404)
Phase 20.5 Universal Invoice + Commission Foundation: completed (f7a6d4b20606)
Phase 20.6 Services/Consultation Final-Price Contracts: completed (b9c8d6e40808)
Phase 20.7 Rental Revenue + Deposit Accounting Boundaries: completed (ecba19a70b11)
Phase 20.8 Balance Release + Settlement/Payout Workflow: completed (fdcb2ab80c12)
Phase 20.9 Refund, Reversal, Adjustment + Concurrency Hardening: completed
Phase 20.10 Real Payment Gateway Adapter + Callback Verification: completed (disabled by default; credentialed sandbox smoke pending)
Phase 20.11 Financial Notifications + Privacy/Audit Hardening: completed
Phase 20.12 Mobile Wallet, Invoices, and Provider Settlements: completed
Phase 20.13 Admin Accounting, Settlement, and Reconciliation: completed
Phase 20.14 Docs/Postman + Runtime Financial Regression: completed
Phase 20.15 Wallet/Settlement/Accounting Release Gate + Tag: completed (v0.22.0-wallet-settlement-accounting-foundation)
Phase 18.1 Search/Filters/Discovery Real-State Audit + Contract Boundary: completed
Phase 18.2 Shared Search Contracts + Persian Query Normalization: completed
Phase 18.3 Product + Store Discovery Hardening: completed
Phase 18.4 Services Discovery Hardening: completed
Phase 18.5 Equipment Rental Discovery Hardening: completed
Phase 18.6 Consultant Discovery Hardening: completed
Phase 18.7 Social Discovery Hardening: completed
Phase 18.8 Unified Cross-Domain Search API + Ranking Boundary: completed
Phase 18.9 Mobile Unified Discovery Hub: completed
Phase 18.10 Performance, Privacy, and Abuse Hardening: completed
Phase 18.11 Docs/Postman + Runtime Search Regression: completed
Phase 18.12 Search/Filters/Discovery Release Gate + Tag: completed (v0.23.0-search-discovery-foundation)
Phase 23.1 Role-Based My Activity Center Real-State Audit: completed
Phase 23.2 Typed Role/Permission Activity Catalog: completed
Phase 23.3 Activity Center Shell + Common Personal Activity: completed
Phase 23.4 Shop Owner Center + Seller Order Workbench: completed
Phase 23.5 Service Provider Activity Integration: completed
Phase 23.6 Lessor Activity Integration: completed
Phase 23.7 Consultant Activity Integration: completed
Phase 23.8 Role Setup/Verification + Multi-Role Hardening: completed
Phase 23.9 Home Navigation Simplification + Deep-Link/Auth Hardening: completed
Phase 23.10 Docs, Tests, and Runtime Regression: completed
Phase 23.11 Role-Based My Activity Center Release Gate + Tag: completed (v0.24.0-activity-center-foundation)
Phase 19.1 Reviews/Ratings/Reports Real-State Audit + Contract Boundary: completed
Phase 19.2 Shared Review DB + Permission Foundation: completed (a7c9e1f30d13)
Phase 19.3 Eligibility, Ownership, Lifecycle + Review CRUD: completed
Phase 19.4 Public Reviews, Aggregates + Discovery Integration: completed
Phase 19.5 Review Reports, Admin Moderation + Audit Logs: completed
Phase 19.6 Notifications, Privacy, Exact-Once + Concurrency Hardening: completed
Phase 19.7 Mobile Review Creation, History + Public Rendering: completed
Phase 19.8 Admin Review/Report Moderation Panel: completed
Phase 19.9 Cross-Domain Contract + Runtime Hardening: completed
Phase 19.10 Docs, Postman + Runtime Regression: completed
Phase 19.11 Reviews/Ratings/Reports Release Gate + Tag: completed (v0.25.0-reviews-foundation)
Phase 21.1 Barzegar AI/RAG Real-State Audit + Product/Privacy Boundary: completed
Phase 21.2 AI Core DB, Permissions, Retention + Provider-Neutral Contracts: completed (a21c4b82a6e0)
Phase 21.3 Knowledge Source Governance, Ingestion + Persian Extraction: completed (b21d5c93b7f1)
Phase 21.4 Retrieval Store, Chunking, Embeddings + Citation Contracts: completed (c21e6d04c8a2)
Phase 21.5 Conversation, Request/Run + Idempotent Async Workflow: completed (d21f7e15d9b3)
Phase 21.6 Selected Farm Context, Consent, Freshness + Privacy Hardening: completed (e21a8f26e0c4)
Phase 22.1 Production Readiness Real-State Audit: completed
Phase 22.2 Release, Branch, Version + Documentation Governance: completed
Phase 22.3 Production Configuration, Secret + Dev-Switch Safety: completed
Phase 22.4 Database Drift, Migration + Backup/Restore Hardening: completed
Phase 22.5 Typed OpenAPI Response Contract Hardening: completed
Phase 22.6 Authentication, Session + Token Storage Hardening: completed
Phase 22.7 Abuse Protection, Security Headers + Transport Hardening: completed
Phase 22.8 Production Topology, Container + Worker Hardening: completed
Phase 22.9 Observability, Readiness, Metrics + Alerting: completed
Phase 22.10 Credentialed Staging Provider Verification: active/blocked on
external provider credentials and owner-approved staging test targets
Phase 24.1 Farm Management Real-State Audit + Domain/Privacy Boundary: completed
Phase 24.2 Crop/Measurement References, Permissions + DB Contract: completed
Phase 24.3 Owner-Scoped Farm CRUD + Archive Lifecycle: completed
Phase 24.4 Plot, Geo Point/Boundary + Area Consistency: completed
Phase 24.5 Crop Catalog, Varieties + Crop-Cycle Lifecycle: completed
Phase 24.6 Soil, Water, Irrigation + Laboratory Observations: completed
Phase 24.7 Operation Diary, Inputs, Harvest + Farm Media: completed
Phase 24.8 Privacy, Concurrency, Audit + Retention Hardening: completed
Phase 24.9 Farm Weather Linking + Contextual Alerts: completed
Phase 24.10 Mobile My Farms, Plots, Cycles + Diary: completed
Phase 24.11 Activity Center + Restricted Admin Support: completed
Phase 24.12 Docs, Postman + Runtime Regression: completed
Phase 24.13 Farm Management Release Gate + Tag: completed
Phase 24 Farm Management / Digital Farm Profiles: completed
Active product track: Phase 25 Unified Subscription & Entitlement Platform
Phase 25.1 Real-State Audit + AI Entitlement Boundary: completed
Phase 25.2 Plan, Feature, Subscription + Entitlement DB Contract: completed
Phase 25.3 Plan Catalog + Public/User Read APIs: completed
Phase 25.4 Subscription Lifecycle, Periods + Cancellation: completed
Phase 25.5 Atomic Quota Reservation, Usage + Idempotency: completed
Phase 25.6 TOMAN Invoice, Wallet + Payment Integration: completed
Phase 25.7 Renewal, Expiry, Grace Period + Notifications: completed
Phase 25.8 Mobile Plans, Current Subscription, Usage + Checkout: completed
Phase 25.9 Admin Plans, Subscriptions, Usage + Manual Operations: completed
Phase 25.10 Security, Concurrency, Audit + Reconciliation Hardening: completed
Phase 25.11 Docs, Postman + Runtime Regression: completed
Phase 25.12 Subscription Release Gate + Tag: completed (v0.27.0-subscriptions-foundation)
Phase 25 Unified Subscription & Entitlement Platform: completed
Active product track: Phase 21 farmer-focused AI/RAG as Barzegar (برزگر)
Phase 21.7 Model Gateway, Prompt/Policy Registry + Routing: completed.
Credentialed OpenAI activation is deferred because the Provider returned
`429 insufficient_quota` and the owner currently has no international payment
card. Keep `AI_PROVIDER_ENABLED=false` until quota exists and a live smoke
succeeds. Next: Phase 21.8 Subscription Quota, Technical Usage/Cost +
Reconciliation. Evidence: `docs/ai/phase-21-model-gateway-routing.md`.
Phase 21.8 Subscription Quota, Technical Usage/Cost + Reconciliation:
completed. Barzegar uses Phase 25 Entitlements/reservations, finalizes only
usable success, releases terminal failure/cancellation, records exact-once
technical usage, and permits only configured TOMAN cost rates. Next: Phase
21.9 Agricultural Safety, Output Validation + Human Escalation. Evidence:
`docs/ai/phase-21-subscription-quota-usage.md`.
Phase 21.9 Agricultural Safety, Output Validation + Human Escalation:
completed. Emergency poisoning is unmetered; high-risk chemical output is
evidence-gated; human escalation is explicit and uses real Consult Requests.
Next: Phase 21.10 Image Analysis Boundary + Evidence-Gated Diagnosis.
Phase 21.10 Image Analysis Boundary + Evidence-Gated Diagnosis: completed.
Owner-scoped Media evidence is bounded and immutable; image conclusions require
visible evidence, uncertainty, and human review. Next: Phase 21.11 Smart Diary
Suggestions + Farmer Reports.
Phase 21.11 Smart Diary Suggestions + Farmer Reports: completed at Alembic head
`k21g8e5c1029`. Context is mandatory; smart-diary output becomes a typed,
owner-private pending suggestion and is written to the real audited Farm diary
only after explicit owner acceptance. Reports are exact-once owner artifacts
with real operation/input/harvest count snapshots. Verification: Ruff,
compileall, 368 backend tests, migration and database/Redis health passed.
OpenAI live generation remains disabled until billing is activated. Next:
Phase 21.12 Mobile Barzegar Assistant.
Evidence: `docs/ai/phase-21-smart-diary-reports.md`.
Phase 21.12 Mobile Barzegar Assistant: completed. Authenticated Home exposes
`/barzegar` with typed support for all six request kinds, explicit 24-hour
Farm/Plot/Cycle context, private image upload, request refresh, farmer-confirmed
diary suggestions, and snapshot-backed reports. Permission, subscription/quota,
safety, Provider-disabled, loading, empty, and error states are rendered.
Flutter analyze, 72 tests, and Web build/Wasm dry run passed. Next: Phase 21.13
Admin Barzegar Governance. Evidence: `docs/ai/phase-21-mobile-barzegar.md`.
```

Services means agricultural operational services, not equipment rental.

## Change Rules

- Modify only files required for the authorized step.
- Preserve unrelated tracked and untracked changes.
- Never stage or commit `.env`, secrets, build output, caches, local storage,
  uploaded media, DB dumps, or generated package metadata.
- If `backend/app/common.zip` exists, do not touch, stage, or commit it.
- Do not use destructive Git commands, delete Docker volumes, or replace the
  repository without explicit authorization.
- Do not commit or tag unless the user explicitly requests it.

## Implementation Pipeline

Follow this order unless repository evidence requires a narrower corrective
step:

1. DB model and Alembic migration
2. permission seed and role assignment
3. schemas
4. repository
5. domain service and status transitions
6. public/user/provider APIs
7. admin APIs
8. notification events and delivery triggers
9. mobile UI
10. admin-panel UI
11. API docs and Postman
12. compile, lint/analyze, tests, migration, health, and smoke checks
13. progress documentation
14. clean step-based commit/tag when explicitly authorized

## Verification Report

For each implementation step, provide:

- commands run and concise results;
- backend compile/lint/test results;
- Alembic heads/current/upgrade result when DB changes are involved;
- seed result when permissions change;
- Flutter analyze/test/build results for affected apps;
- health and feature smoke results;
- OpenAPI route count or contract check;
- final `git status`, separating intended source changes from generated or
  unrelated files.

Never describe a foundation as production-ready unless real external providers,
security controls, tests, deployment, monitoring, and operational verification
actually support that claim.

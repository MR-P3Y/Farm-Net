# Phase 21.4 — Retrieval, Chunking, Embeddings and Citations

Verified: 2026-07-27

## Outcome

Barzegar now has a provider-neutral retrieval foundation with deterministic
Persian page chunking, external vector storage, embedding model/version
governance, approved-source filtering, removal contracts, and immutable
response citations.

No production embedding model, model credential, LLM call, or automatic
ingestion of the candidate PDFs is enabled by this step.

## Storage decision

MySQL remains the authoritative governance and lineage database. Vector arrays
are never stored in MySQL JSON. Qdrant `v1.18.2` is the selected external vector
store and is pinned in the development Compose topology.

The decision is based on the current 30-document/1,245-page corpus and these
required properties:

- collections enforce vector dimensions and distance metric;
- payload filters allow `approved`, `active`, and `source_version_id` gates;
- points can be removed when a version is withdrawn;
- local Docker deployment uses persistent storage;
- the adapter remains behind a Farm-Net Protocol, so application contracts do
  not expose Qdrant-specific objects.

Operational references:

- https://qdrant.tech/documentation/manage-data/collections/
- https://qdrant.tech/documentation/concepts/payload/
- https://qdrant.tech/documentation/installation/

The development port is bound to `127.0.0.1`. Production must add
authentication, encrypted transport, backup/restore, monitoring, and an
approved HA topology before activation.

## Database contract

Migration `c21e6d04c8a2` adds:

- `ai_knowledge_chunks`;
- `ai_embedding_models`;
- `ai_embedding_index_records`;
- `ai_response_citations`.

MySQL stores source lineage, stable offsets/checksums, model version,
collection/point identity, vector checksum, index lifecycle, and citation
snapshots. It does not store the vector payload.

Only one embedding model may be globally active. Chunk/model and
store/collection/point identities are unique. Citations are unique by response
order and chunk.

## Governance gates

- source and source version must both be `approved`;
- document extraction must be `succeeded`;
- pages marked `needs_review` cannot be chunked;
- source/version/document/page lineage must match;
- retrieval queries cannot disable `approved_only`;
- the Qdrant adapter always filters `approved=true` and `active=true`;
- quoted citation text must be an exact substring of its immutable chunk.

## Persian chunking

`barzegar-fa-page-v1` creates deterministic page-bounded chunks with stable
character offsets, SHA-256, bounded overlap, and a conservative token estimate.
Chunks never silently cross page boundaries, preserving exact page citations.

## Runtime evidence

- Qdrant `v1.18.2` started with a persistent named volume;
- collection create, approved-point upsert, filtered query, score, point
  removal, collection cleanup, and `/healthz` passed;
- MySQL migration and no-drift passed;
- Auth seed twice remained idempotent at 12 roles and 284 permissions.
- All 338 Backend tests, Ruff/compileall, app/database/Redis health, and Qdrant
  health passed.

## Next

Step 21.5 — Conversation, Request/Run + Idempotent Async Workflow.

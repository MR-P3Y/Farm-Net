# Phase 22.2 — Release, Branch, Version + Documentation Governance

Date: 2026-07-24

## Purpose

This policy separates development milestones from production releases and
establishes one source of truth for branches, tags, versions, and release
documentation.

## Branch authority

| Ref | Purpose | Allowed state |
| --- | --- | --- |
| `develop` | Integration and next-version development | May be ahead of the latest stable tag |
| `release/vX.Y.Z` | Frozen release candidate | Fixes, version/release notes, and gate changes only |
| `main` | Latest approved stable source | Must point to a tested release commit, never arbitrary development HEAD |
| `hotfix/vX.Y.Z` | Urgent stable correction | Created from `main`, merged back to both `main` and `develop` |

Feature work enters `develop` through reviewed branches. Direct history
rewrites are forbidden. Promotion to `main` must be a fast-forward or reviewed
merge from the approved release commit and must not include commits made after
the release tag.

## Tag classes

Historical `*-foundation` tags through `v0.25.0-reviews-foundation` are
development foundation milestones. They prove their recorded local/runtime
gate, but do not retroactively claim staging deployment, backup, or production
traffic.

From Phase 22 onward:

- a foundation/milestone tag may be created on `develop` only when explicitly
  labelled as non-production;
- a production release tag requires the complete Definition of Done, staging
  evidence, release branch, backup/rollback evidence, `main` promotion, release
  notes, and post-deploy smoke test;
- tags are annotated, immutable, and never moved or recreated.

## Version authority

The product uses one release line across all surfaces. Tool-specific syntax may
differ while representing the same version:

| Surface | Development version |
| --- | --- |
| Product/runtime | `0.26.0-dev.1` |
| Backend package (PEP 440) | `0.26.0.dev1` |
| Mobile/Admin pubspec | `0.26.0-dev.1+26` |

The build suffix is client build metadata, not a different product version.
Production `v0.26.0` must use release metadata (`0.26.0`, with an approved
client build number) before its tag.

Release gates must compare:

- Git release version/tag;
- FastAPI OpenAPI `info.version`;
- Backend package metadata;
- Mobile version/build;
- Admin version/build;
- release notes and deployment artifact labels.

No runtime secret `.env` is edited or committed. Operators set `APP_VERSION`
from the release manifest; `.env.example` documents the development default.

## Stable-main recovery

Before this step, `main` was 122 commits behind `develop` and remained at the
Phase 13 merge. The safe recovery target is the existing annotated stable
milestone `v0.25.0-reviews-foundation` (`756e7ea`), not the later Phase 22 audit
commit. This keeps `main` on a known tested commit while `develop` continues
with Phase 22 work.

No historical tag or commit is rewritten. Future stable promotion follows the
release-branch workflow above.

## Roadmap identity

Roadmap phase numbers, historical implementation step numbers, and semantic
release versions are different identifiers:

- phase number describes product sequencing;
- step number records the historical implementation track;
- semantic version/tag identifies a source release.

Historical names such as Services Steps 17.x and Category Management Phase 12
remain unchanged for traceability. New documentation must use the canonical
module name in addition to its number and must not infer implementation status
from a permission seed or tag number alone.

## Required checks

Every future release gate must fail when:

- working tree or index is not clean;
- the candidate is not synchronized/pushed;
- version metadata disagrees;
- release notes or migration state are missing;
- the release tag already exists;
- `main` promotion would not be fast-forward/reviewed;
- staging, backup/rollback, or post-deploy evidence is absent for a production
  release.

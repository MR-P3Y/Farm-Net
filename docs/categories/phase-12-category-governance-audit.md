# Phase 12.2 — Category Governance Alignment Audit

## Decision

Farm-Net must keep categories inside their owning bounded context. Product
categories, Service categories, Consultant specialties, and Social categories
must not be merged into one polymorphic table. They have different relations,
permissions, hierarchy needs, and lifecycle rules.

The shared target is an Admin experience and governance contract, not a shared
database model.

## Verified matrix

| Capability | Products | Services | Consultants | Social |
| --- | --- | --- | --- | --- |
| Public active list | Yes | Yes | Yes | Yes |
| Admin list/create/update | Yes | Yes | Yes | No |
| Typed Admin UI | Yes | Yes | Yes | No |
| Parent/child hierarchy | Yes | Yes | Not needed | Not needed |
| Self-parent prevention | Yes | Yes | N/A | N/A |
| Full cycle prevention | Yes | No | N/A | N/A |
| Clear an existing parent | Yes | Incomplete | N/A | N/A |
| Search contract | Yes | Yes | Yes | No |
| Usage counters | Yes | No | No | No |
| Non-destructive active state | Yes | Yes | Yes | Model only |
| Seed preserves Admin edits | Yes | No | No default seed found | No |
| Domain-specific permissions | Yes | Yes | Yes | No category permissions |

Runtime OpenAPI confirms all three Product/Services/Consultants management
contracts and confirms that Social Admin category paths do not exist. The local
runtime database currently has zero active rows in Services, Consultants, and
Social, so seed/runtime readiness must be addressed explicitly rather than
assuming reference data exists.

## Domain findings

### Services

The model and Admin UI already support hierarchy and activation. Hardening is
required because update only rejects direct self-parenting; it does not reject
longer cycles. An existing parent cannot be explicitly cleared by the current
partial-update contract. The default seed also renames, reorders, and
reactivates managed rows on every run. Usage counters are not
exposed for provider links, offers, requests, or direct children.

### Consultant specialties

The flat model is appropriate. Public and Admin APIs plus typed Admin UI exist.
The Admin client does not expose the Backend search capability, and there are no
profile/request usage counters. `consult_specialties.delete` exists in the seed
but no delete API was found; deactivation should remain the safe lifecycle.

### Social categories

Only active public listing and post filtering exist. There is no Admin category
API, category-specific permission, typed Admin UI, search, or usage count. The
default seed overwrites title, description, order, and active state, which would
undo future Admin changes.

## Shared governance standard

Every manageable taxonomy should provide:

1. stable normalized code/slug uniqueness;
2. public active-only discovery;
3. permission-protected Admin list/create/update;
4. search, sort order, and active/inactive state;
5. non-destructive lifecycle by default;
6. usage counters relevant to that domain;
7. seed-create-missing behavior that never overwrites Admin-owned rows;
8. typed Admin UI with loading, empty, validation, permission, and error states;
9. focused model/contract tests, OpenAPI documentation, and Postman coverage;
10. hierarchy cycle prevention only for domains that actually use hierarchy.

## Authorized implementation sequence

```text
12.3 Services Category Contract Hardening
12.4 Social Category Management
12.5 Consultant Specialty Usage + Admin Search Hardening
12.6 Unified Admin Taxonomy Navigation + UX Consistency
12.7 Docs/Postman + Runtime Regression
12.8 Category Management Release Gate + Tag
```

No production data, API behavior, UI behavior, permissions, or schema was
changed during this audit.

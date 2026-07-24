# Database Docs

مستندات طراحی دیتابیس، migrationها، جدول‌ها، status flowها و indexهای مهم در این پوشه قرار می‌گیرد.

## Marketplace Reviews foundation

Alembic revision `a7c9e1f30d13` adds the shared Phase 19 Review, rating
aggregate, Review report, and moderation-log tables. The detailed constraints,
permission boundary, verification evidence, and polymorphic identity decision
are documented in `docs/reviews/phase-19-review-db-permissions.md`.

## Production drift hardening

Alembic revision `b8d4f2c71e04` removes four redundant unnamed unique indexes
left by the original Consultants and Services migrations while retaining the
canonical named unique indexes and all uniqueness behavior. Downgrade,
upgrade, autogenerate drift check, backup, and isolated restore evidence are
documented in
`docs/production/database-backup-restore-hardening.md`.

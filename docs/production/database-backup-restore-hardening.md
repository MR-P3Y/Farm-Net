# Step 22.4 — Database Drift, Migration + Backup/Restore Hardening

Date: 2026-07-24
Branch: `develop`

## Database drift

Alembic autogenerate reported four duplicate unique indexes. The original
Consultants and Services migrations created both a named unique index and an
unnamed unique constraint for the same column:

| Table | Column | Canonical index retained |
|---|---|---|
| `consult_specialties` | `code` | `ix_consult_specialties_code` |
| `consult_profiles` | `user_id` | `ix_consult_profiles_user_id` |
| `service_categories` | `code` | `ix_service_categories_code` |
| `service_provider_profiles` | `user_id` | `ix_service_provider_profiles_user_id` |

Revision `b8d4f2c71e04` removes only the redundant unnamed indexes. It does not
change uniqueness, API behavior, data, or model contracts. Downgrade recreates
the removed indexes. Downgrade/upgrade and `alembic check` passed; the database
has one named unique index for each contract.

## Backup contract

Run from the repository root:

```powershell
py -3 scripts\backup\farmnet_backup.py
```

The command creates an atomic, Git-ignored directory under `backups/` with:

- `database.sql.gz`: transactional MySQL dump including routines, triggers,
  events, and binary-safe values;
- `media.tar.gz`: local Media storage, with symbolic links rejected;
- `manifest.json`: format version, UTC timestamp, Git commit, byte sizes, and
  SHA-256 checksums.

MySQL credentials are expanded only inside the database container. They are
not passed as host-side secret values and are never written to the manifest.
A failed backup does not publish a final backup directory.

For production, copy the completed backup to encrypted off-host/object
storage, apply retention policy, restrict access, and monitor scheduled job
results. This step supplies and validates the recovery mechanism; production
scheduling and infrastructure remain part of later deployment work.

## Restore contract

The default operation is read-only verification:

```powershell
py -3 scripts\backup\farmnet_restore.py backups\<backup-directory>
```

It verifies manifest version, both sizes and SHA-256 checksums, and rejects
absolute paths, traversal, links, and device entries in the Media archive.

An actual database restore requires the explicit confirmation phrase and a
validated database name:

```powershell
py -3 scripts\backup\farmnet_restore.py backups\<backup-directory> `
  --apply-database --create-database --database farmnet_restore_test `
  --confirm RESTORE_FARMNET_BACKUP
```

`--create-database` uses the container's administrative account only to create
and populate the new isolated database. Restoring to an existing database uses
the restricted application account. Media restore also requires the
confirmation phrase and refuses a non-empty destination.

Never restore directly over production first. Verify the backup, restore into
an isolated database, run schema/application checks, take a fresh pre-change
backup, announce a maintenance window, and only then perform a controlled
production recovery.

## Verification evidence

- Migration downgrade `b8d4f2c71e04 -> a7c9e1f30d13`: passed.
- Migration upgrade back to `b8d4f2c71e04`: passed.
- `alembic check`: no new upgrade operations detected.
- Canonical unique-index inspection: passed for all four tables.
- Backup creation and checksum/archive verification: passed.
- Restore into isolated `farmnet_restore_22_4`: passed with 98 tables.
- Isolated drill database cleanup: passed.
- Backup helper safety tests: 8 passed.
- Backend Ruff: passed.
- Backend compileall: passed.
- Backend tests: 193 passed with 18 known warnings.
- Runtime health: app, database, and Redis `ok`.

The generated drill backup remains local and ignored by Git; it is not release
source and must not be committed.

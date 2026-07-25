# Backup and restore

Create an atomic MySQL and media backup:

```powershell
py -3 scripts\backup\farmnet_backup.py
```

Verify checksums and archive safety without changing any data:

```powershell
py -3 scripts\backup\farmnet_restore.py backups\<backup-directory>
```

Restore the database only after explicit confirmation, preferably to a new
isolated database first:

```powershell
py -3 scripts\backup\farmnet_restore.py backups\<backup-directory> `
  --apply-database --create-database --database farmnet_restore_test `
  --confirm RESTORE_FARMNET_BACKUP
```

Credentials are read inside the MySQL container and are never stored in the
backup manifest. See `docs/production/database-backup-restore-hardening.md`
before using restore in an operational environment.

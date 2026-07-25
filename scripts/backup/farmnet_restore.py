from __future__ import annotations

import argparse
import gzip
import shutil
import subprocess
from pathlib import Path

from backup_lib import (
    extract_media_archive,
    load_and_validate_manifest,
    validate_database_name,
    validate_media_archive,
)


CONFIRMATION = "RESTORE_FARMNET_BACKUP"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify or restore a Farm-Net backup")
    parser.add_argument("backup_dir", type=Path)
    parser.add_argument("--mysql-container", default="farmnet_mysql")
    parser.add_argument("--database")
    parser.add_argument("--create-database", action="store_true")
    parser.add_argument("--apply-database", action="store_true")
    parser.add_argument("--restore-media-to", type=Path)
    parser.add_argument("--confirm")
    return parser.parse_args()


def mysql_command(container: str, database: str, *, admin: bool = False) -> list[str]:
    credentials = (
        '-uroot -p"$MYSQL_ROOT_PASSWORD"'
        if admin
        else '-u"$MYSQL_USER" -p"$MYSQL_PASSWORD"'
    )
    shell_command = (
        f'exec mysql {credentials} "$RESTORE_DATABASE"'
    )
    return ["docker", "exec", "-i", "-e", f"RESTORE_DATABASE={database}", container, "sh", "-c", shell_command]


def mysql_admin_command(container: str, statement: str) -> list[str]:
    return [
        "docker",
        "exec",
        "-i",
        container,
        "sh",
        "-c",
        f'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -e \'{statement}\'',
    ]


def restore_database(container: str, database: str, dump_path: Path, create: bool) -> None:
    database = validate_database_name(database)
    if create:
        subprocess.run(
            mysql_admin_command(
                container,
                f"CREATE DATABASE `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci",
            ),
            check=True,
        )
    process = subprocess.Popen(
        mysql_command(container, database, admin=create),
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert process.stdin is not None
    with gzip.open(dump_path, "rb") as dump:
        shutil.copyfileobj(dump, process.stdin)
    process.stdin.close()
    stderr = process.stderr.read() if process.stderr is not None else b""
    return_code = process.wait()
    if return_code:
        raise RuntimeError(f"Database restore failed: {stderr.decode(errors='replace').strip()}")


def main() -> int:
    args = parse_args()
    backup_dir = args.backup_dir.resolve()
    manifest = load_and_validate_manifest(backup_dir)
    media_path = backup_dir / manifest["media"]["file"]
    validate_media_archive(media_path)
    wants_restore = args.apply_database or args.restore_media_to is not None
    if wants_restore and args.confirm != CONFIRMATION:
        raise ValueError(f"Restore requires --confirm {CONFIRMATION}")
    if args.apply_database:
        if not args.database:
            raise ValueError("--database is required with --apply-database")
        restore_database(
            args.mysql_container,
            args.database,
            backup_dir / manifest["database"]["file"],
            args.create_database,
        )
    if args.restore_media_to is not None:
        extract_media_archive(media_path, args.restore_media_to.resolve())
    print("Backup verification: OK" if not wants_restore else "Restore: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

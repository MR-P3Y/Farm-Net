from __future__ import annotations

import argparse
import gzip
import json
import os
import shutil
import subprocess
import tarfile
from datetime import UTC, datetime
from pathlib import Path

from backup_lib import BACKUP_FORMAT_VERSION, artifact_metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a verified Farm-Net database and media backup")
    parser.add_argument("--output-root", type=Path, default=Path("backups"))
    parser.add_argument("--media-dir", type=Path, default=Path("backend/storage/media"))
    parser.add_argument("--mysql-container", default="farmnet_mysql")
    return parser.parse_args()


def run_checked(command: list[str], **kwargs: object) -> subprocess.CompletedProcess:
    return subprocess.run(command, check=True, **kwargs)


def create_database_dump(container: str, destination: Path) -> None:
    command = [
        "docker",
        "exec",
        container,
        "sh",
        "-c",
        'exec mysqldump --single-transaction --quick --routines --triggers '
        '--events --hex-blob --default-character-set=utf8mb4 '
        '-u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"',
    ]
    with destination.open("wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as compressed:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert process.stdout is not None
        shutil.copyfileobj(process.stdout, compressed)
        stderr = process.communicate()[1]
    if process.returncode:
        raise RuntimeError(f"mysqldump failed: {stderr.decode(errors='replace').strip()}")


def create_media_archive(source: Path, destination: Path) -> None:
    source = source.resolve()
    if source.exists() and not source.is_dir():
        raise ValueError("Media source must be a directory")
    if source.exists():
        for item in source.rglob("*"):
            if item.is_symlink():
                raise ValueError(f"Media backup refuses symbolic links: {item}")
    with tarfile.open(destination, "w:gz") as archive:
        if source.exists():
            archive.add(source, arcname="media", recursive=True)
        else:
            info = tarfile.TarInfo("media")
            info.type = tarfile.DIRTYPE
            info.mode = 0o750
            archive.addfile(info)


def main() -> int:
    args = parse_args()
    output_root = args.output_root.resolve()
    media_dir = args.media_dir.resolve()
    if output_root == media_dir or media_dir in output_root.parents:
        raise ValueError("Backup output must not be inside the media source")
    output_root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    final_dir = output_root / f"farmnet-backup-{timestamp}"
    temporary_dir = output_root / f".farmnet-backup-{timestamp}.tmp"
    if final_dir.exists() or temporary_dir.exists():
        raise FileExistsError("Backup destination already exists")
    temporary_dir.mkdir(mode=0o700)
    try:
        database_path = temporary_dir / "database.sql.gz"
        media_path = temporary_dir / "media.tar.gz"
        create_database_dump(args.mysql_container, database_path)
        create_media_archive(media_dir, media_path)
        git_commit = run_checked(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True
        ).stdout.strip()
        manifest = {
            "format_version": BACKUP_FORMAT_VERSION,
            "created_at_utc": datetime.now(UTC).isoformat(),
            "git_commit": git_commit,
            "database": artifact_metadata(database_path),
            "media": artifact_metadata(media_path),
        }
        manifest_path = temporary_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        for path in (database_path, media_path, manifest_path):
            try:
                os.chmod(path, 0o600)
            except OSError:
                pass
        temporary_dir.rename(final_dir)
    except Exception:
        if temporary_dir.exists() and temporary_dir.parent == output_root:
            shutil.rmtree(temporary_dir)
        raise
    print(final_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

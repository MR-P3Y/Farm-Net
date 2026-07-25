from __future__ import annotations

import hashlib
import json
import re
import tarfile
from pathlib import Path
from typing import Any


BACKUP_FORMAT_VERSION = 1
DATABASE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_]+$")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact_metadata(path: Path) -> dict[str, Any]:
    return {
        "file": path.name,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def load_and_validate_manifest(backup_dir: Path) -> dict[str, Any]:
    manifest_path = backup_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("format_version") != BACKUP_FORMAT_VERSION:
        raise ValueError("Unsupported backup format version")
    for key in ("database", "media"):
        artifact = manifest.get(key)
        if not isinstance(artifact, dict):
            raise ValueError(f"Manifest is missing {key} metadata")
        path = backup_dir / str(artifact.get("file", ""))
        if path.parent.resolve() != backup_dir.resolve() or not path.is_file():
            raise ValueError(f"Invalid {key} artifact path")
        if path.stat().st_size != artifact.get("bytes"):
            raise ValueError(f"{key} artifact size mismatch")
        if sha256_file(path) != artifact.get("sha256"):
            raise ValueError(f"{key} artifact checksum mismatch")
    return manifest


def validate_database_name(value: str) -> str:
    if not DATABASE_NAME_PATTERN.fullmatch(value):
        raise ValueError("Database name may contain only letters, digits, and underscores")
    return value


def validate_media_archive(path: Path) -> None:
    with tarfile.open(path, "r:gz") as archive:
        for member in archive.getmembers():
            member_path = Path(member.name)
            if (
                member_path.is_absolute()
                or ".." in member_path.parts
                or member.issym()
                or member.islnk()
                or member.isdev()
            ):
                raise ValueError(f"Unsafe media archive member: {member.name}")


def extract_media_archive(path: Path, destination: Path) -> None:
    validate_media_archive(path)
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise ValueError("Media restore destination must be empty")
    with tarfile.open(path, "r:gz") as archive:
        archive.extractall(destination, filter="data")

import io
import json
import tarfile
from pathlib import Path

import pytest

from backup_lib import (
    BACKUP_FORMAT_VERSION,
    artifact_metadata,
    load_and_validate_manifest,
    validate_database_name,
    validate_media_archive,
)


def write_manifest(backup_dir: Path) -> None:
    manifest = {
        "format_version": BACKUP_FORMAT_VERSION,
        "database": artifact_metadata(backup_dir / "database.sql.gz"),
        "media": artifact_metadata(backup_dir / "media.tar.gz"),
    }
    (backup_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


def test_manifest_checks_both_artifacts(tmp_path: Path) -> None:
    (tmp_path / "database.sql.gz").write_bytes(b"database")
    with tarfile.open(tmp_path / "media.tar.gz", "w:gz") as archive:
        archive.addfile(tarfile.TarInfo("media"))
    write_manifest(tmp_path)

    assert load_and_validate_manifest(tmp_path)["format_version"] == 1

    (tmp_path / "database.sql.gz").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="database artifact"):
        load_and_validate_manifest(tmp_path)


def test_unsafe_media_member_is_rejected(tmp_path: Path) -> None:
    archive_path = tmp_path / "media.tar.gz"
    with tarfile.open(archive_path, "w:gz") as archive:
        payload = b"unsafe"
        member = tarfile.TarInfo("../escape")
        member.size = len(payload)
        archive.addfile(member, io.BytesIO(payload))

    with pytest.raises(ValueError, match="Unsafe media archive member"):
        validate_media_archive(archive_path)


@pytest.mark.parametrize("value", ["farmnet_restore_1", "FarmNet2026"])
def test_database_name_accepts_safe_values(value: str) -> None:
    assert validate_database_name(value) == value


@pytest.mark.parametrize("value", ["farmnet-db", "db;DROP", "../db", "db name"])
def test_database_name_rejects_unsafe_values(value: str) -> None:
    with pytest.raises(ValueError, match="Database name"):
        validate_database_name(value)

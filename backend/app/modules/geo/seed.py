from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.modules.geo.models import (
    GeoCity,
    GeoCounty,
    GeoDistrict,
    GeoProvince,
    GeoRuralDistrict,
    GeoVillage,
)


@dataclass(frozen=True)
class GeoSeedResult:
    provinces: int
    counties: int
    districts: int
    rural_districts: int
    cities: int
    villages: int


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        return [
            {str(key).strip(): (value or "").strip() for key, value in row.items()}
            for row in reader
        ]


def _required(row: dict[str, str], key: str, file_name: str) -> str:
    value = row.get(key, "").strip()
    if not value:
        raise ValueError(f"Missing required column '{key}' in {file_name}: {row}")
    return value


def _optional(row: dict[str, str], key: str) -> str | None:
    value = row.get(key, "").strip()
    return value or None


def _to_int(value: str, *, field: str, file_name: str) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"Invalid integer for '{field}' in {file_name}: {value}") from exc


def _upsert_by_amar_code(
    db: Session,
    model: type,
    *,
    amar_code: str,
    values: dict[str, Any],
):
    instance = db.query(model).filter(model.amar_code == amar_code).one_or_none()

    if instance is None:
        instance = model(
            amar_code=amar_code,
            **values,
        )
        db.add(instance)
        db.flush()
        return instance

    for key, value in values.items():
        setattr(instance, key, value)

    db.flush()
    return instance


def seed_geo(csv_dir: str | Path, db: Session) -> GeoSeedResult:
    base = Path(csv_dir)

    province_source_to_db: dict[int, int] = {}
    county_source_to_db: dict[int, int] = {}
    district_source_to_db: dict[int, int] = {}
    rural_district_source_to_db: dict[int, int] = {}

    # 1) Provinces / ostan.csv
    province_rows = _read_csv(base / "ostan.csv")

    for row in province_rows:
        source_id = _to_int(
            _required(row, "id", "ostan.csv"),
            field="id",
            file_name="ostan.csv",
        )
        name = _required(row, "name", "ostan.csv")
        amar_code = _required(row, "amar_code", "ostan.csv")

        province = _upsert_by_amar_code(
            db,
            GeoProvince,
            amar_code=amar_code,
            values={
                "name": name,
                "is_active": True,
            },
        )

        province_source_to_db[source_id] = province.id

    # 2) Counties / shahrestan.csv
    county_rows = _read_csv(base / "shahrestan.csv")

    for row in county_rows:
        source_id = _to_int(
            _required(row, "id", "shahrestan.csv"),
            field="id",
            file_name="shahrestan.csv",
        )
        province_source_id = _to_int(
            _required(row, "ostan", "shahrestan.csv"),
            field="ostan",
            file_name="shahrestan.csv",
        )
        name = _required(row, "name", "shahrestan.csv")
        amar_code = _required(row, "amar_code", "shahrestan.csv")

        province_id = province_source_to_db.get(province_source_id)
        if province_id is None:
            raise ValueError(
                f"Missing province source id {province_source_id} for county {source_id}"
            )

        county = _upsert_by_amar_code(
            db,
            GeoCounty,
            amar_code=amar_code,
            values={
                "province_id": province_id,
                "name": name,
                "is_active": True,
            },
        )

        county_source_to_db[source_id] = county.id

    # 3) Districts / bakhsh.csv
    district_rows = _read_csv(base / "bakhsh.csv")

    for row in district_rows:
        source_id = _to_int(
            _required(row, "id", "bakhsh.csv"),
            field="id",
            file_name="bakhsh.csv",
        )
        province_source_id = _to_int(
            _required(row, "ostan", "bakhsh.csv"),
            field="ostan",
            file_name="bakhsh.csv",
        )
        county_source_id = _to_int(
            _required(row, "shahrestan", "bakhsh.csv"),
            field="shahrestan",
            file_name="bakhsh.csv",
        )

        name = _required(row, "name", "bakhsh.csv")
        amar_code = _required(row, "amar_code", "bakhsh.csv")

        province_id = province_source_to_db.get(province_source_id)
        county_id = county_source_to_db.get(county_source_id)

        if province_id is None:
            raise ValueError(
                f"Missing province source id {province_source_id} for district {source_id}"
            )
        if county_id is None:
            raise ValueError(
                f"Missing county source id {county_source_id} for district {source_id}"
            )

        district = _upsert_by_amar_code(
            db,
            GeoDistrict,
            amar_code=amar_code,
            values={
                "province_id": province_id,
                "county_id": county_id,
                "name": name,
                "is_active": True,
            },
        )

        district_source_to_db[source_id] = district.id

    # 4) Rural districts / dehestan.csv
    rural_rows = _read_csv(base / "dehestan.csv")

    for row in rural_rows:
        source_id = _to_int(
            _required(row, "id", "dehestan.csv"),
            field="id",
            file_name="dehestan.csv",
        )
        province_source_id = _to_int(
            _required(row, "ostan", "dehestan.csv"),
            field="ostan",
            file_name="dehestan.csv",
        )
        county_source_id = _to_int(
            _required(row, "shahrestan", "dehestan.csv"),
            field="shahrestan",
            file_name="dehestan.csv",
        )
        district_source_id = _to_int(
            _required(row, "bakhsh", "dehestan.csv"),
            field="bakhsh",
            file_name="dehestan.csv",
        )

        name = _required(row, "name", "dehestan.csv")
        amar_code = _required(row, "amar_code", "dehestan.csv")

        province_id = province_source_to_db.get(province_source_id)
        county_id = county_source_to_db.get(county_source_id)
        district_id = district_source_to_db.get(district_source_id)

        if province_id is None:
            raise ValueError(
                f"Missing province source id {province_source_id} for rural district {source_id}"
            )
        if county_id is None:
            raise ValueError(
                f"Missing county source id {county_source_id} for rural district {source_id}"
            )
        if district_id is None:
            raise ValueError(
                f"Missing district source id {district_source_id} for rural district {source_id}"
            )

        rural = _upsert_by_amar_code(
            db,
            GeoRuralDistrict,
            amar_code=amar_code,
            values={
                "province_id": province_id,
                "county_id": county_id,
                "district_id": district_id,
                "name": name,
                "is_active": True,
            },
        )

        rural_district_source_to_db[source_id] = rural.id

    # 5) Cities / shahr.csv
    city_rows = _read_csv(base / "shahr.csv")

    for row in city_rows:
        source_id = _required(row, "id", "shahr.csv")
        province_source_id = _to_int(
            _required(row, "ostan", "shahr.csv"),
            field="ostan",
            file_name="shahr.csv",
        )
        county_source_id = _to_int(
            _required(row, "shahrestan", "shahr.csv"),
            field="shahrestan",
            file_name="shahr.csv",
        )
        district_source_id_raw = _optional(row, "bakhsh")

        name = _required(row, "name", "shahr.csv")
        city_type = _optional(row, "shahr_type")
        amar_code = _required(row, "amar_code", "shahr.csv")

        province_id = province_source_to_db.get(province_source_id)
        county_id = county_source_to_db.get(county_source_id)

        if province_id is None:
            raise ValueError(
                f"Missing province source id {province_source_id} for city {source_id}"
            )
        if county_id is None:
            raise ValueError(
                f"Missing county source id {county_source_id} for city {source_id}"
            )

        district_id = None
        if district_source_id_raw:
            district_source_id = _to_int(
                district_source_id_raw,
                field="bakhsh",
                file_name="shahr.csv",
            )
            district_id = district_source_to_db.get(district_source_id)

        _upsert_by_amar_code(
            db,
            GeoCity,
            amar_code=amar_code,
            values={
                "province_id": province_id,
                "county_id": county_id,
                "district_id": district_id,
                "name": name,
                "city_type": city_type,
                "is_active": True,
            },
        )

    # 6) Villages / abadi.csv
    village_rows = _read_csv(base / "abadi.csv")

    for row in village_rows:
        source_id = _required(row, "id", "abadi.csv")
        province_source_id = _to_int(
            _required(row, "ostan", "abadi.csv"),
            field="ostan",
            file_name="abadi.csv",
        )
        county_source_id = _to_int(
            _required(row, "shahrestan", "abadi.csv"),
            field="shahrestan",
            file_name="abadi.csv",
        )
        district_source_id_raw = _optional(row, "bakhsh")
        rural_source_id_raw = _optional(row, "dehestan")

        name = _required(row, "name", "abadi.csv")
        village_type = _optional(row, "abadi_type")
        diag = _optional(row, "diag")
        amar_code = _required(row, "amar_code", "abadi.csv")

        province_id = province_source_to_db.get(province_source_id)
        county_id = county_source_to_db.get(county_source_id)

        if province_id is None:
            raise ValueError(
                f"Missing province source id {province_source_id} for village {source_id}"
            )
        if county_id is None:
            raise ValueError(
                f"Missing county source id {county_source_id} for village {source_id}"
            )

        district_id = None
        if district_source_id_raw:
            district_source_id = _to_int(
                district_source_id_raw,
                field="bakhsh",
                file_name="abadi.csv",
            )
            district_id = district_source_to_db.get(district_source_id)

        rural_district_id = None
        if rural_source_id_raw:
            rural_source_id = _to_int(
                rural_source_id_raw,
                field="dehestan",
                file_name="abadi.csv",
            )
            rural_district_id = rural_district_source_to_db.get(rural_source_id)

        _upsert_by_amar_code(
            db,
            GeoVillage,
            amar_code=amar_code,
            values={
                "province_id": province_id,
                "county_id": county_id,
                "district_id": district_id,
                "rural_district_id": rural_district_id,
                "name": name,
                "village_type": village_type,
                "diag": diag,
                "is_active": True,
            },
        )

    db.commit()

    return GeoSeedResult(
        provinces=db.query(GeoProvince).count(),
        counties=db.query(GeoCounty).count(),
        districts=db.query(GeoDistrict).count(),
        rural_districts=db.query(GeoRuralDistrict).count(),
        cities=db.query(GeoCity).count(),
        villages=db.query(GeoVillage).count(),
    )

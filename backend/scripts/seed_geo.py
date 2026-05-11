from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.session import SessionLocal
from app.modules.geo.seed import seed_geo


DEFAULT_CSV_DIR = Path("/data/geo/iran-cities/v3/csv")


def main() -> None:
    db = SessionLocal()

    try:
        result = seed_geo(DEFAULT_CSV_DIR, db)
    finally:
        db.close()

    print("Geo seed completed.")
    print(f"provinces: {result.provinces}")
    print(f"counties: {result.counties}")
    print(f"districts: {result.districts}")
    print(f"rural_districts: {result.rural_districts}")
    print(f"cities: {result.cities}")
    print(f"villages: {result.villages}")


if __name__ == "__main__":
    main()

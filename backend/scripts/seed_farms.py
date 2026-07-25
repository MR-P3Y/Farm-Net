from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.session import SessionLocal  # noqa: E402
from app.modules.farms.seed import seed_farm_references  # noqa: E402


def main() -> None:
    db = SessionLocal()
    try:
        result = seed_farm_references(db)
    finally:
        db.close()

    print("Farm reference seed completed.")
    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()

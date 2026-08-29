from pathlib import Path
import sys


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.db.session import SessionLocal  # noqa: E402
from app.modules.finance.seed import seed_finance_policies  # noqa: E402


def main() -> None:
    db = SessionLocal()
    try:
        print(seed_finance_policies(db))
    finally:
        db.close()


if __name__ == "__main__":
    main()

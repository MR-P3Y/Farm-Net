from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.session import SessionLocal
from app.modules.orders.seed import seed_commission_settings


def main() -> None:
    db = SessionLocal()

    try:
        result = seed_commission_settings(db)
        print("Order seed completed")
        print(f"commission_total={result['total']}")
        print(f"commission_active={result['active']}")
        print(f"commission_created={result['created']}")
        print(f"commission_updated={result['updated']}")
        print(f"default_id={result['default_id']}")
        print(f"default_percent={result['default_percent']}")
    finally:
        db.close()


if __name__ == "__main__":
    main()

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.session import SessionLocal
from app.modules.products.seed import seed_product_categories


def main() -> None:
    db = SessionLocal()

    try:
        result = seed_product_categories(db)
        print("Product category seed completed")
        print(f"total={result['total']}")
        print(f"active={result['active']}")
        print(f"created={result['created']}")
        print(f"updated={result['updated']}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
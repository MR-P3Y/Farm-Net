import json
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.session import SessionLocal  # noqa: E402
from app.modules.subscriptions.reconciliation_service import (  # noqa: E402
    BillingReconciliationService,
)


def main() -> None:
    db = SessionLocal()
    try:
        result = BillingReconciliationService(db).run()
        print(json.dumps(result.model_dump(mode="json"), ensure_ascii=False))
        raise SystemExit(0 if result.clean else 1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

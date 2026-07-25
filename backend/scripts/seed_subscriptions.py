from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.session import SessionLocal  # noqa: E402
from app.modules.subscriptions.seed import seed_subscription_catalog  # noqa: E402


def main() -> None:
    db = SessionLocal()
    try:
        result = seed_subscription_catalog(db)
    finally:
        db.close()
    print("Subscription catalog seed completed.")
    print(f"features: {result['features']}")
    print(f"plans: {result['plans']}")
    print(f"plan_features: {result['plan_features']}")


if __name__ == "__main__":
    main()

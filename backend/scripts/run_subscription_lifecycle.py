import argparse
import json

from app.db.session import SessionLocal
from app.modules.subscriptions.renewal_service import SubscriptionRenewalService


def main() -> None:
    parser = argparse.ArgumentParser(description="Process due Farm-Net subscriptions")
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()
    db = SessionLocal()
    try:
        result = SubscriptionRenewalService(db).process_due(limit=args.limit)
        print(json.dumps(result, sort_keys=True))
    finally:
        db.close()


if __name__ == "__main__":
    main()

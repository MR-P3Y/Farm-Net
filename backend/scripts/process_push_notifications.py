import argparse
import json
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def main() -> None:
    from app.db.session import SessionLocal
    from app.modules.notifications.push_dispatcher import PushDeliveryDispatcher

    parser = argparse.ArgumentParser(description="Process one Push notification batch")
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()
    db = SessionLocal()
    try:
        result = PushDeliveryDispatcher(db).run_once(limit=args.limit)
        print(json.dumps(result.__dict__, sort_keys=True))
    finally:
        db.close()


if __name__ == "__main__":
    main()

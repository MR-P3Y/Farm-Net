from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.session import SessionLocal  # noqa: E402
from app.modules.auth.seed import seed_auth  # noqa: E402


def main() -> None:
    db = SessionLocal()

    try:
        result = seed_auth(db)
    finally:
        db.close()

    print("Auth seed completed.")
    print(f"roles: {result['roles']}")
    print(f"permissions: {result['permissions']}")
    print(f"super_admin_id: {result['super_admin_id']}")
    print(f"super_admin_email: {result['super_admin_email']}")


if __name__ == "__main__":
    main()

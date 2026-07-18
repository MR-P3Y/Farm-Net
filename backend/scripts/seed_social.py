from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.session import SessionLocal  # noqa: E402
from app.modules.auth import models as auth_models  # noqa: E402, F401
from app.modules.expert import models as expert_models  # noqa: E402, F401
from app.modules.media import models as media_models  # noqa: E402, F401
from app.modules.social.service import SocialService  # noqa: E402


def main() -> None:
    db = SessionLocal()
    try:
        rows = SocialService(db).seed_default_categories()
        print("Social category seed completed")
        print(f"total={len(rows)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()

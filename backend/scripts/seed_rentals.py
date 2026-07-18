from app.db.session import SessionLocal
from app.modules.rentals.service import RentalService


def main() -> None:
    db = SessionLocal()
    try:
        rows = RentalService(db).seed_categories()
        print("Rental category seed completed")
        print(f"total={len(rows)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()

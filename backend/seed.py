from app.core.database import Base, SessionLocal, engine, ensure_schema
from app.models import Booking, DiagnosticCentre, DiagnosticTest, Payment, User  # noqa: F401
from app.seed import seed_centres


def main() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_schema()
    db = SessionLocal()
    try:
        seed_centres(db)
        print("Seed data loaded.")
    finally:
        db.close()


if __name__ == "__main__":
    main()

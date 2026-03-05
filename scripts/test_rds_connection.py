"""
Small helper script to verify the app can connect to the configured PostgreSQL
database (e.g. your AWS RDS instance) using the existing SQLAlchemy engine.

Run from the project root:

    uv run python scripts/test_rds_connection.py

Make sure your .env (or shell) defines DATABASE_URL / POSTGRES_* first.
"""

from sqlalchemy import text

from app.core.config import settings
from app.core.database import sync_engine


def main() -> None:
    print("Using DATABASE_URL:", settings.DATABASE_URL)
    try:
        with sync_engine.connect() as conn:
            result = conn.execute(text("SELECT 1;"))
            scalar = result.scalar()
        print("DB connection OK, SELECT 1 returned:", scalar)
    except Exception as exc:
        print("DB connection FAILED:")
        print(repr(exc))


if __name__ == "__main__":
    main()


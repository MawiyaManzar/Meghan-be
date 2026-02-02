"""
Database initialization script.
Creates all database tables if they don't exist.
Run this script once to initialize the database schema.
"""
from app.core.database import sync_engine
from app.models import Base


def init_db():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=sync_engine)
    print("✓ Database tables created successfully!")


if __name__ == "__main__":
    init_db()


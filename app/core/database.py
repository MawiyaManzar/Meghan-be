"""
Database session management for FastAPI.
Handles SQLAlchemy (PostgreSQL) connections.
MongoDB and Redis have been removed — app uses Aurora PostgreSQL + S3 + Bedrock.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
import logging
import ssl
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

logger = logging.getLogger(__name__)

def _is_supabase_host(database_url: str) -> bool:
    """Return True if DATABASE_URL hostname looks like Supabase Postgres / pooler."""
    try:
        host = urlparse(database_url).hostname or ""
    except Exception:
        return False
    return host.endswith(".supabase.co") or host.endswith(".pooler.supabase.com")


def _ensure_supabase_sslmode(database_url: str) -> str:
    """
    Supabase Postgres requires SSL. For sync psycopg2 connections, the simplest reliable
    approach is to ensure `sslmode=require` exists in the URL query string.
    """
    if not _is_supabase_host(database_url):
        return database_url

    parsed = urlparse(database_url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    if query.get("sslmode"):
        return database_url

    query["sslmode"] = "require"
    return urlunparse(parsed._replace(query=urlencode(query)))


def _to_asyncpg_url(database_url: str) -> str:
    """Convert a Postgres SQLAlchemy URL into an asyncpg URL."""
    if database_url.startswith("postgres://"):
        database_url = "postgresql://" + database_url[len("postgres://") :]
    if database_url.startswith("postgresql+asyncpg://"):
        return database_url
    if database_url.startswith("postgresql+psycopg2://"):
        return "postgresql+asyncpg://" + database_url[len("postgresql+psycopg2://") :]
    if database_url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + database_url[len("postgresql://") :]
    return database_url


# PostgreSQL - SQLAlchemy setup
# Sync engine for migrations and sync operations
_sync_db_url = _ensure_supabase_sslmode(settings.DATABASE_URL)
sync_engine = create_engine(
    _sync_db_url,
    connect_args={"check_same_thread": False} if "sqlite" in _sync_db_url else {},
)

# Async engine for FastAPI operations
_async_db_url = _to_asyncpg_url(_sync_db_url)
async_engine = create_async_engine(
    _async_db_url,
    echo=settings.DEBUG,
    # asyncpg expects an SSLContext (not "require").
    connect_args={"ssl": ssl.create_default_context()} if _is_supabase_host(_sync_db_url) else {},
)

# Session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


def get_db() -> Session:
    """
    Dependency function to get sync database session.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncSession:
    """
    Dependency function to get async database session.
    Yields an async database session and ensures it's closed after use.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

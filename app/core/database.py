"""
Database session management for FastAPI.
Handles SQLAlchemy (PostgreSQL), MongoDB, and Redis connections.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# PostgreSQL - SQLAlchemy setup
# Sync engine for migrations and sync operations
sync_engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Async engine for FastAPI operations
async_engine = create_async_engine(
    settings.postgres_url if not "sqlite" in settings.DATABASE_URL else settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://"),
    echo=settings.DEBUG
)

# Session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# MongoDB client
mongodb_client: AsyncIOMotorClient = None
mongodb_db = None

# Redis client
redis_client: redis.Redis = None


async def init_mongodb():
    """Initialize MongoDB connection. Optional - app will continue if MongoDB is unavailable."""
    global mongodb_client, mongodb_db
    try:
        mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
        mongodb_db = mongodb_client[settings.MONGODB_DB]
        # Test connection
        await mongodb_client.admin.command('ping')
        logger.info("MongoDB connected successfully")
    except Exception as e:
        logger.warning(f"MongoDB connection failed (optional): {e}")
        logger.warning("App will continue without MongoDB. Chat logs and wellbeing data features will be unavailable.")
        mongodb_client = None
        mongodb_db = None


async def init_redis():
    """Initialize Redis connection. Optional - app will continue if Redis is unavailable."""
    global redis_client
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        # Test connection
        await redis_client.ping()
        logger.info("Redis connected successfully")
    except Exception as e:
        logger.warning(f"Redis connection failed (optional): {e}")
        logger.warning("App will continue without Redis. Caching features will be unavailable.")
        redis_client = None


async def close_mongodb():
    """Close MongoDB connection."""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        logger.info("MongoDB connection closed")


async def close_redis():
    """Close Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")


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


def get_mongodb():
    """
    Dependency function to get MongoDB database.
    Returns None if MongoDB is not available.
    """
    if mongodb_db is None:
        logger.warning("MongoDB is not available. Some features may be unavailable.")
    return mongodb_db


def get_redis():
    """
    Dependency function to get Redis client.
    Returns None if Redis is not available.
    """
    if redis_client is None:
        logger.warning("Redis is not available. Caching features may be unavailable.")
    return redis_client


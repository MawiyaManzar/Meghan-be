"""
Main FastAPI application entry point.
"""
import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.routers import auth, llm, chat, users
from app.routers import hearts
from app.routers import onboarding, checkins
from app.routers import therapist
from app.routers import communities  
from app.routers import expressions  
from app.routers import journal
from app.routers import insights
from app.routers import crisis
from app.routers import community_ws
from app.routers import voice

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    logger.info("Starting up Meghan API...")
    logger.info("Application startup complete")
    
    yield
    
    logger.info("Shutting down Meghan API...")
    logger.info("Shutdown complete")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Meghan API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/debug/schema-check")
async def schema_check(db: Session = Depends(get_db)):
    """Debug endpoint to verify key DB tables/columns for A4 schema alignment."""
    required_tables = [
        "users",
        "conversations",
        "chat_messages",
        "hearts_transactions",
        "crisis_events",
        "weekly_wellbeing_insights",
    ]
    required_columns = {
        "chat_messages": ["s3_key"],
        "weekly_wellbeing_insights": ["user_id", "week_start", "week_end", "summary_text"],
    }

    inspector = inspect(db.bind)
    existing_tables = set(inspector.get_table_names())
    missing_tables = [table for table in required_tables if table not in existing_tables]
    missing_columns = {}
    for table_name, columns in required_columns.items():
        if table_name not in existing_tables:
            missing_columns[table_name] = columns
            continue
        existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
        missing = [column for column in columns if column not in existing_columns]
        if missing:
            missing_columns[table_name] = missing

    return {
        "ok": not missing_tables and not missing_columns,
        "required_tables": required_tables,
        "missing_tables": missing_tables,
        "missing_columns": missing_columns,
    }


# Include routers
app.include_router(auth.router)
app.include_router(llm.router)
app.include_router(chat.router)
app.include_router(users.router)
app.include_router(hearts.router)
app.include_router(onboarding.router)  
app.include_router(checkins.router)
app.include_router(therapist.router)
app.include_router(communities.router)
app.include_router(expressions.router)  
app.include_router(journal.router)
app.include_router(insights.router)
app.include_router(crisis.router)
app.include_router(community_ws.router)
app.include_router(voice.router)

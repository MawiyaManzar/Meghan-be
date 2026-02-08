"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import init_mongodb, init_redis, close_mongodb, close_redis
from app.routers import auth, llm, chat, users
from app.routers import hearts
from app.routers import onboarding, checkins
from app.routers import therapist
from app.routers import communities  
import logging
from app.routers import expressions  
from app.routers import journal
from app.routers import insights
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events for database connections.
    """
    # Startup
    logger.info("Starting up Meghan API...")
    # Initialize optional services (MongoDB and Redis)
    # These are optional - app will continue if they fail
    await init_mongodb()
    await init_redis()
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Meghan API...")
    await close_mongodb()
    await close_redis()
    logger.info("All database connections closed")


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
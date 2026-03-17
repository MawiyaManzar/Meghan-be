"""
Configuration settings for the FastAPI application.
Handles environment variables and application settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Optional, Union
import json
from pathlib import Path

# Get the project root directory (parent of app/)
BASE_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application settings
    APP_NAME: str = "Meghan API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True  # Set to False in production
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"

     # === AssemblyAI STT ===
    ASSEMBLYAI_API_KEY: str | None = None
    ASSEMBLYAI_UPLOAD_URL: str = "https://api.assemblyai.com/v2/upload"
    ASSEMBLYAI_TRANSCRIPT_URL: str = "https://api.assemblyai.com/v2/transcript"
    
    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"  # Change in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 60  # 30 days
    
    # CORS - Can be JSON array string or comma-separated string
    CORS_ORIGINS: Union[str, list[str]] = "http://localhost:5173,http://localhost:3000"
    
    # Database - PostgreSQL (primary)
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'meghan.db'}"  # Default fallback
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "meghan"
    POSTGRES_USER: str = "meghan_user"
    POSTGRES_PASSWORD: str = "meghan_password"
    
    # MongoDB (for chat sessions and wellbeing data)
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "meghan_chat"
    
    # Redis (for caching and sessions)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # LLM / Gemini API
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"  # Default model, can be overridden (e.g., "gemini-1.5-pro", "gemini-2.0-flash-exp")
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_TOP_P: float = 0.95
    GEMINI_MAX_OUTPUT_TOKENS: int = 500
    GEMINI_THINKING_BUDGET: int = 200  # Note: May need special handling depending on model support
    
    # === AWS (only if you use AWS services like S3) ===
    # If you are not using AWS at all, you can ignore these.
    AWS_REGION: str = "us-east-1"
    AWS_PROFILE: Optional[str] = None  # Optional: AWS CLI profile name (defaults to "default")
    
    # === AWS S3 media storage ===
    # Keep bucket private; backend returns temporary pre-signed URLs for reads.
    S3_MEDIA_BUCKET: str = "meghan-media"
    S3_MEDIA_PREFIX: str = "media"
    S3_PRESIGNED_URL_TTL_SECONDS: int = 900
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            # Try JSON first
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                pass
            # Fall back to comma-separated
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),  # Use absolute path for .env file too
        case_sensitive=True,
        # Ignore unknown env vars so legacy/unused keys in local .env do not
        # crash application startup (helpful for tests and incremental migration).
        extra="ignore",
    )
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def make_db_path_absolute(cls, v):
        """Convert relative database paths to absolute paths."""
        if isinstance(v, str):
            if v.startswith("sqlite:///./"):
                # Convert relative path to absolute
                db_name = v.replace("sqlite:///./", "")
                abs_path = BASE_DIR / db_name
                # Use 3 slashes: sqlite:///path
                return f"sqlite:///{abs_path.as_posix()}"
            elif v.startswith("sqlite:///"):
                # Already absolute or explicit path, return as-is
                return v
        return v
    
    @field_validator("S3_MEDIA_PREFIX", mode="before")
    @classmethod
    def normalize_s3_prefix(cls, v):
        """Normalize S3 key prefix by trimming leading/trailing slashes."""
        if isinstance(v, str):
            return v.strip("/")
        return v
    
    @field_validator("S3_PRESIGNED_URL_TTL_SECONDS")
    @classmethod
    def validate_presigned_ttl(cls, v):
        """Ensure pre-signed URL TTL is positive and reasonably bounded."""
        if v <= 0:
            raise ValueError("S3_PRESIGNED_URL_TTL_SECONDS must be > 0")
        if v > 86400:
            raise ValueError("S3_PRESIGNED_URL_TTL_SECONDS must be <= 86400")
        return v
    
    @property
    def postgres_url(self) -> str:
        """Build PostgreSQL connection URL from components."""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


# Global settings instance
settings = Settings()


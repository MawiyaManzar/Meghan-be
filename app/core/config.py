"""
Configuration settings for the FastAPI application.
Handles environment variables and application settings.
"""
from pydantic_settings import BaseSettings
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
    DEBUG: bool = False
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"  # Change in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 60  # 30 days
    
    # CORS - Can be JSON array string or comma-separated string
    CORS_ORIGINS: Union[str, list[str]] = "http://localhost:5173,http://localhost:3000"
    
    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'meghan.db'}"
    
    # LLM / Gemini API
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"  # Default model, can be overridden (e.g., "gemini-1.5-pro", "gemini-2.0-flash-exp")
    GEMINI_TEMPERATURE: float = 0.7
    GEMINI_TOP_P: float = 0.95
    GEMINI_MAX_OUTPUT_TOKENS: int = 500
    GEMINI_THINKING_BUDGET: int = 200  # Note: May need special handling depending on model support
    
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
    
    class Config:
        env_file = str(BASE_DIR / ".env")  # Use absolute path for .env file too
        case_sensitive = True
    
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


# Global settings instance
settings = Settings()


"""
Common dependencies for FastAPI routes.
Exports reusable dependencies like get_current_user.
"""
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.routers.auth import get_current_user
from app.models.user import User

# Re-export get_current_user for convenience
__all__ = ["get_current_user", "CurrentUser", "DatabaseSession"]

# Type aliases for dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
DatabaseSession = Annotated[Session, Depends(get_db)]


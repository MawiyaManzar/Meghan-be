"""
Common dependencies for FastAPI routes.
Exports reusable dependencies like get_current_user.
"""
from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.routers.auth import get_current_user
from app.models.user import User

# Re-export get_current_user for convenience
__all__ = ["get_current_user", "CurrentUser", "DatabaseSession", "TherapistUser"]

# Type aliases for dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
DatabaseSession = Annotated[Session, Depends(get_db)]


def get_current_therapist_user(current_user: CurrentUser) -> User:
    """
    Restrict access to therapist/admin users.
    """
    role = getattr(current_user, "role", "user")
    if role not in ("therapist", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Therapist access required",
        )
    return current_user


TherapistUser = Annotated[User, Depends(get_current_therapist_user)]


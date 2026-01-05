"""
User state and profile management router.
Handles user state updates, XP management, and profile operations.
"""
import logging
import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import CurrentUser, DatabaseSession
from app.models.user import User, UserState, UserProfile
from app.schemas.userState import (
    UserStateResponse,
    UserStateUpdate,
    XPAddRequest,
    XPAddResponse
)
from app.schemas.user import UserProfileResponse, UserProfileUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/users", tags=["users"])

# XP bonus per bio field completion
XP_PER_BIO_FIELD = 20


def calculate_level(xp: int) -> int:
    """
    Calculate user level from XP.
    Formula: floor(xp / 200) + 1
    
    Args:
        xp: Experience points
    
    Returns:
        User level
    """
    return math.floor(xp / 200) + 1


def get_or_create_user_state(db: Session, user_id: int) -> UserState:
    """
    Get existing user state or create a default one.
    
    Args:
        db: Database session
        user_id: User ID
    
    Returns:
        UserState object
    """
    user_state = db.query(UserState).filter(UserState.user_id == user_id).first()
    if not user_state:
        # Create default user state
        user_state = UserState(
            user_id=user_id,
            mood="Grounded",
            risk_tier="Green",
            xp=0,
            level=1,
            steps=0,
            sleep_hours=0,
            pomo_sessions=0
        )
        db.add(user_state)
        db.commit()
        db.refresh(user_state)
    return user_state


def get_or_create_user_profile(db: Session, user_id: int) -> UserProfile:
    """
    Get existing user profile or create an empty one.
    
    Args:
        db: Database session
        user_id: User ID
    
    Returns:
        UserProfile object
    """
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.get("/me/state", response_model=UserStateResponse)
async def get_user_state(
    current_user: CurrentUser,
    db: DatabaseSession
):
    """
    Get current user's state.
    
    Args:
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        User state information
    """
    user_state = get_or_create_user_state(db, current_user.id)
    return user_state


@router.put("/me/state", response_model=UserStateResponse)
async def update_user_state(
    state_update: UserStateUpdate,
    current_user: CurrentUser,
    db: DatabaseSession
):
    """
    Update user's state (mood, tier, metrics, etc.).
    
    Args:
        state_update: State update data
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Updated user state
    
    Raises:
        HTTPException: If validation fails
    """
    user_state = get_or_create_user_state(db, current_user.id)
    
    # Validate tier and mood if provided
    valid_tiers = {"Green", "Yellow", "Red"}
    valid_moods = {"Heavy", "Pulse", "Grounded"}
    valid_sources = {"Family", "Relationship", "Career/Academics", "Others"}
    
    if state_update.risk_tier is not None and state_update.risk_tier not in valid_tiers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tier: {state_update.risk_tier}. Must be one of {valid_tiers}"
        )
    
    if state_update.mood is not None and state_update.mood not in valid_moods:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid mood: {state_update.mood}. Must be one of {valid_moods}"
        )
    
    # Validate stress_source if provided
    if state_update.stress_source is not None and state_update.stress_source not in valid_sources:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid stress_source: {state_update.stress_source}. Must be one of {valid_sources}"
        )
    
    # Validate other_text requirement when stress_source is being set to "Others"
    if state_update.stress_source == "Others":
        # If stress_source is being set to "Others", other_text must be provided
        if state_update.other_text is None or state_update.other_text.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="other_text is required when stress_source is 'Others'"
            )
    
    # Update fields
    update_data = state_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user_state, field, value)
    
    db.commit()
    db.refresh(user_state)
    
    logger.info(f"Updated user state for user {current_user.id}")
    return user_state


@router.post("/me/state/xp", response_model=XPAddResponse)
async def add_xp(
    xp_request: XPAddRequest,
    current_user: CurrentUser,
    db: DatabaseSession
):
    """
    Add XP to user state and recalculate level.
    
    Args:
        xp_request: XP addition request (amount)
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Updated XP and level
    """
    user_state = get_or_create_user_state(db, current_user.id)
    
    user_state.xp += xp_request.amount
    user_state.level = calculate_level(user_state.xp)
    
    db.commit()
    db.refresh(user_state)
    
    logger.info(f"Added {xp_request.amount} XP to user {current_user.id}, new level: {user_state.level}")
    
    return XPAddResponse(xp=user_state.xp, level=user_state.level)


@router.get("/me/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: CurrentUser,
    db: DatabaseSession
):
    """
    Get current user's profile.
    
    Args:
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        User profile information
    """
    profile = get_or_create_user_profile(db, current_user.id)
    return profile


@router.put("/me/profile", response_model=UserProfileResponse)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: CurrentUser,
    db: DatabaseSession
):
    """
    Update user's profile/bio information.
    
    Awards 20 XP for each bio field that is newly filled in (was None/empty, now has value).
    
    Args:
        profile_update: Profile update data
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Updated user profile
    """
    profile = get_or_create_user_profile(db, current_user.id)
    
    # Track which fields are being newly filled in for XP bonus
    bio_fields = ["name", "major", "hobbies", "values", "bio"]
    xp_to_award = 0
    
    update_data = profile_update.model_dump(exclude_unset=True)
    
    # Check each field for XP bonus
    for field in bio_fields:
        if field in update_data:
            new_value = update_data[field]
            current_value = getattr(profile, field)
            
            # Award XP if field was empty/None and now has a value
            if (current_value is None or current_value == "") and new_value and new_value.strip():
                xp_to_award += XP_PER_BIO_FIELD
                logger.info(f"User {current_user.id} filled in {field}, awarding {XP_PER_BIO_FIELD} XP")
    
    # Update profile fields
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    
    # Award XP if any fields were newly filled
    if xp_to_award > 0:
        user_state = get_or_create_user_state(db, current_user.id)
        user_state.xp += xp_to_award
        user_state.level = calculate_level(user_state.xp)
        db.commit()
        logger.info(f"Awarded {xp_to_award} XP to user {current_user.id} for bio field completions")
    
    logger.info(f"Updated profile for user {current_user.id}")
    return profile


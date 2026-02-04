"""
Onboarding endpoints:
- PUT /api/onboarding/profile  -> save age_range, life_stage, struggles
- PUT /api/onboarding/privacy  -> save privacy_level
"""

import json
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import CurrentUser, DatabaseSession
from app.models.user import UserProfile
from app.routers.users import get_or_create_user_profile  # reuse helper
from app.schemas.user import UserProfileResponse
from app.services.communities import auto_assign_communities_for_user

router = APIRouter(prefix='/api/onboarding',tags=['onboarding'])

@router.put("/profile",response_model=UserProfileResponse)
async def update_onboarding_profile(
    payload: dict,
    current_user:CurrentUser,
    db:DatabaseSession,
):
    """
    Save onboarding fields: age_range, life_stage, struggles.
    - struggles: expect a list of strings from frontend; store as JSON string.
    """
    # current_user is a User model (from auth dependency) and uses `id`
    profile = get_or_create_user_profile(db, current_user.id)

    age_range = payload.get("age_range")
    life_stage = payload.get("life_stage")
    struggles= payload.get("struggles")

    if struggles is not None:
        if not isinstance(struggles,list):
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail="Struggles must be a list of strings")
        profile.struggles = json.dumps(struggles)
    if age_range is not None:
        profile.age_range = age_range

    if life_stage is not None:
        profile.life_stage = life_stage
    
    db.commit()
    db.refresh(profile)

    # Auto-assign communities based on updated struggles
    auto_assign_communities_for_user(db, current_user.id, profile)
    return profile

@router.put("/privacy",response_model=UserProfileResponse)
async def update_onboarding_privacy(
    payload:dict,
    current_user:CurrentUser,
    db:DatabaseSession,
):
    """
    Save initial privacy preference (privacy_level).
    - privacy_level: "full" | "partial" | "identified"
    """
    profile = get_or_create_user_profile(db,current_user.id)
    privacy_level = payload.get("privacy_level")

    if privacy_level is None:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail="Privacy level is required")
    
    valid_levels = ["full", "partial", "identified"]
    if privacy_level not in valid_levels:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid privacy level. Must be one of: {valid_levels}")
    
    profile.privacy_level = privacy_level
    db.commit()
    db.refresh(profile)
    return profile


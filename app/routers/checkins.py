"""
Check-in endpoints:
- POST /api/checkins/first  -> first emotional check-in
"""
from fastapi import APIRouter, HTTPException, status
from app.core.dependencies import CurrentUser, DatabaseSession
from app.models.user import UserState
from app.routers.users import get_or_create_user_state  # reuse helper

router = APIRouter(prefix="/api/checkins", tags=["checkins"])

@router.post("/first",status_code=status.HTTP_201_CREATED)
async def first_checkin(payload:dict,
current_user:CurrentUser,
db:DatabaseSession
):
    """
    Store first emotional check-in.
    Expect:
    - mood: 'Heavy' | 'Pulse' | 'Grounded'
    - risk_tier: 'Green' | 'Yellow' | 'Red'
    - stress_source: optional
    """
    mood = payload.get("mood")
    risk_tier = payload.get("risk_tier")
    stress_source = payload.get("stress_source")

    if not mood or not risk_tier:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST
        ,detail="Mood and risk tier are required")
    
    valid_moods = {"Heavy", "Pulse", "Grounded"}
    valid_tiers = {"Green", "Yellow", "Red"}

    if mood not in valid_moods:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid mood: {mood}",
        )
    if risk_tier not in valid_tiers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid risk_tier: {risk_tier}",
        )

    user_state = get_or_create_user_state(db,current_user.id)
    user_state.mood = mood
    user_state.risk_tier = risk_tier
    if stress_source is not None:
        user_state.stress_source = stress_source

    db.commit()
    db.refresh(user_state)
    return {"success":True}
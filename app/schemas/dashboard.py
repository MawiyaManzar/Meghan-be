"""
Dashboard Schemas for Project Meghan

Handles aggregated dashboard data for user frontend.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict
from .userState import UserStateResponse
from .user import UserProfileResponse

class DashboardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    state: UserStateResponse
    profile: UserProfileResponse
    hearts_balance: int = 0  # Hearts balance (temporarily from XP)
    xp_to_next_level: int = 0  # Calculated: 200 - (xp % 200)
    progress_percentages: Optional[Dict[str, float]] = None  # { steps: float, sleep: float, pomo: float } (if goals are defined)
    weekly_summary: Optional[Dict] = None  # Stub for now, can be empty
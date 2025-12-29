"""
Dashboard Schemas for Project Meghan

Handles aggregated dashboard data for user frontend.
"""

from pydantic import BaseModel
from typing import Optional, Dict
from .userState import UserStateResponse
from .user import UserProfileResponse

class DashboardResponse(BaseModel):
    state: UserStateResponse
    profile: UserProfileResponse
    xp_to_next_level: int = 0  # Calculated: 200 - (xp % 200)
    progress_percentages: Optional[Dict[str, float]] = None  # { steps: float, sleep: float, pomo: float } (if goals are defined)

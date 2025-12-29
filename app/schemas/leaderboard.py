"""
Leaderboard Schemas for Project Meghan

Handles leaderboard data with user rankings.
"""

from pydantic import BaseModel
from typing import List, Optional

class LeaderboardEntry(BaseModel):
    rank: int
    name: str  # Spirit name or anonymous name (e.g., "QuietSage", "SteadyPulse")
    level: int
    xp: int
    is_user: bool = False  # True if this entry is the current user

class LeaderboardResponse(BaseModel):
    entries: List[LeaderboardEntry]
    user_rank: Optional[int] = None  # Current user's rank (if in top N, otherwise null)

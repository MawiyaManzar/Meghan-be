from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List

class CommunityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str           # positive, user-facing
    description: str
    stress_source: str  # still ok to show
    is_active: bool
    created_at: datetime

class CommunityListResponse(BaseModel):
    communities: List[CommunityResponse]
    user_communities: List[int]  # IDs user belongs to

class CommunityJoinRequest(BaseModel):
    is_anonymous: bool = True
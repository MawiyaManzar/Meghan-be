from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional


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


class CommunityMessageBase(BaseModel):
    content: str
    is_anonymous: bool = True


class CommunityMessageCreate(CommunityMessageBase):
    pass


class CommunityMessageResponse(CommunityMessageBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    community_id: int
    user_id: int
    created_at: datetime
    # Optional display fields for frontend convenience
    display_name: Optional[str] = None


class CommunityMessageListResponse(BaseModel):
    messages: List[CommunityMessageResponse]
    total: int
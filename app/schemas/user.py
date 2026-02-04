from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class UserProfileBase(BaseModel):
    name: Optional[str] = None
    major: Optional[str] = None
    hobbies: Optional[str] = None
    values: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    age_range: Optional[str] = None
    life_stage: Optional[str] = None
    struggles: Optional[str] = None      # JSON string; keep simple for now
    privacy_level: Optional[str] = None  # "full" | "partial" | "identified"

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    major: Optional[str] = None
    hobbies: Optional[str] = None
    values: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    age_range: Optional[str] = None
    life_stage: Optional[str] = None
    struggles: Optional[str] = None
    privacy_level: Optional[str] = None

class UserProfileResponse(UserProfileBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
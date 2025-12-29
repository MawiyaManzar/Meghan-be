from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserProfileBase(BaseModel):
    name: Optional[str] = None
    major: Optional[str] = None
    hobbies: Optional[str] = None
    values: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    major: Optional[str] = None
    hobbies: Optional[str] = None
    values: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None

class UserProfileResponse(UserProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
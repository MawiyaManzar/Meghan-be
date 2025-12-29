from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserStateBase(BaseModel):
    mood: str = Field(description="Values: 'Heavy', 'Pulse', 'Grounded'")
    stress_source: Optional[str] = Field(None, description="Values: 'Family', 'Relationship', 'Career/Academics', 'Others'")
    other_text: Optional[str] = Field(None, description="Required when stress_source is 'Others'")
    risk_tier: str = Field(description="Values: 'Green', 'Yellow', 'Red'")
    steps: int = Field(default=0, description="Daily step count")
    sleep_hours: int = Field(default=0, description="Hours of sleep")
    pomo_sessions: int = Field(default=0, description="Pomodoro sessions completed")

class UserStateCreate(UserStateBase):
    pass

class UserStateUpdate(BaseModel):
    mood: Optional[str] = Field(None, description="Values: 'Heavy', 'Pulse', 'Grounded'")
    stress_source: Optional[str] = Field(None, description="Values: 'Family', 'Relationship', 'Career/Academics', 'Others'")
    other_text: Optional[str] = Field(None, description="Required when stress_source is 'Others'")
    risk_tier: Optional[str] = Field(None, description="Values: 'Green', 'Yellow', 'Red'")
    steps: Optional[int] = Field(None, description="Daily step count")
    sleep_hours: Optional[int] = Field(None, description="Hours of sleep")
    pomo_sessions: Optional[int] = Field(None, description="Pomodoro sessions completed")

class UserStateResponse(BaseModel):
    id: int
    user_id: int
    mood: str
    stress_source: Optional[str] = None
    other_text: Optional[str] = None
    risk_tier: str
    xp: int
    level: int
    steps: int
    sleep_hours: int
    pomo_sessions: int
    last_updated: datetime

    class Config:
        from_attributes = True

class XPAddRequest(BaseModel):
    amount: int = Field(description="XP amount to add", gt=0)

class XPAddResponse(BaseModel):
    xp: int = Field(description="New XP total after addition")
    level: int = Field(description="New level after XP addition")
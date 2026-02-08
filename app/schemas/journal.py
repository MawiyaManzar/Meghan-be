"""
Journal Schemas for Project Meghan

Handles journal entries for sentiment tracking.
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List

class JournalEntryCreate(BaseModel):
    content: str = Field(description="Journal entry text")
    mood_at_time: Optional[str] = Field(None, description="Mood when entry was created (optional)")
    tier_at_time: Optional[str] = Field(None, description="Risk tier when entry was created (optional)")

class JournalEntryUpdate(BaseModel):
    content: Optional[str] = Field(None, description="Journal entry text for editing")

class JournalEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    content: str
    mood_at_time: Optional[str] = None
    tier_at_time: Optional[str] = None
    xp_gained: int = 30  # XP awarded (default: 30)
    created_at: datetime

class JournalEntryListResponse(BaseModel):
    entries: List[JournalEntryResponse]
    total: int  # Total number of entries

class JournalPromptResponse(BaseModel):
    id: str  # e.g., "gratitude", "reflection", "stress_relief"
    title:str
    description:str
    prompt_text:str

class JournalPromptListResponse(BaseModel):
    prompts: List[JournalPromptResponse]
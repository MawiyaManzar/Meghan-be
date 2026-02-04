from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional


class CrisisEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    source: str               # "chat", "community", "journal"
    community_id: Optional[int] = None
    message_excerpt: str
    risk_level: str           # "high", later maybe "medium"/"low"
    matched_phrases: List[str]
    created_at: datetime


class CrisisEventListResponse(BaseModel):
    events: List[CrisisEventResponse]


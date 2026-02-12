"""
Crisis detection and emergency resources schemas.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class CrisisDetectionRequest(BaseModel):
    text: str = Field(..., description="Text to assess for crisis indicators")


class CrisisDetectionResponse(BaseModel):
    risk_level: str  # "low" | "medium" | "high"
    allowed: bool
    matched_phrases: List[str]
    recommended_action: str
    safe_reply: Optional[str] = None


class EmergencyResource(BaseModel):
    name: str
    phone: Optional[str] = None
    website: Optional[str] = None
    available_24_7: bool = True


class EmergencyResourcesResponse(BaseModel):
    resources: List[EmergencyResource]
    country: str
"""
Chat Schemas for Project Meghan

Handles conversation and chat message request/response schemas.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ConversationBase(BaseModel):
    tier: str = Field(description="Risk tier at conversation start: 'Green', 'Yellow', 'Red'")
    mood: str = Field(description="Mood at conversation start: 'Heavy', 'Pulse', 'Grounded'")
    source: str = Field(description="Stress source at conversation start: 'Family', 'Relationship', 'Career/Academics', 'Others'")

class ConversationCreate(BaseModel):
    tier: Optional[str] = Field(None, description="Risk tier at conversation start: 'Green', 'Yellow', 'Red'. If not provided, uses current user state.")
    mood: Optional[str] = Field(None, description="Mood at conversation start: 'Heavy', 'Pulse', 'Grounded'. If not provided, uses current user state.")
    source: Optional[str] = Field(None, description="Stress source at conversation start. If not provided, uses current user state.")

class ConversationResponse(ConversationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ChatMessageBase(BaseModel):
    role: str = Field(description="Values: 'user', 'model'")
    content: str = Field(description="Message text")

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationListResponse(BaseModel):
    conversations: List[ConversationResponse]

class ChatHistoryResponse(BaseModel):
    conversation: ConversationResponse
    messages: List[ChatMessageResponse]


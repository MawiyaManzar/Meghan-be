"""
Internal chat provider contract types.

These models define the input/output shape expected by the AI provider used by
`ChatService`. They are intentionally lightweight so they can be shared by
service code and tests without importing router or ORM modules.
"""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class ChatMode(str, Enum):
    TALK = "talk"
    PLAN = "plan"
    CALM = "calm"
    REFLECT = "reflect"


class ChatPrompt(BaseModel):
    system_prompt: Optional[str] = Field(
        default=None, description="Resolved system instruction sent to the model."
    )
    user_message: str = Field(description="Current user message text.")
    mode: ChatMode = Field(default=ChatMode.TALK)
    temperature: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)


class ChatResult(BaseModel):
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    model_id: Optional[str] = None
    raw_response: Optional[dict[str, Any]] = None


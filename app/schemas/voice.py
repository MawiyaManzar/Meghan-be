"""
Voice-related schemas for WhatsApp-style voice notes.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.chat import ChatMessageResponse


class VoiceMessageResponse(BaseModel):
    """
    Response schema for a voice message exchange:
    - user_message: the saved user ChatMessage (transcript of audio)
    - ai_response: the saved AI ChatMessage reply
    - audio_url: optional URL if/when TTS audio is generated
    """

    model_config = ConfigDict(from_attributes=True)

    user_message: ChatMessageResponse
    ai_response: ChatMessageResponse
    audio_url: Optional[str] = None


"""
Voice router for WhatsApp-style voice notes.
Flow:
- Mobile uploads short audio clip for an existing conversation.
- Backend:
  - Transcribes via AssemblyAI (non-streaming).
  - Saves user ChatMessage with transcript.
  - Generates AI response via existing chat_service.
  - Returns both messages in a single response.
"""
import logging
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.core.config import settings
from app.core.dependencies import CurrentUser, DatabaseSession
from app.models.user import Conversation, ChatMessage
from app.schemas.chat import ChatMessageResponse
from app.schemas.voice import VoiceMessageResponse
from app.services.chat import chat_service
from app.services.s3_storage import S3StorageService, S3StorageError
from app.services.stt import (
    transcribe_audio_assemblyai,
    STTServiceError,
    STTTimeoutError,
)


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["voice"])


MAX_AUDIO_BYTES = 10 * 1024 * 1024  # 10 MB safety limit for uploads
s3_storage_service = S3StorageService(
    bucket=settings.S3_MEDIA_BUCKET,
    region_name=settings.AWS_REGION,
    prefix=settings.S3_MEDIA_PREFIX,
)


@router.post(
    "/conversations/{conversation_id}/voice",
    response_model=VoiceMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def voice_message(
    conversation_id: int,
    audio: UploadFile = File(...),
    include_audio: bool = False,  # reserved for future TTS support
    current_user: CurrentUser = None,
    db: DatabaseSession = None,
):
    """
    Handle a single voice message for an existing conversation.

    - Accepts an audio file upload (WebM/MP3/etc.).
    - Transcribes audio to text via AssemblyAI.
    - Saves the transcript as a user ChatMessage.
    - Generates and saves an AI response using existing chat_service.
    - Returns both messages.
    """
    # 1) Validate conversation exists and belongs to user
    conversation: Optional[Conversation] = (
        db.query(Conversation).filter(Conversation.id == conversation_id).first()
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation",
        )

    # 2) Read audio file and enforce simple size limit
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded audio file is empty",
        )

    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Audio file is too large (max 10 MB)",
        )

    logger.info(
        f"Received voice message upload for conversation {conversation_id} "
        f"from user {current_user.id} (filename={audio.filename}, size={len(audio_bytes)} bytes)"
    )

    # 3) Persist raw voice clip in private S3 (best-effort: continue if upload fails)
    uploaded_s3_key: Optional[str] = None
    try:
        upload_result = s3_storage_service.upload_media_bytes(
            data_bytes=audio_bytes,
            content_type=audio.content_type or "application/octet-stream",
            owner_user_id=current_user.id,
            entity_type="chat_voice",
            entity_id=conversation_id,
        )
        uploaded_s3_key = upload_result.s3_key
    except S3StorageError as e:
        logger.warning(
            f"S3 upload failed for voice clip in conversation {conversation_id}: {e}"
        )

    # 4) Transcribe with AssemblyAI
    try:
        transcript = await transcribe_audio_assemblyai(
            audio_bytes=audio_bytes,
            filename=audio.filename or "audio",
        )
    except STTTimeoutError as e:
        logger.warning(f"AssemblyAI transcription timeout: {e}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Transcription service timed out. Please try again with a shorter message.",
        )
    except STTServiceError as e:
        logger.error(f"AssemblyAI transcription failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Transcription service failed. Please try again later.",
        )

    if not transcript.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not transcribe audio (empty transcript). Please try again.",
        )

    # 5) Save user message (as text, originating from voice) + media key if uploaded
    user_message = ChatMessage(
        conversation_id=conversation_id,
        role="user",
        content=transcript,
        s3_key=uploaded_s3_key,
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    logger.info(
        f"Saved voice-originated user message {user_message.id} "
        f"for conversation {conversation_id}"
    )

    # 6) Build minimal chat history for context (all previous messages)
    existing_messages = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.conversation_id == conversation_id,
            ChatMessage.id < user_message.id,
        )
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    chat_history = [
        {"role": msg.role, "content": msg.content} for msg in existing_messages
    ]

    # 6) Generate AI response using existing chat_service
    # Note: For now we *skip* safety/hearts; that will be wired in V4.
    try:
        llm_response = await chat_service.generate_response(
            user_message=transcript,
            chat_history=chat_history,
            tier=conversation.tier,
            mood=conversation.mood,
            source=conversation.source,
            bio=None,  # can be added later if needed
            other_text=None,
            mode=conversation.mode or "talk",
        )

        if not llm_response.get("success"):
            logger.error(
                f"LLM response generation failed (voice): "
                f"{llm_response.get('error')}"
            )
            response_content = llm_response.get(
                "content",
                "I'm sorry, I'm having trouble responding right now.",
            )
        else:
            response_content = llm_response["content"]

        ai_message = ChatMessage(
            conversation_id=conversation_id,
            role="model",
            content=response_content,
        )
        db.add(ai_message)
        db.commit()
        db.refresh(ai_message)

        logger.info(
            f"Generated AI response {ai_message.id} for voice message "
            f"in conversation {conversation_id}"
        )

    except Exception as e:
        logger.error(
            f"Error generating AI response for voice message: {str(e)}",
            exc_info=True,
        )
        fallback_content = (
            "I'm sorry, I'm experiencing technical difficulties. "
            "Please try again in a moment."
        )
        ai_message = ChatMessage(
            conversation_id=conversation_id,
            role="model",
            content=fallback_content,
        )
        db.add(ai_message)
        db.commit()
        db.refresh(ai_message)

    # 8) Return temporary read URL to the uploaded user voice clip if requested.
    audio_url: Optional[str] = None
    if include_audio and uploaded_s3_key:
        try:
            audio_url = s3_storage_service.generate_presigned_get_url(
                s3_key=uploaded_s3_key,
                expires_in_seconds=settings.S3_PRESIGNED_URL_TTL_SECONDS,
            )
        except S3StorageError as e:
            logger.warning(
                f"Failed to generate presigned URL for conversation {conversation_id}: {e}"
            )

    return VoiceMessageResponse(
        user_message=ChatMessageResponse.model_validate(user_message),
        ai_response=ChatMessageResponse.model_validate(ai_message),
        audio_url=audio_url,
    )


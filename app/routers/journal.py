"""
Journal router for guided journaling with prompts and voice support.
"""
import logging
from fastapi import APIRouter, HTTPException, status, UploadFile, File
from typing import List, Optional

from app.core.dependencies import CurrentUser, DatabaseSession
from app.models.user import JournalEntry
from app.schemas.journal import (
    JournalEntryCreate,
    JournalEntryUpdate,
    JournalEntryResponse,
    JournalEntryListResponse,
    JournalPromptResponse,
    JournalPromptListResponse,
)
from app.schemas.hearts import HeartsTransactionCreate
from app.services.hearts import award_hearts
from app.services.safety import safety_service
from app.services.notifications import notification_service
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/journal",tags=["journal"])

# Hearts awarded for completing a journal entry
HEARTS_FOR_JOURNAL=10

# Hardcoded journal prompts (can be moved to DB later)
JOURNAL_PROMPTS = [
    {
        "id": "gratitude",
        "title": "Gratitude Reflection",
        "description": "Reflect on things you're grateful for today",
        "prompt_text": "What are three things you're grateful for today? How did they make you feel?",
    },
    {
        "id": "stress_relief",
        "title": "Stress Relief",
        "description": "Express and process your current stressors",
        "prompt_text": "What's causing you stress right now? How can you approach it with self-compassion?",
    },
    {
        "id": "daily_reflection",
        "title": "Daily Reflection",
        "description": "Reflect on your day and how you're feeling",
        "prompt_text": "How was your day? What moments stood out, and how are you feeling now?",
    },
    {
        "id": "future_self",
        "title": "Future Self",
        "description": "Write a letter to your future self",
        "prompt_text": "What would you like to tell your future self? What hopes or advice do you have?",
    },
    {
        "id": "emotions",
        "title": "Emotional Check-in",
        "description": "Explore and name your current emotions",
        "prompt_text": "What emotions are you experiencing right now? Where do you feel them in your body?",
    },
    {
        "id": "achievements",
        "title": "Celebrate Achievements",
        "description": "Acknowledge your wins, big or small",
        "prompt_text": "What did you accomplish today, no matter how small? How does that make you feel?",
    },
]

@router.get("/prompts",response_model=JournalPromptListResponse)
async def get_journal_prompts(current_user:CurrentUser):
    """
    Get available journal prompts for guided reflection.
    
    Returns a list of prompts that users can choose from when creating journal entries.
    """

    prompts= [
        JournalPromptResponse(**p) for p in JOURNAL_PROMPTS
    ]
    return JournalPromptListResponse(prompts=prompts)

@router.post("/entries",response_model=JournalEntryResponse,status_code=status.HTTP_201_CREATED)
async def create_journal_entry(
    payload:JournalEntryCreate,
    current_user:CurrentUser,
    db:DatabaseSession
):
    """
    Create a new journal entry.
    
    mood_at_time and tier_at_time are optional and only set if explicitly provided.
    Awards hearts upon completion.
    """
    
    # Use mood/tier from payload if provided, otherwise None
    mood = payload.mood_at_time
    tier = payload.tier_at_time

        # Safety gate check on journal content
    safety = safety_service.assess_user_message(payload.content)
    if not safety.allowed:
        # Log crisis event
        try:
            from app.models.user import CrisisEvent

            event = CrisisEvent(
                user_id=current_user.id,
                source="journal",
                community_id=None,
                message_excerpt=payload.content[:300],
                risk_level=safety.risk_level,
                matched_phrases=json.dumps(safety.matched_phrases),
            )
            db.add(event)
            db.commit()

            # Notify therapist about journal crisis event
            notification_service.notify_therapist_crisis(event)
        except Exception as e:
            logger.error(f"Failed to create CrisisEvent: {e}")
            db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Journal entry appears to contain high-risk content. Please reach out for support.",
        )
    
    #create journal entry
    entry = JournalEntry(
        user_id=current_user.id,
        content = payload.content,
        mood_at_time=mood,
        tier_at_time=tier,
        xp_gained= HEARTS_FOR_JOURNAL
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)

    # Award hearts for journal completion
    tx = HeartsTransactionCreate(
        amount=HEARTS_FOR_JOURNAL,
        type="journal_entry",
        description="Completed a journal entry",
        reference_id=str(entry.id),
    )
    award_hearts(db, current_user.id, tx)
    
    logger.info(f"Created journal entry {entry.id} for user {current_user.id}, awarded {HEARTS_FOR_JOURNAL} hearts")
    
    return JournalEntryResponse(
        id=entry.id,
        user_id=entry.user_id,
        content= entry.content,
        mood_at_time=entry.mood_at_time,
        tier_at_time=entry.tier_at_time,
        xp_gained=entry.xp_gained,
        created_at=entry.created_at,
    
    )

@router.get("/entries",response_model=JournalEntryListResponse)
async def list_journal_entries(
    current_user:CurrentUser,
    db:DatabaseSession,
    limit:int=20,
    offset:int=0
):
    """
    List journal entries for the current user.
    
    Returns paginated list of entries ordered by most recent first.
    """

    total = db.query(JournalEntry).filter(
        JournalEntry.user_id == current_user.id
    ).count()

    entries = (
        db.query(JournalEntry)
        .filter(JournalEntry.user_id == current_user.id)
        .order_by(JournalEntry.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return JournalEntryListResponse(
        entries = [
            JournalEntryResponse(
                id=e.id,
                user_id=e.user_id,
                content=e.content,
                mood_at_time=e.mood_at_time,
                tier_at_time=e.tier_at_time,
                xp_gained=e.xp_gained,
                created_at=e.created_at,
            )
            for e in entries
        ],
        total=total,
    )

@router.post("/entries/{entry_id}/voice",status_code=status.HTTP_201_CREATED)
async def upload_voice_note(
    entry_id:int,
    file:UploadFile = File(...),
    current_user:CurrentUser=None,
    db:DatabaseSession =None
):
    """
    Upload a voice note for a journal entry (STUB).
    
    This is a placeholder endpoint. In production, this would:
    - Validate the audio file format
    - Store the file (S3, local storage, etc.)
    - Optionally transcribe using speech-to-text API
    - Link the voice note to the journal entry
    
    For now, returns a success message.
    """

    # Verify entry exists and belongs to user
    entry = db.query(JournalEntry).filter(
        JournalEntry.id == entry_id,
        JournalEntry.user_id == current_user.id,
    ).first()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")

    # STUB: In production, process and store the file here
    # For now, just validate it's an audio file
    if not file.content_type or not file.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an audio file",
        )
    
    logger.info(f"Voice note upload stub called for entry {entry_id}, file: {file.filename}")
    
    return {
        "success":True,
        "message":"Voice note upload received (stub implementation)",
        "entry_id":entry.id,
        "filename":file.filename,
        "note": "Full voice note processing not yet implemented",
    }
"""
Chat router handling conversation lifecycle, safety gating, LLM orchestration, and crisis escalation.
"""
import logging
import math
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import CurrentUser, DatabaseSession
from app.models.user import User, UserState, UserProfile, Conversation, ChatMessage, CrisisEvent
from app.schemas.chat import (
    ConversationCreate,
    ConversationResponse,
    ConversationListResponse,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatHistoryResponse
)
from app.services.chat import chat_service
from app.services.safety import safety_service
import json
from app.models.user import CrisisEvent


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])

# XP awarded per message sent
XP_PER_MESSAGE = 5


def calculate_level(xp: int) -> int:
    """
    Calculate user level from XP.
    Formula: floor(xp / 200) + 1
    
    Args:
        xp: Experience points
    
    Returns:
        User level
    """
    return math.floor(xp / 200) + 1


def get_or_create_user_state(db: Session, user_id: int) -> UserState:
    """
    Get existing user state or create a default one.
    
    Args:
        db: Database session
        user_id: User ID
    
    Returns:
        UserState object
    """
    user_state = db.query(UserState).filter(UserState.user_id == user_id).first()
    if not user_state:
        # Create default user state
        user_state = UserState(
            user_id=user_id,
            mood="Grounded",
            risk_tier="Green",
            xp=0,
            level=1,
            steps=0,
            sleep_hours=0,
            pomo_sessions=0
        )
        db.add(user_state)
        db.commit()
        db.refresh(user_state)
    return user_state


def get_user_profile_dict(db: Session, user_id: int) -> Optional[Dict[str, Any]]:
    """
    Get user profile as a dictionary for use in bio context.
    
    Args:
        db: Database session
        user_id: User ID
    
    Returns:
        Dict with bio info or None
    """
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        return None
    
    bio_dict = {}
    if profile.name:
        bio_dict["name"] = profile.name
    if profile.major:
        bio_dict["major"] = profile.major
    if profile.hobbies:
        bio_dict["hobbies"] = profile.hobbies
    if profile.values:
        bio_dict["values"] = profile.values
    if profile.bio:
        bio_dict["bio"] = profile.bio
    
    return bio_dict if bio_dict else None


def add_xp_to_user_state(db: Session, user_id: int, amount: int) -> UserState:
    """
    Add XP to user state and update level.
    
    Args:
        db: Database session
        user_id: User ID
        amount: XP amount to add
    
    Returns:
        Updated UserState object
    """
    user_state = get_or_create_user_state(db, user_id)
    user_state.xp += amount
    user_state.level = calculate_level(user_state.xp)
    db.commit()
    db.refresh(user_state)
    return user_state


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: CurrentUser,
    db: DatabaseSession
):
    """
    Create a new conversation.
    
    If tier, mood, or source are not provided, uses current user state values.
    
    Args:
        conversation_data: Conversation creation data
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Created conversation
    """
    # Get or use current user state
    user_state = get_or_create_user_state(db, current_user.id)
    
    # Use provided values or fall back to user state
    tier = conversation_data.tier or user_state.risk_tier
    mood = conversation_data.mood or user_state.mood
    source = conversation_data.source or user_state.stress_source or "Career/Academics"
    
    # Validate tier and mood
    valid_tiers = {"Green", "Yellow", "Red"}
    valid_moods = {"Heavy", "Pulse", "Grounded"}
    
    if tier not in valid_tiers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tier: {tier}. Must be one of {valid_tiers}"
        )
    if mood not in valid_moods:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid mood: {mood}. Must be one of {valid_moods}"
        )
    
    # Create conversation
    conversation = Conversation(
        user_id=current_user.id,
        tier=tier,
        mood=mood,
        source=source
    )
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    logger.info(f"Created conversation {conversation.id} for user {current_user.id}")
    return conversation


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    current_user: CurrentUser,
    db: DatabaseSession
):
    """
    List all conversations for the current user.
    
    Args:
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        List of conversations
    """
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.created_at.desc()).all()
    
    return ConversationListResponse(conversations=conversations)


@router.get("/conversations/{conversation_id}/messages", response_model=ChatHistoryResponse)
async def get_conversation_messages(
    conversation_id: int,
    current_user: CurrentUser,
    db: DatabaseSession
):
    """
    Get all messages for a specific conversation.
    
    Args:
        conversation_id: Conversation ID
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Conversation and its messages
    
    Raises:
        HTTPException: If conversation not found or doesn't belong to user
    """
    # Get conversation
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Verify ownership
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation"
        )
    
    # Get messages
    messages = db.query(ChatMessage).filter(
        ChatMessage.conversation_id == conversation_id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    return ChatHistoryResponse(conversation=conversation, messages=messages)


@router.post("/conversations/{conversation_id}/messages", response_model=ChatMessageResponse)
async def send_message(
    conversation_id: int,
    message_data: ChatMessageCreate,
    current_user: CurrentUser,
    db: DatabaseSession
):
    """
    Send a message in a conversation and get AI response.
    
    Saves the user message, generates AI response using LLM,
    saves the AI response, and awards XP to the user.
    
    Args:
        conversation_id: Conversation ID
        message_data: Message data (role must be 'user')
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        AI model response message
    
    Raises:
        HTTPException: If conversation not found, doesn't belong to user, or message role is invalid
    """
    # Validate message role
    if message_data.role != "user":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message role must be 'user'. Model responses are generated automatically."
        )
    
    # Get conversation
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Verify ownership
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation"
        )
    
    # Get user state and profile for context
    user_state = get_or_create_user_state(db, current_user.id)
    user_profile = get_user_profile_dict(db, current_user.id)
    
    # Save user message
    user_message = ChatMessage(
        conversation_id=conversation_id,
        role="user",
        content=message_data.content
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    
    logger.info(f"User {current_user.id} sent message in conversation {conversation_id}")

    # Safety Gate check (V1) - run before calling the LLM
    # TODO: Replace keyword heuristics with model-based classifier + eval harness
    safety = safety_service.assess_user_message(message_data.content)
    
    if not safety.allowed:
        # Save a safe model message without calling the LLM
        safe_model_message = ChatMessage(
            conversation_id=conversation_id,
            role="model",
            content=safety.safe_reply,
        )
        db.add(safe_model_message)
        db.commit()
        db.refresh(safe_model_message)

        # Log crisis event for therapist monitoring
        try:
            event = CrisisEvent(
                user_id=current_user.id,
                source="chat",
                community_id=None,
                message_excerpt=message_data.content[:300],
                risk_level=safety.risk_level,
                matched_phrases=json.dumps(safety.matched_phrases),
            )
            db.add(event)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to create CrisisEvent: {e}")

        logger.warning(
            f"Safety gate blocked LLM for user={current_user.id}, "
            f"conversation={conversation_id}, risk_level={safety.risk_level}, "
            f"matches={safety.matched_phrases}"
        )

        # For now, do NOT award XP when safety gate triggers
        return safe_model_message
    
    # Get existing chat history for context
    existing_messages = db.query(ChatMessage).filter(
        ChatMessage.conversation_id == conversation_id,
        ChatMessage.id < user_message.id  # Exclude the message we just added
    ).order_by(ChatMessage.created_at.asc()).all()
    
    # Format chat history for LLM
    chat_history = [
        {"role": msg.role, "content": msg.content}
        for msg in existing_messages
    ]
    
    # Generate AI response using chat service
    try:
        llm_response = await chat_service.generate_response(
            user_message=message_data.content,
            chat_history=chat_history,
            tier=conversation.tier,
            mood=conversation.mood,
            source=conversation.source,
            bio=user_profile,
            other_text=user_state.other_text if conversation.source == "Others" else None
        )
        
        if not llm_response.get("success"):
            logger.error(f"LLM response generation failed: {llm_response.get('error')}")
            # Use fallback content if available
            response_content = llm_response.get("content", "I'm sorry, I'm having trouble responding right now.")
        else:
            response_content = llm_response["content"]
        
        # Save AI response
        model_message = ChatMessage(
            conversation_id=conversation_id,
            role="model",
            content=response_content
        )
        db.add(model_message)
        db.commit()
        db.refresh(model_message)
        
        # Update conversation timestamp
        conversation.updated_at = datetime.now(timezone.utc)
        db.commit()
        
        # Award XP for sending message
        add_xp_to_user_state(db, current_user.id, XP_PER_MESSAGE)
        
        logger.info(f"Generated and saved AI response for conversation {conversation_id}, awarded {XP_PER_MESSAGE} XP")
        
        return model_message
        
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}", exc_info=True)
        # Even if LLM fails, we should save a fallback response
        fallback_content = "I'm sorry, I'm experiencing technical difficulties. Please try again in a moment."
        
        model_message = ChatMessage(
            conversation_id=conversation_id,
            role="model",
            content=fallback_content
        )
        db.add(model_message)
        db.commit()
        db.refresh(model_message)
        
        # Still award XP since user sent a message
        add_xp_to_user_state(db, current_user.id, XP_PER_MESSAGE)
        
        return model_message


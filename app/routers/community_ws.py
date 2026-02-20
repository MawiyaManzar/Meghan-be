"""
WebSocket + REST endpoints for real-time community chat.

Goal: Discord-style chat inside each community (single-instance, in-memory rooms).
"""

import json
import logging
from datetime import datetime
from typing import Dict, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status, Depends
from fastapi.websockets import WebSocketState
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.models.user import User, ProblemCommunity, CommunityMembership, CommunityMessage, CrisisEvent
from app.schemas.community import (
    CommunityMessageCreate,
    CommunityMessageResponse,
    CommunityMessageListResponse,
)
from app.services.safety import safety_service
from app.services.notifications import notification_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/communities", tags=["communities-realtime"])


class ConnectionManager:
    """
    Manages active WebSocket connections per community.
    Single-instance, in-memory (sufficient for current deployment).
    """

    def __init__(self) -> None:
        # community_id -> set of websockets
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, community_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.setdefault(community_id, set()).add(websocket)
        logger.info(f"WebSocket connected for community {community_id}, total={len(self.active_connections[community_id])}")

    def disconnect(self, community_id: int, websocket: WebSocket) -> None:
        try:
            self.active_connections.get(community_id, set()).discard(websocket)
            logger.info(f"WebSocket disconnected for community {community_id}")
        except Exception:
            pass

    async def broadcast(self, community_id: int, message: dict) -> None:
        """
        Broadcast JSON message to all active connections in a community.
        """
        dead: list[WebSocket] = []
        for websocket in self.active_connections.get(community_id, set()):
            try:
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_json(message)
                else:
                    dead.append(websocket)
            except Exception:
                dead.append(websocket)

        for ws in dead:
            self.disconnect(community_id, ws)


manager = ConnectionManager()


def _get_db_session() -> Session:
    """
    Helper to get a DB session for WebSocket flows (no dependency injection).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _authenticate_websocket(token: str, db: Session) -> User:
    """
    Authenticate WebSocket using JWT token (same logic as /api/auth/me).
    """
    from fastapi import HTTPException

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate WebSocket credentials",
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user


def _ensure_community_membership(db: Session, community_id: int, user_id: int) -> ProblemCommunity:
    """
    Ensure the community exists and the user is a member.
    """
    community = (
        db.query(ProblemCommunity)
        .filter(ProblemCommunity.id == community_id, ProblemCommunity.is_active == True)
        .first()
    )
    if not community:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Community not found")

    membership = (
        db.query(CommunityMembership)
        .filter(
            CommunityMembership.user_id == user_id,
            CommunityMembership.community_id == community_id,
        )
        .first()
    )
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a member of this community")

    return community


@router.websocket("/ws/{community_id}")
async def community_chat_ws(websocket: WebSocket, community_id: int):
    """
    WebSocket endpoint for real-time community chat.

    Auth:
      - Expect `?token=<JWT>` query param
    Message format (JSON):
      - {"type": "message", "content": "...", "is_anonymous": true|false}
    Broadcast payload:
      - {"type": "message", "message": CommunityMessageResponse}
    """
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # New DB session for this connection
    db = SessionLocal()
    try:
        # Authenticate user
        user = _authenticate_websocket(token, db)

        # Verify community + membership
        _ensure_community_membership(db, community_id, user.id)
    except HTTPException as e:
        await websocket.accept()
        await websocket.send_json({"type": "error", "detail": e.detail})
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        db.close()
        return
    except Exception as e:
        logger.error(f"WebSocket auth error: {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        db.close()
        return

    # If we reach here, user is authenticated and authorized
    await manager.connect(community_id, websocket)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "detail": "Invalid JSON"})
                continue

            if payload.get("type") != "message":
                await websocket.send_json({"type": "error", "detail": "Unsupported message type"})
                continue

            content = (payload.get("content") or "").strip()
            is_anonymous = bool(payload.get("is_anonymous", True))

            if not content:
                await websocket.send_json({"type": "error", "detail": "Message content cannot be empty"})
                continue
            if len(content) > 2000:
                await websocket.send_json({"type": "error", "detail": "Message too long (max 2000 characters)"})
                continue

            # Safety gate check
            safety = safety_service.assess_user_message(content)
            if not safety.allowed:
                # Log crisis event and notify therapist
                try:
                    event = CrisisEvent(
                        user_id=user.id,
                        source="community",
                        community_id=community_id,
                        message_excerpt=content[:300],
                        risk_level=safety.risk_level,
                        matched_phrases=json.dumps(safety.matched_phrases),
                    )
                    db.add(event)
                    db.commit()
                    notification_service.notify_therapist_crisis(event)
                except Exception as e:
                    logger.error(f"Failed to create CrisisEvent from WS: {e}")
                    db.rollback()

                # Send safe reply only to the sender; do not broadcast
                await websocket.send_json(
                    {
                        "type": "system",
                        "role": "safety",
                        "content": safety.safe_reply,
                    }
                )
                continue

            # Persist community message
            msg = CommunityMessage(
                community_id=community_id,
                user_id=user.id,
                content=content,
                is_anonymous=is_anonymous,
            )
            db.add(msg)
            db.commit()
            db.refresh(msg)

            # Build response DTO
            display_name = "Anonymous" if is_anonymous else user.email
            message_dto = CommunityMessageResponse(
                id=msg.id,
                community_id=community_id,
                user_id=user.id,
                content=msg.content,
                is_anonymous=msg.is_anonymous,
                created_at=msg.created_at,
                display_name=display_name,
            )

            # Broadcast to all members in this community
            await manager.broadcast(
                community_id,
                {
                    "type": "message",
                    "message": json.loads(message_dto.model_dump_json()),
                },
            )

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for community {community_id}")
    except Exception as e:
        logger.error(f"WebSocket error in community {community_id}: {e}", exc_info=True)
    finally:
        manager.disconnect(community_id, websocket)
        db.close()


@router.get("/{community_id}/messages", response_model=CommunityMessageListResponse)
async def list_community_messages(
    community_id: int,
    db: Session = Depends(_get_db_session),
    limit: int = 50,
    offset: int = 0,
):
    """
    REST endpoint to fetch recent messages for a community.
    Useful for loading history when opening the community chat view.
    """
    # Verify community exists
    community = db.query(ProblemCommunity).filter(ProblemCommunity.id == community_id).first()
    if not community:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Community not found")

    q = db.query(CommunityMessage).filter(CommunityMessage.community_id == community_id)
    total = q.count()

    items = (
        q.order_by(CommunityMessage.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    messages = []
    for msg in items:
        # NOTE: display_name is not resolved here (requires join). Frontend can decide.
        messages.append(
            CommunityMessageResponse(
                id=msg.id,
                community_id=msg.community_id,
                user_id=msg.user_id,
                content=msg.content,
                is_anonymous=msg.is_anonymous,
                created_at=msg.created_at,
                display_name=None,
            )
        )

    return CommunityMessageListResponse(messages=messages, total=total)


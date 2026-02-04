from fastapi import APIRouter
from app.core.dependencies import TherapistUser, DatabaseSession
from app.models.user import CrisisEvent
from app.schemas.therapist import CrisisEventResponse, CrisisEventListResponse
import json

router = APIRouter(prefix="/api/therapist", tags=["therapist"])


@router.get("/crisis-events", response_model=CrisisEventListResponse)
async def list_crisis_events(
    current_user: TherapistUser,
    db: DatabaseSession,
    community_id: int | None = None,
    limit: int = 50,
):
    """
    List recent crisis events.
    Access restricted to therapist/admin users via TherapistUser dependency.
    """
    q = db.query(CrisisEvent).order_by(CrisisEvent.created_at.desc())
    if community_id is not None:
        q = q.filter(CrisisEvent.community_id == community_id)

    events = q.limit(limit).all()

    items: list[CrisisEventResponse] = []
    for e in events:
        try:
            matched = json.loads(e.matched_phrases) if e.matched_phrases else []
        except Exception:
            matched = []
        items.append(
            CrisisEventResponse(
                id=e.id,
                user_id=e.user_id,
                source=e.source,
                community_id=e.community_id,
                message_excerpt=e.message_excerpt,
                risk_level=e.risk_level,
                matched_phrases=matched,
                created_at=e.created_at,
            )
        )

    return CrisisEventListResponse(events=items)
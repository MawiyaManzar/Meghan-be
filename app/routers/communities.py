import logging
from fastapi import APIRouter, HTTPException, status
from app.core.dependencies import CurrentUser, DatabaseSession
from app.models.user import ProblemCommunity, CommunityMembership
from app.schemas.community import CommunityListResponse, CommunityResponse, CommunityJoinRequest
from app.services.communities import ensure_default_communities

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/communities", tags=["communities"])

@router.get("", response_model=CommunityListResponse)
async def list_communities(
    current_user: CurrentUser,
    db: DatabaseSession,
    stress_source: str | None = None,  # optional filter
):
    ensure_default_communities(db)

    q = db.query(ProblemCommunity).filter(ProblemCommunity.is_active == True)
    if stress_source:
        q = q.filter(ProblemCommunity.stress_source == stress_source)
    communities = q.all()

    memberships = db.query(CommunityMembership).filter(
        CommunityMembership.user_id == current_user.id
    ).all()
    user_community_ids = [m.community_id for m in memberships]

    return CommunityListResponse(
        communities=communities,
        user_communities=user_community_ids,
    )

@router.post("/{community_id}/join", status_code=status.HTTP_201_CREATED)
async def join_community(
    community_id: int,
    payload: CommunityJoinRequest,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    community = db.query(ProblemCommunity).filter(
        ProblemCommunity.id == community_id,
        ProblemCommunity.is_active == True,
    ).first()
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    membership = db.query(CommunityMembership).filter(
        CommunityMembership.user_id == current_user.id,
        CommunityMembership.community_id == community_id,
    ).first()

    if membership:
        membership.is_anonymous = payload.is_anonymous
        db.commit()
        return {"success": True, "message": "Community already joined; anonymity updated."}

    membership = CommunityMembership(
        user_id=current_user.id,
        community_id=community_id,
        is_anonymous=payload.is_anonymous,
    )
    db.add(membership)
    db.commit()

    return {"success": True, "message": "Joined community successfully."}
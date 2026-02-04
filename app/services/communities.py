import json
import profile
from typing import List
from sqlalchemy.orm import Session
from app.models.user import ProblemCommunity, CommunityMembership, UserProfile

# Positive, unique names; internal 'stress_source' used to filter/match
DEFAULT_COMMUNITIES = [
    {
        "name": "Gentle Heartbreak Circle",
        "description": "A warm space for healing from breakups and relationship pain.",
        "stress_source": "Relationship",
    },
    {
        "name": "Healthy Love & Boundaries",
        "description": "Support for building healthy relationships and self-respect.",
        "stress_source": "Relationship",
    },
    {
        "name": "Calm Career Path",
        "description": "Support for study stress, career confusion, and pressure.",
        "stress_source": "Career/Academics",
    },
    {
        "name": "Family Balance Circle",
        "description": "Support for family stress, expectations, and conflicts.",
        "stress_source": "Family",
    },
]


# Map struggle keywords -> stress_source (internal only; not shown to user)
STRUGGLE_TO_STRESS_SOURCE = {
    "career": "Career/Academics",
    "academics": "Career/Academics",
    "studies": "Career/Academics",
    "focus": "Career/Academics",

    "relationship": "Relationship",
    "breakup": "Relationship",
    "loneliness": "Relationship",
    "dating": "Relationship",

    "family": "Family",
    "home": "Family",
}

def _decode_struggles(raw:str|None)->List[str]:
    if not raw:
        return []
    try:
        value= json.loads(raw)
        if isinstance(value, list):
            return [str(v).lower() for v in value]

    except Exception:
        pass
    
    return[str(raw).lower()]

def ensure_default_communities(db: Session) -> None:
    """Create default positive communities once (shared by services and router)."""
    if db.query(ProblemCommunity).count() == 0:
        for c in DEFAULT_COMMUNITIES:
            db.add(ProblemCommunity(**c))
        db.commit()


def auto_assign_communities_for_user(db:Session,user_id:int,profile:UserProfile)->None:
    """
    Join the user to appropriate ProblemCommunity rows based on profile.struggles.
    - This does NOT expose any tags to the user.
    - It only uses internal mapping to pick relevant communities.
    """

    # make sure base communities exist
    ensure_default_communities(db)

    struggles = _decode_struggles(profile.struggles)
    if not struggles:
        return 
    
    #collect stress sources we care
    target_sources:set[str]= set()
    for s in struggles:
        if s in STRUGGLE_TO_STRESS_SOURCE:
            target_sources.add(STRUGGLE_TO_STRESS_SOURCE[s])
    
    if not target_sources:
        return
    
    # fetch communities for these sources

    communities =( db.query(ProblemCommunity)
    .filter(
        ProblemCommunity.is_active == True,
        ProblemCommunity.stress_source.in_(list(target_sources))
        )
    .all()
    )
    
    # Existing memberships to avoid duplicates
    existing = db.query(CommunityMembership).filter(
        CommunityMembership.user_id == user_id
    ).all()
    existing_ids = {m.community_id for m in existing}

    created_any = False
    for community in communities:
        if community.id in existing_ids:
            continue
        m = CommunityMembership(
            user_id=user_id,
            community_id=community.id,
            is_anonymous=True,  # default to anonymous
        )
        db.add(m)
        created_any = True

    if created_any:
        db.commit()

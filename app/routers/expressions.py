from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import expression

from app.core.dependencies import CurrentUser, DatabaseSession
from app.models.user import MicroExpression, EmpathyResponse, CrisisEvent, ProblemCommunity
from app.schemas.expressions import (
    MicroExpressionCreate,
    MicroExpressionResponse,
    EmpathyResponseCreate,
    EmpathyResponseResponse,
    MicroExpressionListResponse,
)
from app.schemas.hearts import HeartsTransactionCreate
from app.services.hearts import award_hearts
from app.services.safety import safety_service

import json
from typing import List


router = APIRouter(prefix="/api/expressions", tags=["expressions"])


HEARTS_FOR_EXPRESSION = 5
HEARTS_FOR_EMPATHY = 3

@router.post("",response_model = MicroExpressionResponse, status_code=status.HTTP_201_CREATED)
async def create_expression(
    payload:MicroExpressionCreate,
    current_user:CurrentUser,
    db:DatabaseSession
):

        # 280-char limit is already enforced by Pydantic Field, but double-check defensively
    if len(payload.content) > 280:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="content must be at most 280 characters",
        )
    
    safety = safety_service.assess_user_message(payload.content)
    if not safety.allowed:
        # Log crisis event (source: community/expression)

        try:
            event = CrisisEvent(
                user_id=current_user.id,
                source="community",
                community_id=payload.community_id,
                message_excerpt = payload.content[:300],
                risk_level=safety.risk_level,
                matched_phrases= json.dumps(safety.matched_phrases)
            )
            db.add(event)
            db.commit()

        except Exception:
            db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message appears to contain high-risk content and cannot be posted.",
        )

        # Optional: validate community_id exists if provided
    if payload.community_id is not None:
            community = db.query(ProblemCommunity).filter(
            ProblemCommunity.id == payload.community_id,
            ProblemCommunity.is_active == True,
            ).first()
    if not community:
            raise HTTPException(status_code=404, detail="Community not found")
    
    expression = MicroExpression(
        user_id = current_user.id,
        community_id=payload.community_id,
        content = payload.content,
        is_anonymous=payload.is_anonymous
    )
    db.add(expression)
    db.commit()
    db.refresh(expression)

    #awards hearts to author
    tx = HeartsTransactionCreate(
        amount=HEARTS_FOR_EXPRESSION,
        type = "expression_post",
        description="Posted a micro expression",
        reference_id= str(expression.id)
    )

    award_hearts(db,current_user.id,tx)

    return MicroExpressionResponse(
        id=expression.id,
        content= expression.content,
        community_id=expression.community_id,
        is_anonymous=expression.is_anonymous,
        created_at= expression.created_at,
        hearts_awarded=HEARTS_FOR_EXPRESSION
    )

@router.get("",response_model=MicroExpressionListResponse)
async def list_expression(
    db:DatabaseSession,
    current_user = CurrentUser,
    community_id:int|None =None,
    limit:int=20,
    offset:int=0
):

    q= db.query(MicroExpression)

    if community_id is not None:
        q = q.filter(MicroExpression.community_id == community_id)

    total= q.count()
    items:List(MicroExpression) = (
        q.order_by(MicroExpression.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return MicroExpressionListResponse(
        items=[
            MicroExpressionResponse(
                id=e.id,
                content=e.content,
                community_id=e.community_id,
                is_anonymous=e.is_anonymous,
                created_at=e.created_at,
                hearts_awarded=None,
            )
            for e in items
        ],
        total = total,
        limit = limit,
        offset = offset
    )

@router.post("/{expression_id}/empathy",response_model=EmpathyResponseResponse,status_code=status.HTTP_201_CREATED,)
async def add_empathy_response(
    expression_id: int,
    payload: EmpathyResponseCreate,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    if len(payload.content)>280:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="content must be at most 280 characters",
        )
    
    expression = db.query(MicroExpression).filter(
        MicroExpression.id == expression_id
    ).first()
    if not expression:
        raise HTTPException(status_code=404,detail="Expression not found")
    
    safety = safety_service.assess_user_message(payload.content)
    if not safety.allowed:
        try:
            event = CrisisEvent(
                user_id= current_user.id,
                source = "community",
                community_id= expression.community_id,
                message_excerpt= payload.content[:300],
                risk_level= safety.risk_level,
                matched_phrases= json.dumps(safety.matched_phrases)
            )
            db.add(event)
            db.commit()
        except Exception:
            db.rollback()
        
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail="Response appears to contain high-risk content and cannot be posted.",
        )
    response = EmpathyResponse(
        expression_id = expression.id,
        user_id = current_user.id,
        content= payload.content,
        is_anonymous= payload.is_anonymous
    )

    db.add()
    db.commit()
    db.refresh(response)

    tx = HeartsTransactionCreate(
        amount=HEARTS_FOR_EMPATHY,
        type="empathy_response",
        description = "Posted an empathy response",
        reference_id= str(response.id)
    )
    award_hearts(db,current_user.id,tx)

    return EmpathyResponseResponse(
        id=response.id,
        expression_id=response.expression_id,
        content=response.content,
        is_anonymous=response.is_anonymous,
        created_at=response.created_at,
    )


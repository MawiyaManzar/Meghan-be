"""
Hearts currency endpoints.

- GET /api/hearts/balance  -> current balance + totals
- POST /api/hearts/earn    -> award hearts (internal / protected)
"""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import CurrentUser, DatabaseSession
from app.schemas.hearts import HeartsBalance, HeartsTransactionCreate, HeartsTransactionResponse
from app.services.hearts import get_hearts_balance, award_hearts

router = APIRouter(prefix="/api/hearts", tags=["hearts"])

@router.get("/balance", response_model=HeartsBalance)
async def get_balance(
    current_user: CurrentUser,
    db: DatabaseSession,
):
    """
    Get current hearts balance and totals for the authenticated user.
    """
    return get_hearts_balance(db, current_user.id)

@router.post("/earn", response_model=HeartsTransactionResponse, status_code=status.HTTP_201_CREATED)
async def earn_hearts(
    payload: HeartsTransactionCreate,
    current_user: CurrentUser,
    db: DatabaseSession,
):
    """
    Award hearts to the current user.

    This is intended to be called from other backend flows (chat, journaling, etc.)
    For now it just appends a transaction to the ledger.
    """
    if payload.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="amount must be positive for earn endpoint",
        )

    return award_hearts(db, current_user.id, payload)
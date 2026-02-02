from sqlalchemy.orm import Session
from app.models.user import HeartsTransaction
from app.models.user import UserState
from app.schemas.hearts import HeartsBalance, HeartsTransactionCreate, HeartsTransactionResponse

def get_hearts_balance(db: Session, user_id: int) -> HeartsBalance:
    """Calculate hearts balance and totals from the transaction ledger."""
    q = db.query(HeartsTransaction).filter(HeartsTransaction.user_id == user_id)

    total_earned = 0
    total_redeemed = 0
    for tx in q:
        if tx.amount > 0:
            total_earned += tx.amount
        else:
            total_redeemed += -tx.amount

    balance = total_earned - total_redeemed
    return HeartsBalance(
        balance=balance,
        total_earned=total_earned,
        total_redeemed=total_redeemed,
    )

def award_hearts(db: Session, user_id: int, data: HeartsTransactionCreate) -> HeartsTransactionResponse:
    """
    Append a new hearts transaction and return it.
    This does NOT do any business rules (like max balance); it's a simple ledger write.
    """
    # Get current balance from last transaction (faster than recomputing all)
    last_tx = (
        db.query(HeartsTransaction)
        .filter(HeartsTransaction.user_id == user_id)
        .order_by(HeartsTransaction.created_at.desc())
        .first()
    )

    current_balance = last_tx.balance_after if last_tx else 0
    new_balance = current_balance + data.amount

    tx = HeartsTransaction(
        user_id=user_id,
        amount=data.amount,
        type=data.type,
        description=data.description,
        reference_id=data.reference_id,
        balance_after=new_balance,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)

    return HeartsTransactionResponse.model_validate(tx)
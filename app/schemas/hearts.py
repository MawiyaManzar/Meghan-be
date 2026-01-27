from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List

class HeartsBalance(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    balance: int
    total_earned: int
    total_redeemed: int

class HeartsTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    amount: int
    type: str
    description: str
    reference_id: str | None = None
    balance_after: int
    created_at: datetime

class HeartsTransactionCreate(BaseModel):
    amount: int
    type: str
    description: str
    reference_id: str | None = None

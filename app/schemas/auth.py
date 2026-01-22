from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: str
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = Field(default="bearer")


class TokenData(BaseModel):
    email: Optional[str] = None
from datetime import datetime
from typing import Optional,List
from pydantic import BaseModel,Field,ConfigDict

class MicroExpressionCreate(BaseModel):
    content: str = Field(..., max_length=280)
    community_id: Optional[int] = None
    is_anonymous: bool = True

class MicroExpressionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:int
    content:str
    community_id:Optional[int] = None
    is_anonymous:bool
    created_at:datetime
    hearts_awarded:Optional[int] = None

class EmpathyResponseCreate(BaseModel):
   content:str=Field(..., max_length=280, description="The content of the empathy response")
   is_anonymous:bool=True

class EmpathyResponseResponse(BaseModel):
   model_config = ConfigDict(from_attributes=True)

   id:int
   expression_id:int
   content:str
   is_anonymous:bool
   created_at:datetime

class MicroExpressionWithResponses(BaseModel):
   model_config = ConfigDict(from_attributes= True)

   expression:MicroExpressionResponse
   responses:List[EmpathyResponseResponse] = []

class MicroExpressionListResponse(BaseModel):
    items: List[MicroExpressionResponse]
    total: int
    limit: int
    offset: int
# app/schemas/quiz.py
from pydantic import BaseModel, Field
from datetime import datetime
from app.utils.util import StatusType

class QuizCreate(BaseModel):
    creator_id: int
    title: str
    description: str
    status: StatusType = Field(..., description="Status of the quiz")
    

class QuizRead(BaseModel):
    id: int
    creator_id: int
    title: str
    description: str
    join_code: str
    created_at: datetime

    class Config:
        from_attributes = True


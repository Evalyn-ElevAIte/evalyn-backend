# app/schemas/quiz.py
from pydantic import BaseModel, Field
from datetime import datetime
from app.utils.util import StatusType

class QuizCreate(BaseModel):
    creator_id: int
    title: str
    description: str
    status: StatusType = Field(..., description="Status of the quiz")
    lecturer_overall_notes: str = Field(
        None, max_length=255, description="Overall notes from the lecturer"
    )
    
    

class QuizRead(BaseModel):
    id: int
    creator_id: int
    title: str
    description: str
    join_code: str
    created_at: datetime

    class Config:
        from_attributes = True


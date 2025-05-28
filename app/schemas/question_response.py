from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class QuestionResponseBase(BaseModel):
    question_id: int = Field(..., description="ID of the question being answered")
    answers: List[str] = Field(..., description="Student's answer to the question")

class QuestionResponseCreate(QuestionResponseBase):
    pass

class QuestionResponseRead(QuestionResponseBase):
    id: int
    question_id: int = Field(..., description="ID of the question being answered")
    joined_at: datetime
    
    class Config:
        from_attributes = True

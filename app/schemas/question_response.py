from pydantic import BaseModel, Field
from datetime import datetime

class QuestionResponseBase(BaseModel):
    question_id: int = Field(..., description="ID of the question being answered")
    answer: str = Field(..., description="Student's answer to the question")

class QuestionResponseCreate(QuestionResponseBase):
    pass

class QuestionResponseRead(QuestionResponseBase):
    id: int
    user_id: int = Field(..., description="ID of the student who answered")
    created_at: datetime
    
    class Config:
        from_attributes = True

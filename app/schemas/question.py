from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from .quiz import QuizRead  # if you also want to nest quiz data
from models import AnswerType

# Shared properties
class QuestionBase(BaseModel):
    # ... means required
    text: str = Field(..., description="Full question text")
    type: AnswerType = Field(
        AnswerType.TEXT,
        description="Answer format: text, video, multiple choice, or pdf"
    )
    rubric: str = Field(..., max_length=100, description="Grading rubric or points")

# Properties to receive on creation
class QuestionCreate(QuestionBase):
    quiz_id: int = Field(..., description="ID of the quiz this question belongs to")

# Properties to receive on updates (all optional)
class QuestionUpdate(BaseModel):
    text: Optional[str] = Field(None, description="Updated question text")
    type: Optional[AnswerType] = Field(None, description="Updated delivery format")
    rubric: Optional[str] = Field(
        None, max_length=100, description="Updated rubric or points"
    )

# Properties to return to the client
class QuestionRead(QuestionBase):
    id: int
    quiz_id: int = Field(..., description="ID of the parent quiz")
    created_at: datetime

    class Config:
        orm_mode = True


# Optionally, if you want to nest the quiz data inside your question responses:
class QuestionReadWithQuiz(QuestionRead):
    quiz: QuizRead

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from .quiz import QuizRead  # if you also want to nest quiz data
from app.models.models import AnswerType

# Shared properties
class QuestionBase(BaseModel):
    # ... means required
    text: str = Field(..., description="Full question text")
    type: AnswerType = Field(
        AnswerType.ESSAY,
        description="Answer format: text / essay or multiple choices"
    )
    rubric: str = Field(..., max_length=100, description="Grading rubric or points")

# Properties to receive on creation
class QuestionCreate(QuestionBase):
    quiz_id: int = Field(..., description="ID of the quiz this question belongs to")
    lecturer_answer_text: Optional[str] = Field(None, description="Lecturer's answer for essay questions")
    options: Optional[str] = Field(None, description="JSON string of options for multiple choice questions")
    correct_answer_mc: Optional[str] = Field(None, description="Correct answer for multiple choice questions")

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
    lecturer_answer_text: Optional[str]
    options: Optional[str]
    correct_answer_mc: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Optionally, if you want to nest the quiz data inside your question responses:
class QuestionReadWithQuiz(QuestionRead):
    quiz: QuizRead

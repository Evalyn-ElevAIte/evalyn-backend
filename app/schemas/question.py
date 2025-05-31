from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.utils.util import AnswerType, StatusType  # Assuming this is your Enum

class QuestionCreate(BaseModel):
    text: str
    type: AnswerType
    options: Optional[List[str]] = None
    expected_answer: Optional[List[str]] = None
    rubric: str
    rubric_max_score: int = Field(default=100)

class QuizWithQuestionsCreate(BaseModel):
    title: str
    description: str
    duration: int
    lecturer_overall_notes: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    completed: bool = False
    questions: List[QuestionCreate]


class QuestionRead(BaseModel):
    id: int
    quiz_id: int
    text: str
    type: AnswerType
    options: Optional[List[str]] = None
    expected_answer: Optional[List[str]] = None
    rubric: str
    rubric_max_score: int
    created_at: datetime

    class Config:
        from_attributes = True

class QuestionReadForStudent(BaseModel):
    id: int
    quiz_id: int
        from_attributes = True

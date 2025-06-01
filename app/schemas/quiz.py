# app/schemas/quiz.py
from pydantic import BaseModel, Field
from datetime import datetime
from app.utils.util import StatusType
from typing import Optional
from typing import List
from app.schemas.question import QuestionRead, QuestionReadForStudent


class QuizCreate(BaseModel):
    title: str
    description: str
    # status: StatusType = Field(..., description="Status of the quiz")
    lecturer_overall_notes: str
    start_time: datetime | None = None
    end_time: datetime | None = None
    duration: Optional[int] = None
    completed: bool = False

class QuizRead(BaseModel):
    id: int
    creator_id: int
    title: str
    description: str
    join_code: str
    created_at: datetime

    class Config:
        from_attributes = True

class QuizWithStatusAll(BaseModel):
    id: int
    title: str
    description: str
    created_at: datetime
    end_time: datetime
    join_code: str
    duration: Optional[int] = None
    status: Optional[StatusType] = None  # Nullable field
    completed: Optional[bool] = None     # Nullable field
    question_counts: Optional[int]= None 

class QuizWithStatus(BaseModel):
    id: int
    title: str
    description: str
    created_at: datetime
    end_time: datetime
    join_code: str
    status: StatusType


class QuizWithStatusCreator(BaseModel):
    title: str
    description: str
    created_at: datetime
    completed: bool

class QuizReadWithQuestions(BaseModel):
    id: int
    creator_id: int
    title: str
    description: str
    join_code: str
    duration: Optional[int]
    created_at: datetime
    questions: List[QuestionReadForStudent]

    class Config:
        from_attributes = True

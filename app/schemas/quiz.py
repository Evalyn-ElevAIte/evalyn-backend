# app/schemas/quiz.py
from pydantic import BaseModel, constr
from datetime import datetime

class QuizCreate(BaseModel):
    creator_id: int
    title: str
    description: str

class QuizRead(BaseModel):
    id: int
    creator_id: int
    title: str
    description: str
    join_code: str
    created_at: datetime

    class Config:
        orm_mode = True
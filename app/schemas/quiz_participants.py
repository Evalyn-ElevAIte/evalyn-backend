from pydantic import BaseModel
from enum import Enum


class JoinQuizRequest(BaseModel):
    join_code: str


class JoinQuizResponse(BaseModel):
    message: str
    participant_id: int

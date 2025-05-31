from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from app.models.models import StatusType  

class JoinQuizRequest(BaseModel):
    join_code: str


class JoinQuizResponse(BaseModel):
    message: str
    participant_id: int


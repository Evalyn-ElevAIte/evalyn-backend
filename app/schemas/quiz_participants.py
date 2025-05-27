from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime

# (reuse your StatusType enum if you already defined one; otherwise, re‐import it)
from models import StatusType  

class QuizParticipantBase(BaseModel):
    user_id: int = Field(..., description="ID of the user joining the quiz")
    quiz_id: int = Field(..., description="ID of the quiz to join")
    status: StatusType = Field(
        StatusType.UNFINISHED,
        description="Participant status (e.g. UNFINISHED, IN_PROGRESS, COMPLETED)",
    )

    class Config:
        from_attributes = True


class QuizParticipantCreate(QuizParticipantBase):
    """
    All fields required to create a new QuizParticipant.
    Inherits user_id, quiz_id, status from QuizParticipantBase.
    """
    pass


class QuizParticipantRead(QuizParticipantBase):
    """
    Fields returned to the client after creation/read.
    Adds `id` and `joined_at` (auto‐populated by the DB).
    """
    id: int
    joined_at: datetime

from fastapi import APIRouter, Depends, HTTPException
from app.models.models import User, Quiz, QuizParticipant
from app.schemas.quiz_participants import QuizParticipantBase
from app.utils.util import StatusType

router = APIRouter()

@router.post("/join-quiz")
async def join_quiz(data: QuizParticipantBase):
    # Fetch the quiz
    quiz = await Quiz.get_or_none(id=data.quiz_id).prefetch_related("creator")
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Determine status based on creator
    if data.user_id == quiz.creator_id:
        status = StatusType.PUBLISHED
    else:
        status = StatusType.UNFINISHED

    # Create the participant entry
    participant = await QuizParticipant.create(
        user_id=data.user_id,
        quiz_id=data.quiz_id,
        status=status
    )

    return {"message": "User joined quiz", "participant_id": participant.id}

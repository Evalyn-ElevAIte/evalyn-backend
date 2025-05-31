from fastapi import APIRouter, Depends, HTTPException
from app.models.models import User, Quiz, QuizParticipant
from app.schemas.quiz_participants import JoinQuizRequest, JoinQuizResponse
from app.utils.util import StatusType
from tortoise.exceptions import IntegrityError
from app.dependencies import get_current_user

router = APIRouter()

@router.post("/join-by-code", response_model=JoinQuizResponse)
async def join_quiz_by_code(
    data: JoinQuizRequest,
    current_user: User = Depends(get_current_user)
):
    quiz = await Quiz.get_or_none(join_code=data.join_code)
    if not quiz:
        raise HTTPException(status_code=404, detail="Invalid join code")

    # Determine status
    if quiz.creator_id != current_user.id:
        status = StatusType.UNFINISHED
    else:
        raise HTTPException(status_code=400, detail="You are the creator")

    # Prevent duplicate entry
    if await QuizParticipant.filter(user=current_user.id, quiz=quiz.id).exists():
        raise HTTPException(status_code=400, detail="Already joined this quiz")

    try:
        participant = await QuizParticipant.create(
            user=current_user,
            quiz=quiz,
            status=status
        )
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Already joined this quiz")

    return {
        "message": "Successfully joined quiz",
        "participant_id": participant.id
    }


# @router.post("/join-quiz")
# async def join_quiz(data: QuizParticipantBase):
#     # Fetch the quiz
#     quiz = await Quiz.get_or_none(id=data.quiz_id).prefetch_related("creator")
#     if not quiz:
#         raise HTTPException(status_code=404, detail="Quiz not found")
    
#     # Determine status based on creator
#     if data.user_id == quiz.creator_id:
#         status = StatusType.PUBLISHED
#     else:
#         status = StatusType.UNFINISHED

#     # Create the participant entry
#     participant = await QuizParticipant.create(
#         user_id=data.user_id,
#         quiz_id=data.quiz_id,
#         status=status
#     )

#     return {"message": "User joined quiz", "participant_id": participant.id}

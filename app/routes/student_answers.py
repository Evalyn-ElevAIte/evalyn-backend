from fastapi import APIRouter, Depends, HTTPException
from tortoise.exceptions import IntegrityError
from app.models.models import QuestionResponse, Question, QuizParticipant
from schemas.question_response import QuestionResponseCreate, QuestionResponseRead
from app.dependencies import get_current_user
from datetime import datetime

router = APIRouter(
    prefix="/api/student/answers",
    tags=["student_answers"]
)

@router.post("/", response_model=QuestionResponseRead)
async def submit_answer(
    response_data: QuestionResponseCreate,
    current_user=Depends(get_current_user)
):
    # Check if question exists
    question = await Question.get_or_none(id=response_data.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Check if user is participant in the quiz
    participant = await QuizParticipant.get_or_none(
        user_id=current_user.id,
        quiz_id=question.quiz_id
    )
    if not participant:
        raise HTTPException(
            status_code=403,
            detail="You are not a participant in this quiz"
        )

    try:
        # Create response
        response = await QuestionResponse.create(
            user_id=current_user.id,
            question_id=response_data.question_id,
            answer=response_data.answer
        )
        return await QuestionResponseRead.from_tortoise_orm(response)
    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="You have already answered this question"
        )

@router.get("/{question_id}", response_model=QuestionResponseRead)
async def get_answer(
    question_id: int,
    current_user=Depends(get_current_user)
):
    response = await QuestionResponse.get_or_none(
        user_id=current_user.id,
        question_id=question_id
    )
    if not response:
        raise HTTPException(status_code=404, detail="Answer not found")
    return await QuestionResponseRead.from_tortoise_orm(response)
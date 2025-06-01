from fastapi import APIRouter, Depends, HTTPException
from tortoise.exceptions import DoesNotExist
from app.models.models import Question, User
from app.schemas.question import QuestionCreate, QuestionRead
from app.dependencies import get_current_user
from tortoise.contrib.pydantic import pydantic_model_creator
from app.models.models import QuestionResponse, Question, QuizParticipant, Quiz


router = APIRouter()

Question_Pydantic = pydantic_model_creator(Question, name="Question")

@router.post("/", response_model=Question_Pydantic)
async def create_question(
    payload: QuestionCreate,
    current_user: User = Depends(get_current_user)
):
    # Optional: Check if quiz exists
    try:
        from app.models.models import Quiz
        quiz = await Quiz.get(id=payload.quiz_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Quiz not found")

    question = await Question.create(
        quiz_id=payload.quiz_id,
        text=payload.text,
        type=payload.type,
        options=payload.options,
        expected_anwer=payload.expected_anwer,
        rubric=payload.rubric,
        rubric_max_score=payload.rubric_max_score
    )
    return await Question_Pydantic.from_tortoise_orm(question)


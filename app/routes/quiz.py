# app/routes/quiz.py
from fastapi import APIRouter, HTTPException
from tortoise.exceptions import IntegrityError
from app.models.models import Quiz
from app.schemas.quiz import QuizCreate, QuizRead
from app.utils.util import make_join_code
from tortoise.contrib.pydantic import pydantic_model_creator

Quiz_Pydantic = pydantic_model_creator(
    Quiz, name="Quiz", exclude=("questions", "participants")
)

router = APIRouter(tags=["quizzes"], prefix="/quizzes")

# ! get all quizzes
@router.get("", response_model=list[Quiz_Pydantic])
async def get_quizzes():
    return await Quiz.all()


# ! create a quiz
@router.post("", response_model=Quiz_Pydantic)
async def create_quiz(payload: QuizCreate):
    # generate a code, retry on collision
    for _ in range(5):
        code = make_join_code(6)
        try:
            quiz = await Quiz.create(
                creator_id=payload.creator_id,
                title=payload.title,
                description=payload.description,
                # status=payload.status,
                join_code=code,
            )
            return await Quiz_Pydantic.from_tortoise_orm(quiz)
        except IntegrityError:
            # join_code clash, try again
            continue
    raise HTTPException(500, "Could not generate a unique join code, please retry")
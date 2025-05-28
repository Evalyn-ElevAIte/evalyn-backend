# app/routes/quiz.py
from fastapi import APIRouter, HTTPException, Depends
from tortoise.exceptions import IntegrityError
from app.models.models import Quiz, User
from app.schemas.quiz import QuizCreate, QuizRead
from app.utils.util import make_join_code
from tortoise.contrib.pydantic import pydantic_model_creator
from app.dependencies import get_current_user


Quiz_Pydantic = pydantic_model_creator(
    Quiz, name="Quiz", exclude=("questions", "participants")
)

router = APIRouter(dependencies=[Depends(get_current_user)])

# ! get all quizzes
@router.get("/", response_model=list[Quiz_Pydantic])
async def get_quizzes():
    return await Quiz.all()

# ! create a quiz
@router.post("/", response_model=Quiz_Pydantic)
async def create_quiz(payload: QuizCreate, current_user: User = Depends(get_current_user)):
    # Generate a unique join code with retry
    for _ in range(5):
        code = make_join_code(6)

        try:
            quiz = await Quiz.create(
                creator_id=current_user.id,  # use token-based user
                title=payload.title,
                description=payload.description,
                lecturer_overall_notes=payload.lecturer_overall_notes,
                start_time=payload.start_time,
                end_time=payload.end_time,
                completed=payload.completed,
                join_code=code
            )
            return await Quiz_Pydantic.from_tortoise_orm(quiz)

        except IntegrityError:
            continue  # retry if join_code is not unique

    raise HTTPException(status_code=500, detail="Could not generate a unique join code, please retry")
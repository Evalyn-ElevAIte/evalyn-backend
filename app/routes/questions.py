from typing import List
from fastapi import APIRouter, HTTPException, status
from tortoise.exceptions import DoesNotExist

from models import Question as QuestionModel
from schemas.question import (
    QuestionCreate,
    QuestionRead,
)

router = APIRouter(prefix="/questions", tags=["questions"])

@router.get("/quiz/{quiz_id}", response_model=List[QuestionRead])
async def get_questions_by_quiz(quiz_id: int):
    """
    Retrieve all questions belonging to a specific quiz by its ID.
    """
    questions = await QuestionModel.filter(quiz_id=quiz_id).all()
    return [QuestionRead.from_orm(q) for q in questions]

@router.post("/", response_model=QuestionRead, status_code=status.HTTP_201_CREATED)
async def create_question(data: QuestionCreate):
    """
    Create a new question under a specified quiz.
    """
    # Ensure the parent quiz exists
    try:
        # This will raise if no quiz with that ID
        await QuestionModel._meta.fields['quiz'].related_model.get(id=data.quiz_id)
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz with id {data.quiz_id} not found"
        )

    question = await QuestionModel.create(**data.dict())
    return QuestionRead.from_orm(question)

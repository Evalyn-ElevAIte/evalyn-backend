# app/routes/quiz.py
from fastapi import APIRouter, HTTPException, Depends
from tortoise.exceptions import IntegrityError
from app.models.models import Quiz, User, Question, QuizParticipant
from app.schemas.quiz import QuizCreate, QuizRead, QuizWithStatusAll
from app.schemas.question import QuizWithQuestionsCreate

from app.utils.util import make_join_code
from tortoise.contrib.pydantic import pydantic_model_creator
from app.dependencies import get_current_user


Quiz_Pydantic = pydantic_model_creator(
    Quiz, name="Quiz", exclude=("questions", "participants")
)

router = APIRouter()

# ! get all quizzes
@router.get("/", response_model=list[Quiz_Pydantic])
async def get_quizzes():
    return await Quiz.all()

# ! get by kuis id
@router.get("/{quiz_id}", response_model=QuizWithStatusAll)
async def get_quiz_by_id(quiz_id: int, current_user: User = Depends(get_current_user)):
    # Try to find participation
    participation = await QuizParticipant.filter(user=current_user.id, quiz_id=quiz_id).prefetch_related("quiz").first()
    if participation:
        quiz_obj = participation.quiz
        question_count = await Question.filter(quiz=quiz_obj).count()
        return {
            "id": quiz_obj.id,
            "title": quiz_obj.title,
            "description": quiz_obj.description,
            "created_at": quiz_obj.created_at,
            "end_time": quiz_obj.end_time,
            "join_code": quiz_obj.join_code,
            "duration": quiz_obj.duration,
            "status": participation.status,
            "completed": None,
            "question_count": question_count
        }

    # Try to find as creator
    quiz = await Quiz.filter(creator=current_user.id, id=quiz_id).first()
    if quiz:
        question_count = await Question.filter(quiz=quiz).count()
        return {
            "id": quiz.id,
            "title": quiz.title,
            "description": quiz.description,
            "created_at": quiz.created_at,
            "end_time": quiz.end_time,
            "join_code": quiz.join_code,
            "duration": quiz.duration,
            "status": None,
            "completed": quiz.completed,
            "question_count": question_count
        }

    raise HTTPException(status_code=200, detail="Quiz not found. You either not enrolled in this quiz or you are not the creator of this quiz")


# ! create a quiz with questions
@router.post("/create-with-questions")
async def create_quiz_with_questions(
    payload: QuizWithQuestionsCreate,
    current_user: User = Depends(get_current_user)
):
    for _ in range(5):
        code = make_join_code(6)
        try:
            quiz = await Quiz.create(
                creator=current_user,
                title=payload.title,
                description=payload.description,
                lecturer_overall_notes=payload.lecturer_overall_notes,
                start_time=payload.start_time,
                end_time=payload.end_time,
                duration=payload.duration,
                join_code=code,
            )
            break
        except IntegrityError:
            continue
    else:
        raise HTTPException(status_code=500, detail="Could not generate a unique join code")

    # Create questions
    for q in payload.questions:
        await Question.create(
            quiz=quiz,
            text=q.text,
            type=q.type,
            options=q.options,
            expected_answer=q.expected_answer,
            rubric=q.rubric,
            rubric_max_score=q.rubric_max_score,
        )

    return {"message": "Quiz and questions created successfully", "quiz_id": quiz.id}


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
                duration=payload.duration,
                completed=payload.completed,
                join_code=code
            )
            return await Quiz_Pydantic.from_tortoise_orm(quiz)

        except IntegrityError:
            continue  # retry if join_code is not unique

    raise HTTPException(status_code=500, detail="Could not generate a unique join code, please retry")

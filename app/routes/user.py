# app/routes/user.py

from fastapi import APIRouter, HTTPException
from app.models.models import User
from app.models.models import Quiz
from app.models.models import QuizParticipant

from tortoise.contrib.pydantic import pydantic_model_creator

router = APIRouter()

# ! Create a Pydantic serializer for the User model
User_Pydantic = pydantic_model_creator(User, name="User")
User_Pydantic_With_Quizzes = pydantic_model_creator(User, name="UserWithQuizzes", exclude=("password",))
Quiz_Pydantic = pydantic_model_creator(Quiz, name="Quiz")


# ! get all user
@router.get("/users", response_model=list[User_Pydantic])
async def get_users():
    return await User.all()

# ! get user by id
@router.get("/users/{user_id}", response_model=User_Pydantic)
async def get_user(user_id: int):
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ! get kuis yang diikuti oleh user
@router.get("/users/{user_id}/quizzes", response_model=list[Quiz_Pydantic])
async def get_user_quizzes(user_id: int):
    participations  = await QuizParticipant.filter(user=user_id).prefetch_related("quiz")
    if not participations:
        raise HTTPException(status_code=404, detail="User's quizzes not found")
    
    quizzes = [p.quiz for p in participations]
    
    return quizzes 

# ! get data kuis yang diikuti oleh user
@router.get("/users/{user_id}/quizzes/{quiz_id}", response_model=Quiz_Pydantic)
async def get_user_quiz(user_id: int, quiz_id: int):
    quiz = await QuizParticipant.get_or_none(user=user_id, quiz=quiz_id).prefetch_related("quiz")
    if not quiz:
        raise HTTPException(status_code=404, detail="User's Quiz not found")
    
    return quiz.quiz

# ! get user ini buat kuis apa aja
@router.get("/users/{user_id}/quizzes_creator", response_model=list[Quiz_Pydantic])
async def get_user_participants(user_id: int):
    quizes = await Quiz.filter(creator=user_id).prefetch_related("participants__user")
    if not quizes:
        raise HTTPException(status_code=404, detail="No quizzes found for this user")
    return quizes
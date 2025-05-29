# app/routes/user.py
from fastapi import APIRouter, HTTPException, Depends, status
from app.models.models import User, Quiz, QuizParticipant
from app.dependencies import get_current_user
from app.schemas.quiz import QuizWithStatusAll, QuizWithStatus, QuizWithStatusCreator
from itertools import chain
from tortoise.contrib.pydantic import pydantic_model_creator

# router = APIRouter(dependencies=[Depends(get_current_user)])
router = APIRouter()

# ! Create a Pydantic serializer for the User model
User_Read_Plain = pydantic_model_creator(User, name="UserPlain")
User_Pydantic_Read = pydantic_model_creator(User, name="UserNoPass", exclude=("password","id"))
Quiz_Pydantic = pydantic_model_creator(Quiz, name="Quiz")

# ! get all user
@router.get("/all_users", response_model=list[User_Read_Plain])
async def get_users():
    return await User.all()

# ! get user by id
@router.get('/', response_model=User_Pydantic_Read)
async def get_user(current_user: User = Depends(get_current_user)):
    return current_user

# ! get seluruh kuis user (creator dan participant)
@router.get('/quizzes/all', response_model=list[QuizWithStatusAll])
async def get_all_user_quizzes(current_user: User = Depends(get_current_user)):
    # Quizzes where user is a participant
    participations = await QuizParticipant.filter(user=current_user.id).prefetch_related("quiz")
    
    # Quizzes where user is the creator
    created_quizzes = await Quiz.filter(creator=current_user.id)

    # Combine both, converting them to a unified QuizWithStatus structure
    combined = []

    for p in participations:
        combined.append({
            "title": p.quiz.title,
            "description": p.quiz.description,
            "created_at": p.quiz.created_at,
            "status": p.status
        })

    for q in created_quizzes:
        combined.append({
            "title": q.title,
            "description": q.description,
            "created_at": q.created_at,
            "completed": q.completed
        })

    # Sort all quizzes by created_at descending
    combined.sort(key=lambda x: x["created_at"], reverse=True)

    return combined

# ! get kuis yang diikuti oleh user
@router.get('/quizzes', response_model=list[QuizWithStatus])
async def get_user_quizzes(current_user: User = Depends(get_current_user)):
    participations = await QuizParticipant.filter(user=current_user.id).prefetch_related("quiz").order_by("-quiz__created_at")
    if not participations:
        raise HTTPException(status_code=404, detail="User's quizzes not found")
    
    result = [
        QuizWithStatus(
            id = p.quiz.id,
            title=p.quiz.title,
            description=p.quiz.description,
            created_at=p.quiz.created_at,
            status=p.status
        )
        for p in participations
    ]
    
    return result 

# ! get user ini buat kuis apa aja
@router.get('/quizzes_creator', response_model=list[Quiz_Pydantic])
async def get_user_quizzes_creator(current_user: User = Depends(get_current_user)):
    quizes = await Quiz.filter(creator=current_user.id).prefetch_related("participants__user")
    if not quizes:
        raise HTTPException(status_code=404, detail="No quizzes found for this user")
    return quizes
    
# # ! get data kuis yang diikuti oleh user
# @router.get("/{user_id}/quizzes/{quiz_id}", response_model=Quiz_Pydantic)
# async def get_user_quiz(user_id: int, quiz_id: int):
#     quiz = await QuizParticipant.get_or_none(user=user_id, quiz=quiz_id).prefetch_related("quiz")
#     if not quiz:
#         raise HTTPException(status_code=404, detail="User's Quiz not found")
    
#     return quiz.quiz

# # ! get user ini buat kuis apa aja
# @router.get("/{user_id}/quizzes_creator", response_model=list[Quiz_Pydantic])
# async def get_user_participants(user_id: int):
#     quizes = await Quiz.filter(creator=user_id).prefetch_related("participants__user")
#     if not quizes:
#         raise HTTPException(status_code=404, detail="No quizzes found for this user")
#     return quizes

# # ! get kuis yang diikuti oleh user
# @router.get('/quizzes', response_model=list[Quiz_Pydantic])
# async def get_user_quizzes(current_user: User = Depends(get_current_user)):
#     print('user id : ',current_user.id)
#     participations = await QuizParticipant.filter(user=current_user.id).prefetch_related("quiz")
#     print(current_user.id)
#     if not participations:
#         raise HTTPException(status_code=404, detail="User's quizzes not found")
    
#     quizzes = [p.quiz for p in participations]
    
#     return quizzes 
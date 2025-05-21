# app/routes/user.py

from fastapi import APIRouter, HTTPException
from app.models.models import User
from tortoise.contrib.pydantic import pydantic_model_creator

router = APIRouter()

# Create a Pydantic serializer for the User model
User_Pydantic = pydantic_model_creator(User, name="User")
User_Pydantic_With_Quizzes = pydantic_model_creator(User, name="UserWithQuizzes", exclude=("password",))

@router.get("/users/{user_id}/quizzes", response_model=User_Pydantic_With_Quizzes)
async def get_user_quizzes(user_id: int):
    user = await User.get_or_none(id=user_id).prefetch_related("participants__quiz")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

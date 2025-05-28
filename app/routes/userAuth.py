from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.schemas.userAuth import LoginSchema
from app.schemas.user import UserCreate
from app.models.models import User
from app.utils.util import hash_password, verify_password
from app.auth import create_access_token
from tortoise.contrib.pydantic import pydantic_model_creator

UserRead = pydantic_model_creator(User, name="UserRead", exclude=["password"])

router = APIRouter()

# ! REGISTER
@router.post("/register")
async def create_user(payload: UserCreate):
    if await User.filter(email=payload.email).exists():
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(payload.password)
    await User.create(
        name=payload.name,
        email=payload.email,
        password=hashed
    )

    return JSONResponse(
        status_code=201,
        content={"message": "User successfully registered"}
    )

# ! LOGIN
@router.post('/login')
async def login(payload: LoginSchema):
    user = await User.get_or_none(email=payload.email)
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=401, detail='Invalid email or password')

    token_data = {"sub": str(user.id)}
    access_token = create_access_token(data=token_data)

    return JSONResponse(
        status_code=200,
        content={
            "access_token": access_token,
            "token_type": "bearer"
        }
    )
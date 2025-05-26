from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.auth import verify_access_token
from app.models.models import User

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token:str = Depends(oauth_scheme)):
    payload = verify_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await User.get_or_none(id=payload["sub"])
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

# secret key to encode/decode JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCES_TOKEN_EXPIRED = 1440

# create acces token
def create_access_token(data:dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCES_TOKEN_EXPIRED))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token:str):
    try:
        payload=jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return print('Invalid token')
    
# app/core/utils.py
from passlib.context import CryptContext
import random
import string
from enum import Enum

# helper class
class AnswerType(str, Enum):
    TEXT  = "text"
    # VIDEO = "video"
    # PDF   = "pdf"
    MULTI_CHOICE = "multi_choice"
    SINGLE_CHOICE = "single_choice"
    
class StatusType(str, Enum):
    # # TEACHER
    # PUBLISHED  = "published"
    # DONE = "done"
    # STUDENT
    UNFINISHED   = "unfinished"
    SUBMITED = "submited"
    GRADED = "graded"

# password helper function
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# create randomize join code
def make_join_code(length: int = 8) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(random.choices(alphabet, k=length))
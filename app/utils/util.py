# app/core/utils.py
from passlib.context import CryptContext
import random
import string
from enum import Enum

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AnswerType(str, Enum):
    TEXT  = "text"
    VIDEO = "video"
    PDF   = "pdf"
    CHOICE = "choice"
    
class StatusType(str, Enum):
    # TEACHER
    PUBLISHED  = "published"
    DONE = "done"
    # STUDENT
    UNFINISHED   = "unfinished"
    SUBMITED = "submited"
    GRADED = "graded"

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def make_join_code(length: int = 8) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(random.choices(alphabet, k=length))
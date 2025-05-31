# app/core/utils.py
from passlib.context import CryptContext
import random
import string
from enum import Enum
import httpx
from dotenv import load_dotenv
import os

load_dotenv()

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

# ! new api
async def check_ai_with_sapling(text: str) -> dict | None:
    url = "https://api.sapling.ai/api/v1/aidetect"
    api_key = os.getenv("SAPLING_API_KEY")  # Make sure this is set

    payload = {
        "key": api_key,
        "text": text
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()  # Returns the full API response as dict
    except httpx.HTTPError as e:
        print(f"Sapling API error: {e}")
        return None


# ai plagiarism
async def check_ai_plagiarism(text: str, version: str = "v1") -> float | None:
    url = os.getenv('AI_URL_WEB')
    api_key = os.getenv('AI_DETECTOR_KEY')
    

    if not url or not api_key:
        raise ValueError("AI_URL_WEB or AI_DETECTOR_KEY environment variable is not set.")

    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "text": text,
        "version": version
    }
    
    print(f'payload : {payload}')

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("score")  # Adjust if the key is named differently
    except (httpx.HTTPError, ValueError, KeyError) as e:
        # Log error and return None or fallback value
        print(f"Plagiarism API error: {e}")
        return None
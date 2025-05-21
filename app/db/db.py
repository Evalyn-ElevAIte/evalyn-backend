# app/db/db.py

from tortoise import Tortoise
from dotenv import load_dotenv
import os

load_dotenv()

async def init_db():
    
    await Tortoise.init(
        db_url=os.getenv("DATABASE_URL"),
        modules={"models": ["app.models.models"]}
        )
    await Tortoise.generate_schemas()

async def close_db():
    await Tortoise.close_connections()
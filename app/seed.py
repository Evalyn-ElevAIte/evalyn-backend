import asyncio
from app.db.db import init_db, close_db
from app.models.models import User, Quiz, Question, QuizParticipant

async def seed():
    await init_db()
    
    await QuizParticipant.all().delete()
    await Question.all().delete()
    await Quiz.all().delete()
    await User.all().delete()
    
    # create users
    user1 = await User.create(name="Dadan Widodok", email="k4K0s@example.com", password="admin")
    user2 = await User.create(name="Mayun suharjono", email="4l9oR@example.com", password="admin")
    
    # Create Quizzes
    quiz1 = await Quiz.create(title="Math Quiz", description="test math", join_code="MATH123", creator=user1)
    quiz2 = await Quiz.create(title="Science Quiz", description="test Science", join_code="SCI456", creator=user2)

    # Create Questionss
    # await Question.create(quiz=quiz1, text="What is 2+2?", type="text", criteria="Must be 4")
    # await Question.create(quiz=quiz2, text="What is H2O?", type="text", criteria="Must be water")

    # Add Participants
    await QuizParticipant.create(user=user2, quiz=quiz1)
    await QuizParticipant.create(user=user1, quiz=quiz2)
    
    print("✅ Seed complete.")
    await close_db()
    
if __name__ == "__main__":
    asyncio.run(seed())
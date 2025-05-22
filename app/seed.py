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
    user2 = await User.create(name="Mayun Suharjono", email="4l9oR@example.com", password="admin")
    user3 = await User.create(name="Alice Johnson", email="alice@example.com", password="password123")
    user4 = await User.create(name="Bob Smith", email="bob@example.com", password="password123")
    user5 = await User.create(name="Charlie Brown", email="charlie@example.com", password="password123")
    user6 = await User.create(name="David Wilson", email="david@example.com", password="password123")
    user7 = await User.create(name="Eva Green", email="eva@example.com", password="password123")
    user8 = await User.create(name="Frank Wright", email="frank@example.com", password="password123")
    user9 = await User.create(name="Grace Lee", email="grace@example.com", password="password123")
    user10 = await User.create(name="Henry Clark", email="henry@example.com", password="password123")
    
    # Create Quizzes
    quiz1 = await Quiz.create(title="Math Quiz", description="test math", join_code="MATH123", creator=user1)
    quiz2 = await Quiz.create(title="Science Quiz", description="test Science", join_code="SCI456", creator=user2)
    quiz3 = await Quiz.create(title="History Quiz", description="test History", join_code="HIST789", creator=user3)
    quiz4 = await Quiz.create(title="Geography Quiz", description="test Geography", join_code="GEO999", creator=user4)
    quiz5 = await Quiz.create(title="Art Quiz", description="test Art", join_code="ART101", creator=user5)
    quiz6 = await Quiz.create(title="Programming Quiz", description="test Programming", join_code="PROG456", creator=user1)
    quiz7 = await Quiz.create(title="Biology Quiz", description="test Biology", join_code="BIO789", creator=user2)
    quiz8 = await Quiz.create(title="Physics Quiz", description="test Physics", join_code="PHYS123", creator=user3)
    quiz9 = await Quiz.create(title="Economy Quiz", description="test Economy", join_code="ECON456", creator=user4)
    quiz10 = await Quiz.create(title="Philosophy Quiz", description="test Philosophy", join_code="PHIL789", creator=user5)
    quiz11 = await Quiz.create(title="Chemistry Quiz", description="test Chemistry", join_code="CHEM101", creator=user1)
    quiz12 = await Quiz.create(title="Computer Science Quiz", description="test Computer Science", join_code="CS101", creator=user2)
    quiz13 = await Quiz.create(title="Math Problem Solving Quiz", description="test Math Problem Solving", join_code="MATHPS101", creator=user3)
    quiz14 = await Quiz.create(title="Science Problem Solving Quiz", description="test Science Problem Solving", join_code="SCIPROB101", creator=user4)
    quiz15 = await Quiz.create(title="History Problem Solving Quiz", description="test History Problem Solving", join_code="HISTPROB1", creator=user5)

    # Create Questionss
    # await Question.create(quiz=quiz1, text="What is 2+2?", type="text", criteria="Must be 4")
    # await Question.create(quiz=quiz2, text="What is H2O?", type="text", criteria="Must be water")

    # Add Participants
    for i in range(1, 11):
        for j in range(1, 16):
            await QuizParticipant.create(user=eval(f"user{i}"), quiz=eval(f"quiz{j}"))
    # await QuizParticipant.create(user=user10, quiz=quiz2)
    
    print("✅ Seed complete.")
    await close_db()
    
if __name__ == "__main__":
    asyncio.run(seed())
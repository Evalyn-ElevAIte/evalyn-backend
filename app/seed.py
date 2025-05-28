import asyncio
from app.db.db import init_db, close_db
from app.models.models import User, Quiz, Question, QuizParticipant
from app.utils.util import AnswerType, StatusType, hash_password, make_join_code


async def seed():
    await init_db()
    
    await QuizParticipant.all().delete()
    await Question.all().delete()
    await Quiz.all().delete()
    await User.all().delete()
    
    # create users
    user1 = await User.create(name="Dadan Widodok", email="k4K0s@example.com", password=hash_password("admin"))
    user2 = await User.create(name="Mayun Suharjono", email="4l9oR@example.com", password=hash_password("admin"))
    user3 = await User.create(name="Alice Johnson", email="alice@example.com", password=hash_password("admin"))
    user4 = await User.create(name="Bob Smith", email="bob@example.com", password=hash_password("admin"))
    user5 = await User.create(name="Charlie Brown", email="charlie@example.com", password=hash_password("admin"))
    user6 = await User.create(name="David Wilson", email="david@example.com", password=hash_password("admin"))
    user7 = await User.create(name="Eva Green", email="eva@example.com", password=hash_password("admin"))
    user8 = await User.create(name="Frank Wright", email="frank@example.com", password=hash_password("admin"))
    user9 = await User.create(name="Grace Lee", email="grace@example.com", password=hash_password("admin"))
    user10 = await User.create(name="Henry Clark", email="henry@example.com", password=hash_password("admin"))
    
    # Create Quizzes
    import random
    from datetime import datetime, timedelta

    def random_datetime():
        start = datetime.now() - timedelta(days=30)
        end = datetime.now()
        return start + timedelta(
            seconds=random.randint(0, int((end-start).total_seconds())),
        )

    quiz1 = await Quiz.create(title="Math Quiz", description="test math", join_code="MATH123", creator=user1, lecturer_overall_notes='test notes', completed=False, start_time=random_datetime(), end_time=random_datetime())
    quiz2 = await Quiz.create(title="Science Quiz", description="test Science", join_code="SCI456", creator=user2, lecturer_overall_notes='ini notes dari lecturer', completed=False, start_time=random_datetime(), end_time=random_datetime())
    quiz3 = await Quiz.create(title="History Quiz", description="test History", join_code="HIST789", creator=user3, lecturer_overall_notes='ini notes dari lecturer untuk historia', completed=False, start_time=random_datetime(), end_time=random_datetime())
    quiz4 = await Quiz.create(title="Geography Quiz", description="test Geography", join_code="GEO999", creator=user4, lecturer_overall_notes='ini notes dari lecturer untuk geographia', completed=False, start_time=random_datetime(), end_time=random_datetime())
    quiz5 = await Quiz.create(title="Art Quiz", description="test Art", join_code="ART101", creator=user5, lecturer_overall_notes='ini notes dari lecturer untuk art', completed=False, start_time=random_datetime(), end_time=random_datetime())
    quiz6 = await Quiz.create(title="Programming Quiz", description="test Programming", join_code="PROG456", creator=user1, lecturer_overall_notes='ini notes dari lecturer untuk programming', completed=False, start_time=random_datetime(), end_time=random_datetime())
    quiz7 = await Quiz.create(title="Biology Quiz", description="test Biology", join_code="BIO789", creator=user2, lecturer_overall_notes='ini notes dari lecturer untuk biology', completed=False, start_time=random_datetime(), end_time=random_datetime())
    quiz8 = await Quiz.create(title="Physics Quiz", description="test Physics", join_code="PHYS123", creator=user3, lecturer_overall_notes='ini notes dari lecturer untuk physics', completed=False, start_time=random_datetime(), end_time=random_datetime())
    quiz9 = await Quiz.create(title="Economy Quiz", description="test Economy", join_code="ECON456", creator=user4, lecturer_overall_notes='ini notes dari lecturer untuk economy', completed=False, start_time=random_datetime(), end_time=random_datetime())
    quiz10 = await Quiz.create(title="Philosophy Quiz", description="test Philosophy", join_code="PHIL789", creator=user5, lecturer_overall_notes='ini notes dari lecturer untuk philosophy', completed=False, start_time=random_datetime(), end_time=random_datetime())

    # Create Questionss
    # await Question.create(quiz=quiz1, text="What is 2+2?", type=AnswerType.TEXT, rubric="Must be good listener", rubric_max_score=10)
    # await Question.create(quiz=quiz2, text="What is H2O?", type=AnswerType.TEXT, rubric="specific and definable", rubric_max_score=8)
    # await Question.create(quiz=quiz3, text="What is 2+2?", type=AnswerType.TEXT, rubric="details", rubric_max_score=7)
    # await Question.create(quiz=quiz4, text="What is H2O?", type=AnswerType.TEXT, rubric="critical thinking", rubric_max_score=9)

    # Add Participants
    for i in range(1, 11):
        for j in range(1, 11):
            if i%2 == 0:
                status=StatusType.DONE
            else:
                status=StatusType.UNFINISHED
            await QuizParticipant.create(user=eval(f"user{i}"), quiz=eval(f"quiz{j}"), status=status)
    # await QuizParticipant.create(user=user10, quiz=quiz2)
    
    print("✅ Seed complete.")
    await close_db()
    
if __name__ == "__main__":
    asyncio.run(seed())
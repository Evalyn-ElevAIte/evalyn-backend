import asyncio
from app.db.db import init_db, close_db
from app.models.models import User, Quiz, Question, QuizParticipant, QuestionResponse
from app.utils.util import AnswerType, StatusType, hash_password, make_join_code
import random
from datetime import datetime, timedelta

async def seed():
    print('Seeding started')
    await init_db()
    
    # await QuizParticipant.all().delete()
    # await Question.all().delete()
    # await Quiz.all().delete()
    # await User.all().delete()
    
    # # create users
    # user1 = await User.create(name="Dadan Widodok", email="k4K0s@example.com", password=hash_password("admin"))
    # user2 = await User.create(name="Mayun Suharjono", email="4l9oR@example.com", password=hash_password("admin"))
    # user3 = await User.create(name="Alice Johnson", email="alice@example.com", password=hash_password("admin"))
    # user4 = await User.create(name="Bob Smith", email="bob@example.com", password=hash_password("admin"))
    # user5 = await User.create(name="Charlie Brown", email="charlie@example.com", password=hash_password("admin"))
    # user6 = await User.create(name="David Wilson", email="david@example.com", password=hash_password("admin"))
    # user7 = await User.create(name="Eva Green", email="eva@example.com", password=hash_password("admin"))
    # user8 = await User.create(name="Frank Wright", email="frank@example.com", password=hash_password("admin"))
    # user9 = await User.create(name="Grace Lee", email="grace@example.com", password=hash_password("admin"))
    # user10 = await User.create(name="Henry Clark", email="henry@example.com", password=hash_password("admin"))
    # print('User Seed Done')
    
    
    # # Create Quizzes
    # def random_datetime():
    #     start = datetime.now() - timedelta(days=30)
    #     end = datetime.now()
    #     return start + timedelta(
    #         seconds=random.randint(0, int((end-start).total_seconds())),
    #     )

    # quiz1 = await Quiz.create(title="Math Quiz", description="test math", join_code="MATH123", creator=user1, lecturer_overall_notes='test notes', completed=False, start_time=random_datetime(), end_time=random_datetime())
    # quiz2 = await Quiz.create(title="Science Quiz", description="test Science", join_code="SCI456", creator=user2, lecturer_overall_notes='ini notes dari lecturer', completed=False, start_time=random_datetime(), end_time=random_datetime())
    # quiz3 = await Quiz.create(title="History Quiz", description="test History", join_code="HIST789", creator=user3, lecturer_overall_notes='ini notes dari lecturer untuk historia', completed=False, start_time=random_datetime(), end_time=random_datetime())
    # quiz4 = await Quiz.create(title="Geography Quiz", description="test Geography", join_code="GEO999", creator=user4, lecturer_overall_notes='ini notes dari lecturer untuk geographia', completed=False, start_time=random_datetime(), end_time=random_datetime())
    # quiz5 = await Quiz.create(title="Art Quiz", description="test Art", join_code="ART101", creator=user5, lecturer_overall_notes='ini notes dari lecturer untuk art', completed=False, start_time=random_datetime(), end_time=random_datetime())
    # quiz6 = await Quiz.create(title="Programming Quiz", description="test Programming", join_code="PROG456", creator=user1, lecturer_overall_notes='ini notes dari lecturer untuk programming', completed=False, start_time=random_datetime(), end_time=random_datetime())
    # quiz7 = await Quiz.create(title="Biology Quiz", description="test Biology", join_code="BIO789", creator=user2, lecturer_overall_notes='ini notes dari lecturer untuk biology', completed=False, start_time=random_datetime(), end_time=random_datetime())
    # quiz8 = await Quiz.create(title="Physics Quiz", description="test Physics", join_code="PHYS123", creator=user3, lecturer_overall_notes='ini notes dari lecturer untuk physics', completed=False, start_time=random_datetime(), end_time=random_datetime())
    # quiz9 = await Quiz.create(title="Economy Quiz", description="test Economy", join_code="ECON456", creator=user4, lecturer_overall_notes='ini notes dari lecturer untuk economy', completed=False, start_time=random_datetime(), end_time=random_datetime())
    # quiz10 = await Quiz.create(title="Philosophy Quiz", description="test Philosophy", join_code="PHIL789", creator=user5, lecturer_overall_notes='ini notes dari lecturer untuk philosophy', completed=False, start_time=random_datetime(), end_time=random_datetime())
    # print('Quiz Seed Done')

    # # Create Questionss
    # question1 = await Question.create(
    #     quiz=quiz1,
    #     text="What is the capital of France?",
    #     type=AnswerType.SINGLE_CHOICE,
    #     rubric="Must be precise",
    #     rubric_max_score=10,
    #     options=["Paris", "Berlin", "Madrid", "Rome"],
    #     expected_answer=["Paris"]
    # )
    # question2 = await Question.create(
    #     quiz=quiz2,
    #     text="Who wrote 'Hamlet'?",
    #     type=AnswerType.SINGLE_CHOICE,
    #     rubric="Must show understanding",
    #     rubric_max_score=10,
    #     options=["Shakespeare", "Hemingway", "Tolkien", "Orwell"],
    #     expected_answer=["Shakespeare"]
    # )
    # question3 = await Question.create(
    #     quiz=quiz3,
    #     text="What is the chemical symbol for Gold?",
    #     type=AnswerType.SINGLE_CHOICE,
    #     rubric="Must be accurate",
    #     rubric_max_score=10,
    #     options=["Au", "Ag", "Pb", "Fe"],
    #     expected_answer=["Au"]
    # )
    # question4 = await Question.create(
    #     quiz=quiz4,
    #     text="What is the 2 largest planet in our solar system?",
    #     type=AnswerType.MULTI_CHOICE,
    #     rubric="Must be knowledgeable",
    #     rubric_max_score=10,
    #     options=["Jupiter", "Mars", "Earth", "Venus"],
    #     expected_answer=["Jupiter", "Mars"]
    # )
    # question5 = await Question.create(
    #     quiz=quiz5,
    #     text="Which element does 'O' represent on the periodic table?",
    #     type=AnswerType.MULTI_CHOICE,
    #     rubric="Must be correct",
    #     rubric_max_score=10,
    #     options=["Oxygen", "Hydrogen", "Carbon", "Nitrogen"],
    #     expected_answer=["Oxygen", "Hydrogen"]
    # )
    # question6 = await Question.create(
    #     quiz=quiz6,
    #     text="Explain the theory of relativity.",
    #     type=AnswerType.TEXT,
    #     rubric="Must be thorough",
    #     rubric_max_score=10,
    #     expected_answer=["The theory of relativity, developed by Albert Einstein, encompasses two theories: special relativity and general relativity. It fundamentally changed the understanding of space, time, and gravity."]
    # )
    # question7 = await Question.create(
    #     quiz=quiz7,
    #     text="Describe the process of photosynthesis.",
    #     type=AnswerType.TEXT,
    #     rubric="Must include essential details",
    #     rubric_max_score=10,
    #     expected_answer=["Photosynthesis is the process by which green plants and some other organisms use sunlight to synthesize foods with the help of chlorophyll and carbon dioxide. It produces oxygen as a by-product."]
    # )
    # question8 = await Question.create(
    #     quiz=quiz8,
    #     text="Discuss the impact of World War II on global politics.",
    #     type=AnswerType.TEXT,
    #     rubric="Must be analytical",
    #     rubric_max_score=10,
    #     expected_answer=["World War II significantly altered global politics, leading to the formation of the United Nations, the Cold War, and the decolonization movements in Asia and Africa."]
    # )
    # question9 = await Question.create(
    #     quiz=quiz9,
    #     text="What is the significance of the law of supply and demand?",
    #     type=AnswerType.TEXT,
    #     rubric="Must demonstrate understanding",
    #     rubric_max_score=10,
    #     expected_answer=["The law of supply and demand is a fundamental economic concept that describes the relationship between the supply of a product and the desire for that product. It affects price and market equilibrium."]
    # )
    # question10 = await Question.create(
    #     quiz=quiz10,
    #     text="Outline the key principles of democracy.",
    #     type=AnswerType.TEXT,
    #     rubric="Must be comprehensive",
    #     rubric_max_score=10,
    #     expected_answer=["Democracy is founded on principles such as the rule of law, equal representation, free and fair elections, protection of human rights, and the active participation of the citizenry."]
    # )

    # print('Questionss Seed Done')

    # # Add Participants
    # for i in range(1, 11):
    #     for j in range(1, 11):
    #         status = random.choice([StatusType.UNFINISHED, StatusType.SUBMITED, StatusType.GRADED])
    #         await QuizParticipant.create(user=eval(f"user{i}"), quiz=eval(f"quiz{j}"), status=status)
    # print('Participants Seed Done')
    
    # answer seeder
    users = [await User.get(id=i) for i in range(1, 11)]
    print('were here 1')

    # Fetch the single question with id=1
    question = await Question.get(id=1)
    print('were here 2')
    

    # Create responses for each user, all for question 1
    # await QuestionResponse.create(user=users[0], question=question, answer={"text": "Paris"})
    # await QuestionResponse.create(user=users[1], question=question, answer={"text": "Berlin"})
    await QuestionResponse.create(user=users[2], question=question, answer={"text": "Madrid"})
    await QuestionResponse.create(user=users[3], question=question, answer={"text": "Rome"})
    await QuestionResponse.create(user=users[4], question=question, answer={"text": "Paris"})
    await QuestionResponse.create(user=users[5], question=question, answer={"text": "Berlin"})
    await QuestionResponse.create(user=users[6], question=question, answer={"text": "Paris"})
    await QuestionResponse.create(user=users[7], question=question, answer={"text": "Rome"})
    await QuestionResponse.create(user=users[8], question=question, answer={"text": "Madrid"})
    await QuestionResponse.create(user=users[9], question=question, answer={"text": "Paris"})

    # Fetch users with id 1 to 10
    users = [await User.get(id=i) for i in range(1, 11)]

    # Fetch the question with id=4
    question = await Question.get(id=4)

    # Create responses
    await QuestionResponse.create(user=users[0], question=question, answer={"text": ["Jupiter", "Mars"]})
    await QuestionResponse.create(user=users[1], question=question, answer={"text": ["Jupiter", "Earth"]})
    await QuestionResponse.create(user=users[2], question=question, answer={"text": ["Mars", "Venus"]})
    await QuestionResponse.create(user=users[3], question=question, answer={"text": ["Jupiter", "Mars", "Earth"]})
    await QuestionResponse.create(user=users[4], question=question, answer={"text": ["Mars"]})
    await QuestionResponse.create(user=users[5], question=question, answer={"text": ["Jupiter"]})
    await QuestionResponse.create(user=users[6], question=question, answer={"text": ["Earth", "Venus"]})
    await QuestionResponse.create(user=users[7], question=question, answer={"text": ["Jupiter", "Mars"]})
    await QuestionResponse.create(user=users[8], question=question, answer={"text": ["Jupiter", "Venus"]})
    await QuestionResponse.create(user=users[9], question=question, answer={"text": ["Jupiter", "Mars"]})
    
    # answer seeders for question8 (essay/text)
    # Fetch users with id 1 to 10
    users = [await User.get(id=i) for i in range(1, 11)]

    # Fetch question with id=8
    question = await Question.get(id=8)

    # Create responses for question 8 (essay/text)
    await QuestionResponse.create(
        user=users[0],
        question=question,
        answer={"text": "World War II reshaped international alliances, gave rise to the United Nations, and shifted the balance of power between the US and the Soviet Union."}
    )
    await QuestionResponse.create(
        user=users[1],
        question=question,
        answer={"text": "The war led to massive geopolitical changes, including the division of Germany, the start of the Cold War, and the acceleration of decolonization."}
    )
    await QuestionResponse.create(
        user=users[2],
        question=question,
        answer={"text": "After World War II, the world saw the emergence of two superpowers, the USA and USSR, which influenced global politics for decades."}
    )
    await QuestionResponse.create(
        user=users[3],
        question=question,
        answer={"text": "World War II created a demand for international cooperation, leading to institutions like the UN and NATO to promote peace and stability."}
    )
    await QuestionResponse.create(
        user=users[4],
        question=question,
        answer={"text": "WWII caused a huge shift in colonial powers, sparking independence movements across Africa and Asia, altering the global political landscape."}
    )
    await QuestionResponse.create(
        user=users[5],
        question=question,
        answer={"text": "The war's end led to the Cold War, as ideological tensions grew between capitalist and communist states."}
    )
    await QuestionResponse.create(
        user=users[6],
        question=question,
        answer={"text": "World War II marked the beginning of American dominance in international affairs and weakened many European powers."}
    )
    await QuestionResponse.create(
        user=users[7],
        question=question,
        answer={"text": "Following the war, new political systems were put in place in occupied nations, and the groundwork for the EU began."}
    )
    await QuestionResponse.create(
        user=users[8],
        question=question,
        answer={"text": "It led to massive reconstruction efforts, the Marshall Plan, and a new focus on international diplomacy and peacekeeping."}
    )
    await QuestionResponse.create(
        user=users[9],
        question=question,
        answer={"text": "The geopolitical tension from WWII shaped the latter half of the 20th century, with proxy wars and nuclear arms races dominating global politics."}
    )
    print('question asnwer done')
    
    
    print("✅ Seed complete.")
    await close_db()
    
if __name__ == "__main__":
    asyncio.run(seed())
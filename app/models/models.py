from tortoise import fields
from tortoise.models import Model
from app.utils.util import AnswerType, StatusType


# ! helper functions

class User(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255, unique=True)
    password = fields.CharField(max_length=128)
    created_at = fields.DatetimeField(auto_now_add=True)
    
    """
    reverse relation: it defines the reverse access to the related Quiz models. 
    Its like saying: 
        “This user can have many quizzes that they have created.”
        
    with this we can acces:
        user.quizzes.all()
    """
    quizzes: fields.ReverseRelation["Quiz"] # reverse relation
    participants: fields.ReverseRelation["QuizParticipant"]

class Quiz(Model):
    id = fields.IntField(pk=True)
    creator = fields.ForeignKeyField("models.User", related_name="quizzes")
    title = fields.CharField(max_length=64)
    description = fields.CharField(max_length=255)
    lecturer_overall_notes = fields.TextField(null=True)
    join_code = fields.CharField(max_length=10, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    questions: fields.ReverseRelation["Question"]
    participants: fields.ReverseRelation["QuizParticipant"]

class Question(Model):
    id = fields.IntField(pk=True)
    quiz = fields.ForeignKeyField("models.Quiz", related_name="questions")
    question_id = fields.CharField(max_length=255)  # Matches prompt_generator.py
    text = fields.TextField()
    type = fields.CharField(max_length=50)  # e.g., "text", "video", "pdf"
    student_answer_text = fields.TextField(null=True)  # Matches prompt_generator.py
    lecturer_answer_text = fields.TextField(null=True)  # For text/essay answers
    options = fields.TextField(null=True)  # Stores JSON string of options for multiple choice
    correct_answer_mc = fields.TextField(null=True) # Stores the correct answer for multiple choice
    rubric = fields.TextField()  # Matches prompt_generator.py
    rubric_max_score = fields.IntField(default=0)  # Matches prompt_generator.py
    created_at = fields.DatetimeField(auto_now_add=True)

class QuizParticipant(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="participants")
    quiz = fields.ForeignKeyField("models.Quiz", related_name="participants")
    status = fields.CharEnumField(StatusType)
    joined_at = fields.DatetimeField(auto_now_add=True)
    score = fields.IntField(default=0)
    completed = fields.BooleanField(default=False)

class QuizResponse(Model):
    id = fields.IntField(pk=True)
    creator = fields.ForeignKeyField("models.User", related_name="responses")
    title = fields.CharField(max_length=64)
    description = fields.CharField(max_length=255)
    optional_context = fields.TextField(null=True)  # Optional context for the response
    participant = fields.ForeignKeyField("models.QuizParticipant", related_name="responses")
    question = fields.ForeignKeyField("models.Question", related_name="responses")
    answer = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        unique_together = (("participant", "question"),)  # Ensure one response per question per participant

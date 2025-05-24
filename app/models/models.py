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
    join_code = fields.CharField(max_length=10, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    questions: fields.ReverseRelation["Question"]
    participants: fields.ReverseRelation["QuizParticipant"]

class Question(Model):
    id = fields.IntField(pk=True)
    quiz = fields.ForeignKeyField("models.Quiz", related_name="questions")
    text = fields.TextField()
    type = fields.CharEnumField(AnswerType, default=AnswerType.TEXT)
    rubric = fields.CharField(max_length=100)  # can be list of rubrics or points
    created_at = fields.DatetimeField(auto_now_add=True)

class QuizParticipant(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="participants")
    quiz = fields.ForeignKeyField("models.Quiz", related_name="participants")
    status = fields.CharEnumField(StatusType)
    joined_at = fields.DatetimeField(auto_now_add=True)


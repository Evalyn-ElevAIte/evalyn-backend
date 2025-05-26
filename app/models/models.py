from tortoise import fields
from tortoise.models import Model
from app.utils.util import AnswerType, StatusType


# ! helper functions
# User model
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

# ! Quiz model, it can have many questions, many users (participants), but one creator
class Quiz(Model):
    id = fields.IntField(pk=True)
    creator = fields.ForeignKeyField("models.User", related_name="creator")
    title = fields.CharField(max_length=64)
    description = fields.CharField(max_length=255)
    # assignment_id = fields.CharField(max_length=255)  # Matches prompt_generator.py
    # student_id = fields.CharField(max_length=255)  # Matches prompt_generator.py
    lecturer_overall_notes = fields.TextField(null=True)
    join_code = fields.CharField(max_length=10, unique=True)
    completed = fields.BooleanField(default=False) # true = time is up
    start_time = fields.DatetimeField(null=True)
    end_time = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    questions: fields.ReverseRelation["Question"]
    participants: fields.ReverseRelation["QuizParticipant"]

# ! Question model, it belongs to one quiz, it can have many responses
class Question(Model):
    id = fields.IntField(pk=True)
    quiz = fields.ForeignKeyField("models.Quiz", related_name="questions")
    text = fields.TextField()
    type = fields.CharEnumField(AnswerType, default=AnswerType.TEXT)
    
    # optional if it is multiple choice
    options = fields.JSONField(null=True)  # list of strings for choices
    expected_answer = fields.JSONField(null=True)
    
    rubric = fields.CharField(max_length=100)
    rubric_max_score = fields.IntField(default=100)
    created_at = fields.DatetimeField(auto_now_add=True)

    responses: fields.ReverseRelation["QuestionResponse"]

# ! Participant model
class QuizParticipant(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="participants")
    quiz = fields.ForeignKeyField("models.Quiz", related_name="participants")
    status = fields.CharEnumField(StatusType)
    score = fields.IntField(default=0)
    joined_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("user", "quiz")

# ! Response model, basically an answer for a certain question in a certain quiz
class QuestionResponse(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="responden")
    question = fields.ForeignKeyField("models.Question", related_name="question")
    answer = fields.JSONField()
    
    joined_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("user", "question")

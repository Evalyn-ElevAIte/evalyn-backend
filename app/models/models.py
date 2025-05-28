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
    quizzes: fields.ReverseRelation["Quiz"]  # reverse relation
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
    completed = fields.BooleanField(default=False)  # true = time is up
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
    # rubric = fields.JSONField()
    rubric = fields.TextField()  # Matches prompt_generator.py
    rubric_max_score = fields.IntField(default=0)  # Matches prompt_generator.py
    created_at = fields.DatetimeField(auto_now_add=True)
    responses: fields.ReverseRelation["QuestionResponse"]


# ! Participant model
class QuizParticipant(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="participants")
    quiz = fields.ForeignKeyField("models.Quiz", related_name="quiz")
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

class Assessment(Model):
    """Main assessment model"""
    id = fields.IntField(pk=True)
    assessment_id = fields.CharField(max_length=255, unique=True, index=True)
    student_identifier = fields.CharField(max_length=100, index=True)
    assignment_identifier = fields.CharField(max_length=100, index=True)
    question_identifier = fields.CharField(max_length=100, null=True)
    submission_timestamp_utc = fields.DatetimeField(index=True)
    assessment_timestamp_utc = fields.DatetimeField(index=True)
    overall_score = fields.IntField(default=0)
    overall_max_score = fields.IntField(default=0)
    summary_of_performance = fields.TextField(null=True)
    general_positive_feedback = fields.TextField(null=True)
    general_areas_for_improvement = fields.TextField(null=True)
    overall_scoring_confidence = fields.DecimalField(max_digits=3, decimal_places=2, null=True)
    feedback_generation_confidence = fields.DecimalField(max_digits=3, decimal_places=2, null=True)
    model_used = fields.CharField(max_length=50, null=True)
    prompt_version = fields.CharField(max_length=100, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # Reverse foreign key relationships
    question_assessments: fields.ReverseRelation["QuestionAssessment"]
    suggested_resources: fields.ReverseRelation["SuggestedResource"]

    class Meta:
        table = "assessments"
        indexes = [
            ["student_identifier", "assignment_identifier"],
        ]

    def __str__(self):
        return f"Assessment {self.assessment_id} - Student {self.student_identifier}"


class QuestionAssessment(Model):
    """Question assessment model"""
    id = fields.IntField(pk=True)
    assessment = fields.ForeignKeyField("models.Assessment", related_name="question_assessments", on_delete=fields.CASCADE)
    question_id = fields.CharField(max_length=100)
    question_text = fields.TextField()
    student_answer_text = fields.TextField(null=True)
    lecturer_answer_text = fields.TextField(null=True)
    rubric = fields.TextField(null=True)
    rubric_max_score = fields.IntField(default=0)
    score = fields.IntField(default=0)
    max_score_possible = fields.IntField(default=0)
    overall_question_feedback = fields.TextField(null=True)
    # add AI plagiarism score
    created_at = fields.DatetimeField(auto_now_add=True)

    # Reverse foreign key relationships
    rubric_components: fields.ReverseRelation["RubricComponentFeedback"]
    key_points: fields.ReverseRelation["StudentKeyPoint"]
    missing_concepts: fields.ReverseRelation["MissingConcept"]

    class Meta:
        table = "question_assessments"
        indexes = [
            ["assessment_id", "question_id"],
        ]

    def __str__(self):
        return f"Question {self.question_id} - Assessment {self.assessment.assessment_id}"


class RubricComponentFeedback(Model):
    """Rubric component feedback model"""
    id = fields.IntField(pk=True)
    question_assessment = fields.ForeignKeyField("models.QuestionAssessment", related_name="rubric_components", on_delete=fields.CASCADE)
    component_description = fields.CharField(max_length=255)
    component_evaluation = fields.TextField(null=True)
    component_strengths = fields.TextField(null=True)
    component_areas_for_improvement = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "rubric_component_feedback"

    def __str__(self):
        return f"Rubric Component: {self.component_description}"


class StudentKeyPoint(Model):
    """Key points covered by student model"""
    id = fields.IntField(pk=True)
    question_assessment = fields.ForeignKeyField("models.QuestionAssessment", related_name="key_points", on_delete=fields.CASCADE)
    key_point = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "student_key_points"

    def __str__(self):
        return f"Key Point: {self.key_point[:50]}..."


class MissingConcept(Model):
    """Missing concepts in student answer model"""
    id = fields.IntField(pk=True)
    question_assessment = fields.ForeignKeyField("models.QuestionAssessment", related_name="missing_concepts", on_delete=fields.CASCADE)
    missing_concept = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "missing_concepts"

    def __str__(self):
        return f"Missing Concept: {self.missing_concept[:50]}..."


class SuggestedResource(Model):
    """Suggested next steps or resources model"""
    id = fields.IntField(pk=True)
    assessment = fields.ForeignKeyField("models.Assessment", related_name="suggested_resources", on_delete=fields.CASCADE)
    resource_description = fields.TextField()
    sequence_order = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "suggested_resources"
        ordering = ["sequence_order"]

    def __str__(self):
        return f"Resource: {self.resource_description[:50]}..."
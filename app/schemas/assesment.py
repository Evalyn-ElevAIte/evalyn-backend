from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal


# Input schemas for creating records
class RubricComponentCreate(BaseModel):
    component_description: str
    component_evaluation: Optional[str] = None
    component_strengths: Optional[str] = None
    component_areas_for_improvement: Optional[str] = None


class QuestionAssessmentCreate(BaseModel):
    question_id: int
    question_text: str
    student_answer_text: Optional[str] = None
    lecturer_answer_text: Optional[str] = None
    rubric: Optional[str] = None
    rubric_max_score: int = 0
    score: int = 0
    rating_plagiarism: Optional[int] = None
    max_score_possible: int = 0
    overall_question_feedback: Optional[str] = None
    rubric_component_feedback: List[RubricComponentCreate] = []
    key_points_covered_by_student: List[str] = []
    missing_concepts_in_student_answer: List[str] = []


class OverallAssessmentCreate(BaseModel):
    score: int = 0
    max_score_possible: int = 0
    summary_of_performance: Optional[str] = None
    general_positive_feedback: Optional[str] = None
    general_areas_for_improvement: Optional[str] = None


class AIConfidenceScores(BaseModel):
    overall_scoring_confidence: Optional[Decimal] = None
    feedback_generation_confidence: Optional[Decimal] = None


class ProcessingMetadata(BaseModel):
    model_used: Optional[str] = None
    prompt_version: Optional[str] = None


class AssessmentCreate(BaseModel):
    user_id: int
    quiz_id: int
    submission_timestamp_utc: datetime
    assessment_timestamp_utc: datetime
    overall_assessment: OverallAssessmentCreate
    question_assessments: List[QuestionAssessmentCreate] = []
    ai_confidence_scores: Optional[AIConfidenceScores] = None
    processing_metadata: Optional[ProcessingMetadata] = None


# Output schemas for reading records
class RubricComponentResponse(BaseModel):
    id: int
    component_description: str
    component_evaluation: Optional[str]
    component_strengths: Optional[str]
    component_areas_for_improvement: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class StudentKeyPointResponse(BaseModel):
    id: int
    key_point: str
    created_at: datetime

    class Config:
        from_attributes = True


class MissingConceptResponse(BaseModel):
    id: int
    missing_concept: str
    created_at: datetime

    class Config:
        from_attributes = True


class QuestionAssessmentResponse(BaseModel):
    id: int
    question_id: int
    question_text: str
    student_answer_text: Optional[str]
    lecturer_answer_text: Optional[str]
    rubric: Optional[str]
    rubric_max_score: int
    score: int
    max_score_possible: int
    overall_question_feedback: Optional[str]
    created_at: datetime
    rubric_components: List[RubricComponentResponse] = []
    key_points: List[StudentKeyPointResponse] = []
    missing_concepts: List[MissingConceptResponse] = []

    class Config:
        from_attributes = True


class AssessmentResponse(BaseModel):
    id: int # The actual primary key from the database
    user_id: int
    quiz_id: int
    submission_timestamp_utc: datetime
    assessment_timestamp_utc: datetime
    overall_score: int
    overall_max_score: int
    summary_of_performance: Optional[str]
    general_positive_feedback: Optional[str]
    general_areas_for_improvement: Optional[str]
    overall_scoring_confidence: Optional[Decimal]
    feedback_generation_confidence: Optional[Decimal]
    model_used: Optional[str]
    prompt_version: Optional[str]
    created_at: datetime
    updated_at: datetime
    question_assessments: List[QuestionAssessmentResponse] = []
    class Config:
        from_attributes = True


# Summary schemas for analytics
class AssessmentSummary(BaseModel):
    id: int # The actual primary key from the database
    user_id: int
    quiz_id: int
    overall_score: int
    overall_max_score: int
    score_percentage: float
    assessment_timestamp_utc: datetime

    class Config:
        from_attributes = True


class StudentPerformanceSummary(BaseModel):
    user_id: int
    total_assessments: int
    average_score: float
    average_max_score: float
    average_percentage: float
    latest_assessment_date: datetime


# Filter schemas for queries
class AssessmentFilter(BaseModel):
    user_id: Optional[int] = None
    quiz_id: Optional[int] = None
    min_score: Optional[int] = None
    max_score: Optional[int] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class StudentFilter(BaseModel):
    user_ids: Optional[List[int]] = None
    quiz_id: Optional[int] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None

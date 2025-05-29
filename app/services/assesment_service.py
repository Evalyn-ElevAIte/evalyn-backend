import json
from typing import List, Optional, Dict, Any
from tortoise.transactions import in_transaction
from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise.queryset import QuerySet
from datetime import datetime
import logging

# Import models and schemas (assuming they're in separate files)
from app.models.models import (
    Assessment,
    QuestionAssessment,
    RubricComponentFeedback,
    StudentKeyPoint,
    MissingConcept,
)
from app.schemas.assesment import (
    AssessmentCreate,
    AssessmentResponse,
    AssessmentSummary,
    StudentPerformanceSummary,
    AssessmentFilter,
    StudentFilter,
)

logger = logging.getLogger(__name__)


class AssessmentService:
    """Service class for handling assessment operations with Tortoise ORM"""

    @staticmethod
    async def create_assessment_from_json(
        assessment_json: str,
    ) -> Optional[AssessmentResponse]:
        """
        Create assessment from JSON string
        """
        try:
            # Parse JSON to dict first
            assessment_dict = json.loads(assessment_json)

            # Convert to Pydantic model for validation
            assessment_data = AssessmentCreate(**assessment_dict)

            return await AssessmentService.create_assessment(assessment_data)

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating assessment from JSON: {e}")
            return None

    @staticmethod
    async def create_assessment(
        assessment_data: AssessmentCreate,
    ) -> Optional[AssessmentResponse]:
        """
        Create a complete assessment with all related data
        """
        async with in_transaction() as conn:
            try:
                # Create main assessment
                assessment = await Assessment.create(
                    assessment_id=assessment_data.assessment_id,
                    student_identifier=assessment_data.student_id,
                    assignment_identifier=assessment_data.assignment_identifier,
                    question_identifier=assessment_data.question_identifier,
                    submission_timestamp_utc=assessment_data.submission_timestamp_utc,
                    assessment_timestamp_utc=assessment_data.assessment_timestamp_utc,
                    overall_score=assessment_data.overall_assessment.score,
                    overall_max_score=assessment_data.overall_assessment.max_score_possible,
                    summary_of_performance=assessment_data.overall_assessment.summary_of_performance,
                    general_positive_feedback=assessment_data.overall_assessment.general_positive_feedback,
                    general_areas_for_improvement=assessment_data.overall_assessment.general_areas_for_improvement,
                    overall_scoring_confidence=(
                        assessment_data.ai_confidence_scores.overall_scoring_confidence
                        if assessment_data.ai_confidence_scores
                        else None
                    ),
                    feedback_generation_confidence=(
                        assessment_data.ai_confidence_scores.feedback_generation_confidence
                        if assessment_data.ai_confidence_scores
                        else None
                    ),
                    model_used=(
                        assessment_data.processing_metadata.model_used
                        if assessment_data.processing_metadata
                        else None
                    ),
                    prompt_version=(
                        assessment_data.processing_metadata.prompt_version
                        if assessment_data.processing_metadata
                        else None
                    ),
                    using_db=conn,
                )

                # Create question assessments
                for question_data in assessment_data.question_assessments:
                    question_assessment = await QuestionAssessment.create(
                        assessment=assessment,
                        question_id=question_data.question_id,
                        question_text=question_data.question_text,
                        student_answer_text=question_data.student_answer_text,
                        lecturer_answer_text=question_data.lecturer_answer_text,
                        rubric=question_data.rubric,
                        rubric_max_score=question_data.rubric_max_score,
                        score=question_data.score,
                        max_score_possible=question_data.max_score_possible,
                        overall_question_feedback=question_data.overall_question_feedback,
                        using_db=conn,
                    )

                    # Create rubric components
                    for component_data in question_data.rubric_component_feedback:
                        await RubricComponentFeedback.create(
                            question_assessment=question_assessment,
                            component_description=component_data.component_description,
                            component_evaluation=component_data.component_evaluation,
                            component_strengths=component_data.component_strengths,
                            component_areas_for_improvement=component_data.component_areas_for_improvement,
                            using_db=conn,
                        )

                    # Create key points
                    for key_point in question_data.key_points_covered_by_student:
                        await StudentKeyPoint.create(
                            question_assessment=question_assessment,
                            key_point=key_point,
                            using_db=conn,
                        )

                    # Create missing concepts
                    for concept in question_data.missing_concepts_in_student_answer:
                        await MissingConcept.create(
                            question_assessment=question_assessment,
                            missing_concept=concept,
                            using_db=conn,
                        )

                

                # Return the created assessment with all relations
                return await AssessmentService.get_assessment_by_id(
                    assessment_data.assessment_id
                )

            except IntegrityError as e:
                logger.error(f"Integrity error creating assessment: {e}")
                return None
            except Exception as e:
                logger.error(f"Unexpected error creating assessment: {e}")
                return None

    @staticmethod
    async def get_assessment_by_id(assessment_id: str) -> Optional[AssessmentResponse]:
        """
        Get complete assessment by ID with all related data, supposed to be call by student_identifier / student_id
        """
        try:
            assessment = await Assessment.get(
                assessment_id=assessment_id
            ).prefetch_related(
                "question_assessments__rubric_components",
                "question_assessments__key_points",
                "question_assessments__missing_concepts",
                "suggested_resources",
            )

            return AssessmentResponse.from_orm(assessment)

        except DoesNotExist:
            logger.warning(f"Assessment with ID {assessment_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error retrieving assessment: {e}")
            return None

    @staticmethod
    async def get_assessments_by_filter(
        filter_params: AssessmentFilter,
    ) -> List[AssessmentResponse]:
        """
        Get assessments based on filter parameters
        """
        try:
            query = Assessment.all()

            # Apply filters
            if filter_params.student_identifier:
                query = query.filter(
                    student_identifier=filter_params.student_identifier
                )

            if filter_params.assignment_identifier:
                query = query.filter(
                    assignment_identifier=filter_params.assignment_identifier
                )

            if filter_params.min_score is not None:
                query = query.filter(overall_score__gte=filter_params.min_score)

            if filter_params.max_score is not None:
                query = query.filter(overall_score__lte=filter_params.max_score)

            if filter_params.from_date:
                query = query.filter(
                    assessment_timestamp_utc__gte=filter_params.from_date
                )

            if filter_params.to_date:
                query = query.filter(
                    assessment_timestamp_utc__lte=filter_params.to_date
                )

            # Apply pagination and prefetch relations
            assessments = (
                await query.offset(filter_params.offset)
                .limit(filter_params.limit)
                .prefetch_related(
                    "question_assessments__rubric_components",
                    "question_assessments__key_points",
                    "question_assessments__missing_concepts",
                    "suggested_resources",
                )
            )

            return [
                AssessmentResponse.from_orm(assessment) for assessment in assessments
            ]

        except Exception as e:
            logger.error(f"Error filtering assessments: {e}")
            return []

    @staticmethod
    async def get_student_assessments(
        student_id: str, limit: int = 10
    ) -> List[AssessmentSummary]:
        """
        Get recent assessments summary for a student
        """
        try:
            assessments = (
                await Assessment.filter(student_identifier=student_id)
                .order_by("-assessment_timestamp_utc")
                .limit(limit)
            )

            return [
                AssessmentSummary(
                    assessment_id=assessment.assessment_id,
                    student_identifier=assessment.student_identifier,
                    assignment_identifier=assessment.assignment_identifier,
                    overall_score=assessment.overall_score,
                    overall_max_score=assessment.overall_max_score,
                    score_percentage=round(
                        (
                            (
                                assessment.overall_score
                                / assessment.overall_max_score
                                * 100
                            )
                            if assessment.overall_max_score > 0
                            else 0
                        ),
                        2,
                    ),
                    assessment_timestamp_utc=assessment.assessment_timestamp_utc,
                )
                for assessment in assessments
            ]

        except Exception as e:
            logger.error(f"Error getting student assessments: {e}")
            return []

    @staticmethod
    async def get_student_performance_summary(
        student_filter: StudentFilter,
    ) -> List[StudentPerformanceSummary]:
        """
        Get performance summary for students
        """
        try:
            query = Assessment.all()

            # Apply filters
            if student_filter.student_identifiers:
                query = query.filter(
                    student_identifier__in=student_filter.student_ids
                )

            if student_filter.assignment_identifier:
                query = query.filter(
                    assignment_identifier=student_filter.assignment_identifier
                )

            if student_filter.from_date:
                query = query.filter(
                    assessment_timestamp_utc__gte=student_filter.from_date
                )

            if student_filter.to_date:
                query = query.filter(
                    assessment_timestamp_utc__lte=student_filter.to_date
                )

            # Group by student and calculate aggregates
            from tortoise.functions import Count, Avg, Max

            results = (
                await query.group_by("student_identifier")
                .annotate(
                    total_assessments=Count("id"),
                    average_score=Avg("overall_score"),
                    average_max_score=Avg("overall_max_score"),
                    latest_assessment_date=Max("assessment_timestamp_utc"),
                )
                .values(
                    "student_identifier",
                    "total_assessments",
                    "average_score",
                    "average_max_score",
                    "latest_assessment_date",
                )
            )

            return [
                StudentPerformanceSummary(
                    student_identifier=result["student_identifier"],
                    total_assessments=result["total_assessments"],
                    average_score=round(result["average_score"], 2),
                    average_max_score=round(result["average_max_score"], 2),
                    average_percentage=round(
                        (
                            (
                                result["average_score"]
                                / result["average_max_score"]
                                * 100
                            )
                            if result["average_max_score"] > 0
                            else 0
                        ),
                        2,
                    ),
                    latest_assessment_date=result["latest_assessment_date"],
                )
                for result in results
            ]

        except Exception as e:
            logger.error(f"Error getting student performance summary: {e}")
            return []

    @staticmethod
    async def update_assessment_score(assessment_id: str, new_score: int) -> bool:
        """
        Update overall score for an assessment
        """
        try:
            assessment = await Assessment.get(assessment_id=assessment_id)
            assessment.overall_score = new_score
            await assessment.save()
            return True

        except DoesNotExist:
            logger.warning(f"Assessment with ID {assessment_id} not found")
            return False
        except Exception as e:
            logger.error(f"Error updating assessment score: {e}")
            return False

    @staticmethod
    async def delete_assessment(assessment_id: str) -> bool:
        """
        Delete assessment and all related data
        """
        try:
            assessment = await Assessment.get(assessment_id=assessment_id)
            await assessment.delete()
            return True

        except DoesNotExist:
            logger.warning(f"Assessment with ID {assessment_id} not found")
            return False
        except Exception as e:
            logger.error(f"Error deleting assessment: {e}")
            return False

    @staticmethod
    async def get_assessment_statistics() -> Dict[str, Any]:
        """
        Get overall assessment statistics
        """
        try:
            from tortoise.functions import Count, Avg, Min, Max

            stats = (
                await Assessment.all()
                .annotate(
                    total_assessments=Count("id"),
                    average_score=Avg("overall_score"),
                    min_score=Min("overall_score"),
                    max_score=Max("overall_score"),
                    earliest_assessment=Min("assessment_timestamp_utc"),
                    latest_assessment=Max("assessment_timestamp_utc"),
                )
                .values(
                    "total_assessments",
                    "average_score",
                    "min_score",
                    "max_score",
                    "earliest_assessment",
                    "latest_assessment",
                )
            )

            if stats:
                return {
                    "total_assessments": stats[0]["total_assessments"],
                    "average_score": (
                        round(stats[0]["average_score"], 2)
                        if stats[0]["average_score"]
                        else 0
                    ),
                    "min_score": stats[0]["min_score"] or 0,
                    "max_score": stats[0]["max_score"] or 0,
                    "earliest_assessment": stats[0]["earliest_assessment"],
                    "latest_assessment": stats[0]["latest_assessment"],
                }
            else:
                return {
                    "total_assessments": 0,
                    "average_score": 0,
                    "min_score": 0,
                    "max_score": 0,
                    "earliest_assessment": None,
                    "latest_assessment": None,
                }

        except Exception as e:
            logger.error(f"Error getting assessment statistics: {e}")
            return {}

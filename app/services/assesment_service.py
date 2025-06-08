import json
from typing import List, Optional, Dict, Any
from tortoise.transactions import in_transaction
from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise.queryset import QuerySet
from datetime import datetime
import logging
from fastapi import HTTPException
from app.utils.util import check_ai_plagiarism, check_ai_with_sapling

# Import models and schemas (assuming they're in separate files)
from app.models.models import (
    Assessment,
    QuestionAssessment,
    RubricComponentFeedback,
    StudentKeyPoint,
    MissingConcept,
    User,  # Import User model
    Quiz,  # Import Quiz model
    QuizParticipant,
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
            assessment_dict = {}
            # Attempt to parse as JSON first
            try:
                assessment_dict = json.loads(assessment_json)
            except json.JSONDecodeError as json_error:
                # If JSON parsing fails, try parsing as a Python literal (dictionary string)
                try:
                    import ast
                    assessment_dict = ast.literal_eval(assessment_json)
                except (ValueError, SyntaxError) as ast_error:
                    # If both fail, try to fix common JSON issues (e.g., unescaped backslashes)
                    # This is a last resort, as it modifies the string for JSON parsing specifically
                    try:
                        assessment_dict = json.loads(assessment_json.replace('\\', '\\\\'))
                    except json.JSONDecodeError as final_json_error:
                        logger.error(f"Failed to parse assessment_json: Original JSON error: {json_error}, AST error: {ast_error}, Final JSON (escaped) error: {final_json_error}")
                        return None
            
            # Convert to Pydantic model for validation
            assessment_data = AssessmentCreate(**assessment_dict)

            return await AssessmentService.create_assessment(assessment_data)

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
                # Fetch User and Quiz objects
                user_obj = await User.get_or_none(id=assessment_data.user_id)
                if not user_obj:
                    raise DoesNotExist(
                        f"User with ID {assessment_data.user_id} not found"
                    )

                quiz_obj = await Quiz.get_or_none(id=assessment_data.quiz_id)
                if not quiz_obj:
                    raise DoesNotExist(
                        f"Quiz with ID {assessment_data.quiz_id} not found"
                    )

                # Create main assessment
                assessment = await Assessment.create(
                    user=user_obj,  # Use the fetched User object
                    quiz=quiz_obj,  # Use the fetched Quiz object
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
                    # == AI ANALYZER CHECK ==
                    print(
                        "==question_data.student_answer_text : ",
                        question_data.student_answer_text,
                    )
                    print(type(question_data.student_answer_text))

                    temp_student_answer_text = question_data.student_answer_text
                    string_student_answer_text = question_data.student_answer_text["text"] if isinstance(question_data.student_answer_text, dict) else question_data.student_answer_text

                    # Check if it's a string that needs parsing
                    if isinstance(temp_student_answer_text, str):
                        try:
                            # First try JSON parsing (for properly formatted JSON)
                            temp_student_answer_text = json.loads(
                                temp_student_answer_text
                            )
                            print("Successfully parsed JSON string")
                        except json.JSONDecodeError:
                            try:
                                # If JSON fails, try using ast.literal_eval for Python dict strings
                                import ast

                                temp_student_answer_text = ast.literal_eval(
                                    temp_student_answer_text
                                )
                                print("Successfully parsed Python dict string")
                            except (ValueError, SyntaxError):
                                # If both fail, wrap the string in a dict with "text" key
                                temp_student_answer_text = {
                                    "text": temp_student_answer_text
                                }
                                print("Wrapped plain text in JSON dict with 'text' key")
                    # If it's already a dict, no need to parse
                    elif isinstance(temp_student_answer_text, dict):
                        print("Already a dictionary, no parsing needed")

                    plagiarism_score_final = None  # Default value if not set by checks

                    # Now check if we have a dictionary with text content
                    if isinstance(temp_student_answer_text, dict):
                        if "text" in temp_student_answer_text:
                            text = temp_student_answer_text["text"]
                            plagiarism_score_result = await check_ai_with_sapling(text)
                            print(f"AI detector result: {plagiarism_score_result}")

                            # Append the AI detector score to the dictionary (rounded to 2 decimal places)
                            plagiarism_score_final = round(
                                plagiarism_score_result["score"], 2
                            )

                            print(f"AI detection score appended: {plagiarism_score_final}")
                        else:
                            print("No 'text' key found in dictionary")
                            plagiarism_score_final = None
                    else:
                        print("student_answer_text is not a dictionary")
                        plagiarism_score_final = None

                    print(f"Final AI detection score: {plagiarism_score_final}")
                    question_assessment = await QuestionAssessment.create(
                        assessment=assessment,
                        question_id=question_data.question_id,
                        question_text=question_data.question_text,
                        student_answer_text=string_student_answer_text,
                        lecturer_answer_text=question_data.lecturer_answer_text,
                        rubric=question_data.rubric,
                        rubric_max_score=question_data.rubric_max_score,
                        score=question_data.score,
                        rating_plagiarism=plagiarism_score_final,
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
                return await AssessmentService.get_assessment_by_id(assessment.id)

            except IntegrityError as e:
                logger.error(f"Integrity error creating assessment: {e}")
                raise HTTPException(status_code=400, detail=str(e))
            except DoesNotExist as e:
                logger.error(f"Related object not found: {e}")
                raise HTTPException(status_code=404, detail=str(e))
            except Exception as e:
                logger.error(f"Unexpected error creating assessment: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_assessment_by_id(id: int) -> Optional[AssessmentResponse]:
        """
        Get complete assessment by ID with all related data
        """
        try:
            assessment = await Assessment.get(id=id).prefetch_related(
                "question_assessments__rubric_components",
                "question_assessments__key_points",
                "question_assessments__missing_concepts",
            )

            return AssessmentResponse.from_orm(assessment)

        except DoesNotExist:
            logger.warning(f"Assessment with ID {id} not found")
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
            if filter_params.user_id:
                query = query.filter(user_id=filter_params.user_id)

            if filter_params.quiz_id:
                query = query.filter(quiz_id=filter_params.quiz_id)

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
        user_id: int, limit: int = 10
    ) -> List[AssessmentSummary]:
        """
        Get recent assessments summary for a student
        """
        try:
            assessments = (
                await Assessment.filter(user_id=user_id)
                .order_by("-assessment_timestamp_utc")
                .limit(limit)
            )

            return [
                AssessmentSummary(
                    id=assessment.id,
                    user_id=assessment.user_id,
                    quiz_id=assessment.quiz_id,
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
            if student_filter.user_ids:
                query = query.filter(user_id__in=student_filter.user_ids)

            if student_filter.quiz_id:
                query = query.filter(quiz_id=student_filter.quiz_id)

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
                await query.group_by("user_id")
                .annotate(
                    total_assessments=Count("id"),
                    average_score=Avg("overall_score"),
                    average_max_score=Avg("overall_max_score"),
                    latest_assessment_date=Max("assessment_timestamp_utc"),
                )
                .values(
                    "user_id",
                    "total_assessments",
                    "average_score",
                    "average_max_score",
                    "latest_assessment_date",
                )
            )

            return [
                StudentPerformanceSummary(
                    user_id=result["user_id"],
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
    async def update_assessment_score(id: int, new_score: int) -> bool:
        """
        Update overall score for an assessment
        """
        try:
            assessment = await Assessment.get(id=id)
            assessment.overall_score = new_score
            await assessment.save()
            return True

        except DoesNotExist:
            logger.warning(f"Assessment with ID {id} not found")
            return False
        except Exception as e:
            logger.error(f"Error updating assessment score: {e}")
            return False

    @staticmethod
    async def delete_assessment(id: int) -> bool:
        """
        Delete assessment and all related data
        """
        try:
            assessment = await Assessment.get(id=id)
            await assessment.delete()
            return True

        except DoesNotExist:
            logger.warning(f"Assessment with ID {id} not found")
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

    @staticmethod
    async def get_quiz_assessments_with_filters(
        quiz_id: int,
        student_name: Optional[str] = None,
        min_score: Optional[float] = None,
        max_score: Optional[float] = None,
        offset: int = 0,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        Get all assessments for a specific quiz with filtering options
        Returns assessments with student information and quiz details
        """
        try:
            # Get quiz information first
            quiz = await Quiz.get_or_none(id=quiz_id).select_related("creator")
            if not quiz:
                return {"quiz": None, "assessments": [], "error": "Quiz not found"}

            query = Assessment.filter(quiz_id=quiz_id).select_related("user")

            # Filter by student name if provided
            if student_name:
                # Assuming User model has 'name' or 'username' field
                # Adjust field name based on your User model structure
                query = query.filter(user__name__icontains=student_name)

            # Filter by score range
            if min_score is not None:
                query = query.filter(overall_score__gte=min_score)

            if max_score is not None:
                query = query.filter(overall_score__lte=max_score)

            # Apply pagination and order by assessment date
            assessments = (
                await query.order_by("-assessment_timestamp_utc")
                .offset(offset)
                .limit(limit)
            )

            # Format response with student information
            assessment_results = []
            for assessment in assessments:
                # Get participant status for this user and quiz
                participant = await QuizParticipant.get_or_none(
                    user_id=assessment.user_id, quiz_id=quiz_id
                )

                assessment_results.append(
                    {
                        "id": assessment.id,
                        "user_id": assessment.user_id,
                        "student_name": (
                            assessment.user.name
                            if hasattr(assessment.user, "name")
                            else assessment.user.username
                        ),
                        "student_email": getattr(assessment.user, "email", None),
                        "overall_score": assessment.overall_score,
                        "overall_max_score": assessment.overall_max_score,
                        "score_percentage": round(
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
                        "assessment_timestamp_utc": assessment.assessment_timestamp_utc,
                        "submission_timestamp_utc": assessment.submission_timestamp_utc,
                        "summary_of_performance": assessment.summary_of_performance,
                        "general_positive_feedback": assessment.general_positive_feedback,
                        "general_areas_for_improvement": assessment.general_areas_for_improvement,
                        "participant_status": (
                            participant.status if participant else None
                        ),
                    }
                )

            # Prepare quiz information
            quiz_info = {
                "id": quiz.id,
                "title": quiz.title,
                "description": quiz.description,
                "creator_name": (
                    quiz.creator.name
                    if hasattr(quiz.creator, "name")
                    else quiz.creator.username
                ),
                "join_code": quiz.join_code,
                "completed": quiz.completed,
                "start_time": quiz.start_time,
                "end_time": quiz.end_time,
                "created_at": quiz.created_at,
            }

            return {"quiz": quiz_info, "assessments": assessment_results}

        except Exception as e:
            logger.error(f"Error getting quiz assessments: {e}")
            return {"quiz": None, "assessments": [], "error": str(e)}

    @staticmethod
    async def get_quiz_statistics(quiz_id: int) -> Dict[str, Any]:
        """
        Get comprehensive statistics for a specific quiz
        """
        try:
            from tortoise.functions import Count, Avg, Min, Max, Sum

            # Get basic statistics
            stats = (
                await Assessment.filter(quiz_id=quiz_id)
                .annotate(
                    total_assessments=Count("id"),
                    average_score=Avg("overall_score"),
                    min_score=Min("overall_score"),
                    max_score=Max("overall_score"),
                    average_max_score=Avg("overall_max_score"),
                    earliest_assessment=Min("assessment_timestamp_utc"),
                    latest_assessment=Max("assessment_timestamp_utc"),
                )
                .values(
                    "total_assessments",
                    "average_score",
                    "min_score",
                    "max_score",
                    "average_max_score",
                    "earliest_assessment",
                    "latest_assessment",
                )
            )

            # Get score distribution (grade ranges)
            assessments = await Assessment.filter(quiz_id=quiz_id).values(
                "overall_score", "overall_max_score"
            )

            grade_distribution = {
                "A (90-100%)": 0,
                "B (80-89%)": 0,
                "C (70-79%)": 0,
                "D (60-69%)": 0,
                "F (0-59%)": 0,
            }

            for assessment in assessments:
                if assessment["overall_max_score"] > 0:
                    percentage = (
                        assessment["overall_score"] / assessment["overall_max_score"]
                    ) * 100
                    if percentage >= 90:
                        grade_distribution["A (90-100%)"] += 1
                    elif percentage >= 80:
                        grade_distribution["B (80-89%)"] += 1
                    elif percentage >= 70:
                        grade_distribution["C (70-79%)"] += 1
                    elif percentage >= 60:
                        grade_distribution["D (60-69%)"] += 1
                    else:
                        grade_distribution["F (0-59%)"] += 1

            # Get top and bottom performers
            top_performers = (
                await Assessment.filter(quiz_id=quiz_id)
                .select_related("user")
                .order_by("-overall_score")
                .limit(5)
            )
            bottom_performers = (
                await Assessment.filter(quiz_id=quiz_id)
                .select_related("user")
                .order_by("overall_score")
                .limit(5)
            )

            if stats:
                result = {
                    "quiz_id": quiz_id,
                    "total_assessments": stats[0]["total_assessments"],
                    "average_score": (
                        round(stats[0]["average_score"], 2)
                        if stats[0]["average_score"]
                        else 0
                    ),
                    "average_percentage": (
                        round(
                            (
                                stats[0]["average_score"]
                                / stats[0]["average_max_score"]
                                * 100
                            ),
                            2,
                        )
                        if stats[0]["average_score"] and stats[0]["average_max_score"]
                        else 0
                    ),
                    "min_score": stats[0]["min_score"] or 0,
                    "max_score": stats[0]["max_score"] or 0,
                    "earliest_assessment": stats[0]["earliest_assessment"],
                    "latest_assessment": stats[0]["latest_assessment"],
                    "grade_distribution": grade_distribution,
                    "top_performers": [
                        {
                            "student_name": (
                                performer.user.name
                                if hasattr(performer.user, "name")
                                else performer.user.username
                            ),
                            "score": performer.overall_score,
                            "max_score": performer.overall_max_score,
                            "percentage": (
                                round(
                                    (
                                        performer.overall_score
                                        / performer.overall_max_score
                                        * 100
                                    ),
                                    2,
                                )
                                if performer.overall_max_score > 0
                                else 0
                            ),
                        }
                        for performer in top_performers
                    ],
                    "bottom_performers": [
                        {
                            "student_name": (
                                performer.user.name
                                if hasattr(performer.user, "name")
                                else performer.user.username
                            ),
                            "score": performer.overall_score,
                            "max_score": performer.overall_max_score,
                            "percentage": (
                                round(
                                    (
                                        performer.overall_score
                                        / performer.overall_max_score
                                        * 100
                                    ),
                                    2,
                                )
                                if performer.overall_max_score > 0
                                else 0
                            ),
                        }
                        for performer in bottom_performers
                    ],
                }
            else:
                result = {
                    "quiz_id": quiz_id,
                    "total_assessments": 0,
                    "average_score": 0,
                    "average_percentage": 0,
                    "min_score": 0,
                    "max_score": 0,
                    "earliest_assessment": None,
                    "latest_assessment": None,
                    "grade_distribution": grade_distribution,
                    "top_performers": [],
                    "bottom_performers": [],
                }

            return result

        except Exception as e:
            logger.error(f"Error getting quiz statistics: {e}")
            return {}

    @staticmethod
    async def get_all_students_assessments(
        quiz_id: int,
        student_name: Optional[str] = None,
        min_score: Optional[float] = None,
        max_score: Optional[float] = None,
        status: Optional[str] = None,
        offset: int = 0,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        Get all students' assessments for a specific quiz (TEACHER VIEW)
        Shows scores for all students in one quiz
        """
        try:
            # Get quiz information first
            quiz = await Quiz.get_or_none(id=quiz_id).select_related("creator")
            if not quiz:
                return {"quiz": None, "assessments": [], "error": "Quiz not found"}

            # Get quiz participants to check status
            participants_query = QuizParticipant.filter(quiz_id=quiz_id).select_related(
                "user"
            )

            # Filter by student name if provided
            if student_name:
                participants_query = participants_query.filter(
                    user__name__icontains=student_name
                )

            # Filter by status if provided
            if status:
                participants_query = participants_query.filter(status=status)

            participants = await participants_query

            # Get assessments for these participants
            user_ids = [p.user_id for p in participants]
            assessment_query = Assessment.filter(
                quiz_id=quiz_id, user_id__in=user_ids
            ).select_related("user")

            # Apply score filters
            if min_score is not None:
                assessment_query = assessment_query.filter(overall_score__gte=min_score)
            if max_score is not None:
                assessment_query = assessment_query.filter(overall_score__lte=max_score)

            # Get assessments with pagination
            assessments = (
                await assessment_query.order_by("-assessment_timestamp_utc")
                .offset(offset)
                .limit(limit)
            )

            # Create a mapping of participants for quick lookup
            participant_map = {p.user_id: p for p in participants}

            # Format response
            assessment_results = []
            for assessment in assessments:
                participant = participant_map.get(assessment.user_id)

                assessment_results.append(
                    {
                        "assessment_id": assessment.id,
                        "user_id": assessment.user_id,
                        "student_name": (
                            assessment.user.name
                            if hasattr(assessment.user, "name")
                            else assessment.user.username
                        ),
                        "student_email": getattr(assessment.user, "email", None),
                        "overall_score": assessment.overall_score,
                        "overall_max_score": assessment.overall_max_score,
                        "score_percentage": round(
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
                        "status": participant.status if participant else "unknown",
                        "assessment_timestamp_utc": assessment.assessment_timestamp_utc,
                        "submission_timestamp_utc": assessment.submission_timestamp_utc,
                        "summary_of_performance": assessment.summary_of_performance,
                        "general_positive_feedback": assessment.general_positive_feedback,
                        "general_areas_for_improvement": assessment.general_areas_for_improvement,
                        "can_be_graded": (
                            participant.status == "submited" if participant else False
                        ),
                    }
                )

            # Also include participants who haven't submitted yet
            assessed_user_ids = {a.user_id for a in assessments}
            print(assessed_user_ids)
            for participant in participants:
                if participant.user_id not in assessed_user_ids:
                    assessment_results.append(
                        {
                            "id": None,
                            "user_id": participant.user_id,
                            "student_name": (
                                participant.user.name
                                if hasattr(participant.user, "name")
                                else participant.user.username
                            ),
                            "student_email": getattr(participant.user, "email", None),
                            "overall_score": None,
                            "overall_max_score": None,
                            "score_percentage": None,
                            "status": participant.status,
                            "assessment_timestamp_utc": None,
                            "submission_timestamp_utc": None,
                            "summary_of_performance": None,
                            "general_positive_feedback": None,
                            "general_areas_for_improvement": None,
                            "can_be_graded": False,
                        }
                    )

            # Prepare quiz information
            quiz_info = {
                "id": quiz.id,
                "title": quiz.title,
                "description": quiz.description,
                "creator_name": (
                    quiz.creator.name
                    if hasattr(quiz.creator, "name")
                    else quiz.creator.username
                ),
                "join_code": quiz.join_code,
                "completed": quiz.completed,
                "start_time": quiz.start_time,
                "end_time": quiz.end_time,
                "created_at": quiz.created_at,
            }

            return {
                "quiz": quiz_info,
                "assessments": assessment_results,
                "pagination": {
                    "offset": offset,
                    "limit": limit,
                    "total_returned": len(assessment_results),
                },
                "filters_applied": {
                    "student_name": student_name,
                    "min_score": min_score,
                    "max_score": max_score,
                    "status": status,
                },
            }

        except Exception as e:
            logger.error(f"Error getting all students assessments: {e}")
            return {"quiz": None, "assessments": [], "error": str(e)}

    @staticmethod
    async def update_assessment_grading(
        assessment_id: int,
        question_scores: List[
            Dict[str, Any]
        ],  # [{"question_id": int, "new_score": float}]
    ) -> Optional[Dict[str, Any]]:
        """
        Update assessment grading by teacher
        Updates individual question scores and recalculates overall score
        Changes status from "submited" to "graded"
        """
        async with in_transaction() as conn:
            try:
                # Get the assessment with all question assessments
                assessment = await Assessment.get(id=assessment_id).prefetch_related(
                    "question_assessments"
                )

                if not assessment:
                    return None

                # Update individual question scores
                total_score = 0
                total_max_score = 0

                for score_update in question_scores:
                    question_id = score_update.question_id
                    new_score = score_update.new_score

                    # Find and update the specific question assessment
                    question_assessment = await QuestionAssessment.get_or_none(
                        assessment_id=assessment_id, question_id=question_id
                    )

                    if question_assessment:
                        question_assessment.score = new_score
                        await question_assessment.save(using_db=conn)

                        total_score += new_score
                        total_max_score += question_assessment.max_score_possible

                # Update overall assessment score
                assessment.overall_score = total_score
                assessment.overall_max_score = total_max_score
                await assessment.save(using_db=conn)

                # Update participant status to "graded"
                participant = await QuizParticipant.get_or_none(
                    user_id=assessment.user_id, quiz_id=assessment.quiz_id
                )

                if participant:
                    participant.status = "graded"
                    await participant.save(using_db=conn)

                # Calculate new percentage
                print(total_score, total_max_score)
                new_percentage = round(
                    (total_score / total_max_score * 100) if total_max_score > 0 else 0,
                    2,
                )

                return {
                    "new_overall_score": total_score,
                    "new_score_percentage": new_percentage,
                    "updated_questions": len(question_scores),
                }

            except Exception as e:
                logger.error(f"Error updating assessment grading: {e}")
                raise e

    @staticmethod
    async def get_student_own_assessments(
        user_id: int,
        quiz_id: Optional[int] = None,
        status: Optional[str] = None,
        offset: int = 0,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        Get student's own assessments (STUDENT VIEW)
        Student can only see their own assessments when status is "graded"
        """
        try:
            # Get participant records for this student
            participants_query = QuizParticipant.filter(user_id=user_id).select_related(
                "quiz"
            )

            # Filter by quiz if specified
            if quiz_id:
                participants_query = participants_query.filter(quiz_id=quiz_id)

            # Filter by status if specified
            if status:
                participants_query = participants_query.filter(status=status)
            else:
                # By default, only show graded assessments to students
                participants_query = participants_query.filter(status="graded")

            participants = await participants_query

            # Get assessments for graded quizzes
            quiz_ids = [p.quiz_id for p in participants if p.status == "graded"]

            if not quiz_ids:
                return {
                    "assessments": [],
                    "pagination": {
                        "offset": offset,
                        "limit": limit,
                        "total_returned": 0,
                    },
                    "message": "No graded assessments available yet",
                }

            # Get assessments
            assessment_query = (
                Assessment.filter(user_id=user_id, quiz_id__in=quiz_ids)
                .select_related("quiz")
                .prefetch_related(
                    "question_assessments__rubric_components",
                    "question_assessments__key_points",
                    "question_assessments__missing_concepts",
                )
            )

            assessments = (
                await assessment_query.order_by("-assessment_timestamp_utc")
                .offset(offset)
                .limit(limit)
            )

            # Create participant mapping for status lookup
            participant_map = {p.quiz_id: p for p in participants}

            # Format response
            assessment_results = []
            for assessment in assessments:
                participant = participant_map.get(assessment.quiz_id)

                # Only include if status is graded
                if participant and participant.status == "graded":
                    assessment_results.append(
                        {
                            "id": assessment.id,
                            "quiz_id": assessment.quiz_id,
                            "quiz_title": assessment.quiz.title,
                            "quiz_description": assessment.quiz.description,
                            "overall_score": assessment.overall_score,
                            "overall_max_score": assessment.overall_max_score,
                            "score_percentage": round(
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
                            "assessment_timestamp_utc": assessment.assessment_timestamp_utc,
                            "submission_timestamp_utc": assessment.submission_timestamp_utc,
                            "summary_of_performance": assessment.summary_of_performance,
                            "general_positive_feedback": assessment.general_positive_feedback,
                            "general_areas_for_improvement": assessment.general_areas_for_improvement,
                            "status": participant.status,
                            "question_assessments": [
                                {
                                    "question_id": qa.question_id,
                                    "question_text": qa.question_text,
                                    "student_answer": qa.student_answer_text,
                                    "score": qa.score,
                                    "max_score_possible": qa.max_score_possible,
                                    "score_percentage": round(
                                        (
                                            (qa.score / qa.max_score_possible * 100)
                                            if qa.max_score_possible > 0
                                            else 0
                                        ),
                                        2,
                                    ),
                                    "overall_question_feedback": qa.overall_question_feedback,
                                    "rating_plagiarism": qa.rating_plagiarism,
                                }
                                for qa in assessment.question_assessments
                            ],
                        }
                    )

            return {
                "assessments": assessment_results,
                "pagination": {
                    "offset": offset,
                    "limit": limit,
                    "total_returned": len(assessment_results),
                },
                "filters_applied": {
                    "quiz_id": quiz_id,
                    "status": status or "graded",
                },
            }

        except Exception as e:
            logger.error(f"Error getting student own assessments: {e}")
            return {"assessments": [], "error": str(e)}

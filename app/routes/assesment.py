from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from app.services.assesment_service import AssessmentService
from app.schemas.assesment import (
    AssessmentResponse,
    AssessmentSummary,
    StudentPerformanceSummary,
    AssessmentFilter,
    StudentFilter,
)

router = APIRouter()

# Pydantic models for request bodies
class QuestionScoreUpdate(BaseModel):
    question_id: int
    new_score: int

class AssessmentGradingUpdate(BaseModel):
    question_scores: List[QuestionScoreUpdate]


@router.get("/{id}", response_model=Optional[AssessmentResponse])
async def get_assessment(id: int, quiz_id: Optional[int] = None):
    """
    Get assessment by ID

    Args:
        id: Assessment ID
        quiz_id: Optional quiz ID to verify assessment belongs to specified quiz
    """
    result = await AssessmentService.get_assessment_by_id(id)
    if not result:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return result


@router.get("/", response_model=List[AssessmentResponse])
async def get_assessments(
    quiz_id: int,
    user_id: Optional[int] = None,
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    offset: int = 0,
    limit: int = 10,
):
    """
    Get filtered assessments with pagination
    this is use for FILTER (PENCARIAN WAK)
    """
    filter_params = AssessmentFilter(
        user_id=user_id,
        quiz_id=quiz_id,
        min_score=min_score,
        max_score=max_score,
        from_date=from_date,
        to_date=to_date,
        offset=offset,
        limit=limit,
    )
    return await AssessmentService.get_assessments_by_filter(filter_params)


# 1. GET ALL STUDENTS ASSESSMENTS (FOR TEACHERS)
@router.get("/quiz/{quiz_id}/all-students")
async def get_all_students_assessments(
    quiz_id: int,
    student_name: Optional[str] = Query(None, description="Filter by student name"),
    min_score: Optional[float] = Query(None, description="Minimum score filter"),
    max_score: Optional[float] = Query(None, description="Maximum score filter"),
    status: Optional[str] = Query(None, description="Filter by status"),
    offset: int = Query(0, description="Pagination offset"),
    limit: int = Query(10, description="Number of results per page"),
) -> Dict[str, Any]:
    """
    Get all students' assessments for a specific quiz (TEACHER VIEW)
    Shows scores for all students in one quiz
    
    Args:
        quiz_id: Quiz ID to get assessments for
        student_name: Optional student name filter
        min_score: Optional minimum score filter
        max_score: Optional maximum score filter
        status: Optional status filter (submited, graded, etc.)
        offset: Pagination offset
        limit: Number of results per page
    """
    try:
        result = await AssessmentService.get_all_students_assessments(
            quiz_id=quiz_id,
            student_name=student_name,
            min_score=min_score,
            max_score=max_score,
            status=status,
            offset=offset,
            limit=limit,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving students assessments: {str(e)}"
        )

# 2. UPDATE STUDENT ASSESSMENT (TEACHER GRADING)
@router.patch("/{assessment_id}/grade")
async def update_assessment_grading(
    assessment_id: int,
    grading_data: AssessmentGradingUpdate
) -> Dict[str, Any]:
    """
    Update assessment grading by teacher
    Updates individual question scores and recalculates overall score
    Changes status from "submited" to "graded"
    
    Args:
        assessment_id: Assessment ID to update
        grading_data: List of question score updates
    """
    try:
        result = await AssessmentService.update_assessment_grading(
            assessment_id=assessment_id,
            question_scores=grading_data.question_scores
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        return {
            "message": "Assessment graded successfully",
            "assessment_id": assessment_id,
            "updated_scores": grading_data.question_scores,
            "new_overall_score": result.get("new_overall_score"),
            "new_score_percentage": result.get("new_score_percentage"),
            "status": "graded"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating assessment grading: {str(e)}"
        )


# 3. GET STUDENT'S OWN ASSESSMENTS (STUDENT VIEW)
@router.get("/student/my-assessments")
async def get_my_assessments(
    user_id: int,  # This should come from current_user authorization
    quiz_id: Optional[int] = Query(None, description="Filter by specific quiz"),
    status: Optional[str] = Query(None, description="Filter by status"),
    offset: int = Query(0, description="Pagination offset"),
    limit: int = Query(10, description="Number of results per page"),
) -> Dict[str, Any]:
    """
    Get student's own assessments (STUDENT VIEW)
    Student can only see their own assessments when status is "graded"
    
    Args:
        user_id: Student's user ID (from authorization)
        quiz_id: Optional quiz ID filter
        status: Optional status filter
        offset: Pagination offset
        limit: Number of results per page
    """
    try:
        result = await AssessmentService.get_student_own_assessments(
            user_id=user_id,
            quiz_id=quiz_id,
            status=status,
            offset=offset,
            limit=limit,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving student assessments: {str(e)}"
        )


@router.get("/quiz/{user_id}", response_model=List[AssessmentSummary])
async def get_student_recent_assessments(user_id: int, quiz_id: int, limit: int = 10):
    """
    Get recent assessments for a student in a specific quiz

    Args:
        user_id: Student ID
        quiz_id: Quiz ID to filter by
        limit: Maximum number of assessments to return
    """
    return await AssessmentService.get_student_assessments(user_id, quiz_id, limit)


@router.get("/students/performance", response_model=List[StudentPerformanceSummary])
async def get_students_performance(
    user_ids: Optional[List[int]] = Query(None),
    quiz_id: Optional[int] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
):
    """
    Get performance summary for students
    """
    filter_params = StudentFilter(
        user_ids=user_ids, quiz_id=quiz_id, from_date=from_date, to_date=to_date
    )
    return await AssessmentService.get_student_performance_summary(filter_params)


@router.patch("/{id}/score", status_code=204)
async def update_assessment_score(id: int, new_score: float):
    """
    Update assessment score
    """
    success = await AssessmentService.update_assessment_score(id, new_score)
    if not success:
        raise HTTPException(status_code=404, detail="Assessment not found")


@router.delete("/{id}", status_code=204)
async def delete_assessment(id: int):
    """
    Delete assessment
    """
    success = await AssessmentService.delete_assessment(id)
    if not success:
        raise HTTPException(status_code=404, detail="Assessment not found")


@router.get("/statistics/overview")
async def get_assessment_statistics(quiz_id: Optional[int] = None):
    """
    Get assessment statistics

    Args:
        quiz_id: Optional quiz ID to filter statistics by
    """
    return await AssessmentService.get_assessment_statistics(quiz_id)

# FOR BACKWARD COMPATIBILITY - Keep existing endpoint
@router.get("/quiz/{quiz_id}/assessments")
async def get_quiz_assessments(
    quiz_id: int,
    student_name: Optional[str] = Query(
        None, description="Filter by student name (partial match)"
    ),
    min_score: Optional[float] = Query(None, description="Minimum score filter"),
    max_score: Optional[float] = Query(None, description="Maximum score filter"),
    offset: int = Query(0, description="Pagination offset"),
    limit: int = Query(10, description="Number of results per page"),
) -> Dict[str, Any]:
    """
    Get all assessments for a specific quiz with filtering options
    
    Ini buat dapetin penilaian 1 kuis yang mencakup pengerjaan seluruh siswa

    Args:
        quiz_id: Quiz ID to get assessments for
        student_name: Optional student name filter (case-insensitive partial match)
        min_score: Optional minimum score filter
        max_score: Optional maximum score filter
        offset: Pagination offset
        limit: Number of results per page

    Returns:
        Dictionary containing assessments list and metadata
    """
    try:
        assessments = await AssessmentService.get_quiz_assessments_with_filters(
            quiz_id=quiz_id,
            student_name=student_name,
            min_score=min_score,
            max_score=max_score,
            offset=offset,
            limit=limit,
        )

        return {
            "quiz_id": quiz_id,
            "assessments": assessments,
            "pagination": {
                "offset": offset,
                "limit": limit,
                "total_returned": len(assessments),
            },
            "filters_applied": {
                "student_name": student_name,
                "min_score": min_score,
                "max_score": max_score,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving quiz assessments: {str(e)}"
        )


# FIXED: Add missing route path
@router.get("/quiz/{quiz_id}/statistics")
async def get_quiz_statistics(quiz_id: int) -> Dict[str, Any]:
    """
    Get comprehensive statistics for a specific quiz

    Args:
        quiz_id: Quiz ID to get statistics for

    Returns:
        Dictionary containing various statistics including:
        - Total assessments
        - Average scores and percentages
        - Score distribution by grade
        - Top and bottom performers
        - Date range of assessments
    """
    try:
        statistics = await AssessmentService.get_quiz_statistics(quiz_id)
        if not statistics:
            raise HTTPException(
                status_code=404, detail="No assessments found for this quiz"
            )
        return statistics
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving quiz statistics: {str(e)}"
        )

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.services.assesment_service import AssessmentService
from app.schemas.assesment import (
    AssessmentResponse,
    AssessmentSummary,
    StudentPerformanceSummary,
    AssessmentFilter,
    StudentFilter,
)

router = APIRouter()


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


# Untuk halaman yang menunjukkan keseluruhan pengerjaan siswa / View Submission Page
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


@router.get("           ")
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


@router.get("/students/{user_id}/recent", response_model=List[AssessmentSummary])
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

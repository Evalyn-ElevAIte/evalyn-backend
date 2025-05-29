from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from app.services.assesment_service import AssessmentService
from app.schemas.assesment import (
    AssessmentResponse,
    AssessmentSummary,
    StudentPerformanceSummary,
    AssessmentFilter,
    StudentFilter
)

router = APIRouter()


@router.get("/{id}", response_model=Optional[AssessmentResponse])
async def get_assessment(id: int):
    """
    Get assessment by ID
    """
    result = await AssessmentService.get_assessment_by_id(id)
    if not result:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return result

@router.get("/", response_model=List[AssessmentResponse])
async def get_assessments(
    user_id: Optional[int] = None,
    quiz_id: Optional[int] = None,
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    offset: int = 0,
    limit: int = 10
):
    """
    Get filtered assessments with pagination
    """
    filter_params = AssessmentFilter(
        user_id=user_id,
        quiz_id=quiz_id,
        min_score=min_score,
        max_score=max_score,
        from_date=from_date,
        to_date=to_date,
        offset=offset,
        limit=limit
    )
    return await AssessmentService.get_assessments_by_filter(filter_params)

@router.get("/students/{user_id}/recent", response_model=List[AssessmentSummary])
async def get_student_recent_assessments(user_id: int, limit: int = 10):
    """
    Get recent assessments for a student
    """
    return await AssessmentService.get_student_assessments(user_id, limit)

@router.get("/students/performance", response_model=List[StudentPerformanceSummary])
async def get_students_performance(
    user_ids: Optional[List[int]] = Query(None),
    quiz_id: Optional[int] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None
):
    """
    Get performance summary for students
    """
    filter_params = StudentFilter(
        user_ids=user_ids,
        quiz_id=quiz_id,
        from_date=from_date,
        to_date=to_date
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
async def get_assessment_statistics():
    """
    Get assessment statistics
    """
    return await AssessmentService.get_assessment_statistics()

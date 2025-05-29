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


@router.get("/{assessment_id}", response_model=Optional[AssessmentResponse])
async def get_assessment(assessment_id: str):
    """
    Get assessment by ID
    """
    result = await AssessmentService.get_assessment_by_id(assessment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return result

@router.get("/", response_model=List[AssessmentResponse])
async def get_assessments(
    student_identifier: Optional[str] = None,
    assignment_identifier: Optional[str] = None,
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
        student_identifier=student_identifier,
        assignment_identifier=assignment_identifier,
        min_score=min_score,
        max_score=max_score,
        from_date=from_date,
        to_date=to_date,
        offset=offset,
        limit=limit
    )
    return await AssessmentService.get_assessments_by_filter(filter_params)

@router.get("/students/{student_id}/recent", response_model=List[AssessmentSummary])
async def get_student_recent_assessments(student_id: str, limit: int = 10):
    """
    Get recent assessments for a student
    """
    return await AssessmentService.get_student_assessments(student_id, limit)

@router.get("/students/performance", response_model=List[StudentPerformanceSummary])
async def get_students_performance(
    student_identifiers: Optional[List[str]] = Query(None),
    assignment_identifier: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None
):
    """
    Get performance summary for students
    """
    filter_params = StudentFilter(
        student_identifiers=student_identifiers,
        assignment_identifier=assignment_identifier,
        from_date=from_date,
        to_date=to_date
    )
    return await AssessmentService.get_student_performance_summary(filter_params)

@router.patch("/{assessment_id}/score", status_code=204)
async def update_assessment_score(assessment_id: str, new_score: float):
    """
    Update assessment score
    """
    success = await AssessmentService.update_assessment_score(assessment_id, new_score)
    if not success:
        raise HTTPException(status_code=404, detail="Assessment not found")

@router.delete("/{assessment_id}", status_code=204)
async def delete_assessment(assessment_id: str):
    """
    Delete assessment
    """
    success = await AssessmentService.delete_assessment(assessment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Assessment not found")

@router.get("/statistics/overview")
async def get_assessment_statistics():
    """
    Get assessment statistics
    """
    return await AssessmentService.get_assessment_statistics()
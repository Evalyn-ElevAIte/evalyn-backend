import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta
from app.main import app
from app.schemas.assesment import (
    AssessmentResponse,
    AssessmentSummary,
    StudentPerformanceSummary
)

client = TestClient(app)

@pytest.fixture
def mock_assessment_service():
    with patch("app.routes.assesment.AssessmentService") as mock:
        yield mock

def test_get_assessment_success(mock_assessment_service):
    # Setup mock
    mock_response = AssessmentResponse(
        assessment_id="test123",
        student_identifier="student1",
        assignment_identifier="assignment1",
        question_identifier="question1",
        submission_timestamp_utc=datetime.utcnow(),
        assessment_timestamp_utc=datetime.utcnow(),
        overall_score=85,
        overall_max_score=100,
        summary_of_performance="Good work",
        general_positive_feedback="Well done",
        general_areas_for_improvement="Could improve",
        question_assessments=[]
    )
    mock_assessment_service.get_assessment_by_id = AsyncMock(return_value=mock_response)

    # Test
    response = client.get("/assessments/test123")
    
    # Assert
    assert response.status_code == 200
    assert response.json()["assessment_id"] == "test123"
    mock_assessment_service.get_assessment_by_id.assert_called_once_with("test123")

def test_get_assessment_not_found(mock_assessment_service):
    # Setup mock
    mock_assessment_service.get_assessment_by_id = AsyncMock(return_value=None)

    # Test
    response = client.get("/assessments/nonexistent")
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Assessment not found"

def test_get_assessments_with_filters(mock_assessment_service):
    # Setup mock
    mock_response = [
        AssessmentResponse(
            assessment_id=f"test{i}",
            student_identifier="student1",
            assignment_identifier="assignment1",
            question_identifier=f"question{i}",
            submission_timestamp_utc=datetime.utcnow(),
            assessment_timestamp_utc=datetime.utcnow(),
            overall_score=80 + i,
            overall_max_score=100,
            summary_of_performance="Good",
            general_positive_feedback="Well done",
            general_areas_for_improvement="Improve",
            question_assessments=[]
        ) for i in range(3)
    ]
    mock_assessment_service.get_assessments_by_filter = AsyncMock(return_value=mock_response)

    # Test with filters
    params = {
        "student_identifier": "student1",
        "assignment_identifier": "assignment1",
        "min_score": 80,
        "max_score": 90,
        "from_date": (datetime.utcnow() - timedelta(days=7)).isoformat(),
        "to_date": datetime.utcnow().isoformat(),
        "offset": 0,
        "limit": 10
    }
    response = client.get("/assessments/", params=params)
    
    # Assert
    assert response.status_code == 200
    assert len(response.json()) == 3
    mock_assessment_service.get_assessments_by_filter.assert_called_once()

def test_get_student_recent_assessments(mock_assessment_service):
    # Setup mock
    mock_response = [
        AssessmentSummary(
            assessment_id=f"test{i}",
            student_identifier="student1",
            assignment_identifier="assignment1",
            overall_score=80 + i,
            overall_max_score=100,
            score_percentage=80 + i,
            assessment_timestamp_utc=datetime.utcnow()
        ) for i in range(3)
    ]
    mock_assessment_service.get_student_assessments = AsyncMock(return_value=mock_response)

    # Test
    response = client.get("/assessments/students/student1/recent?limit=3")
    
    # Assert
    assert response.status_code == 200
    assert len(response.json()) == 3
    mock_assessment_service.get_student_assessments.assert_called_once_with("student1", 3)

def test_get_students_performance(mock_assessment_service):
    # Setup mock
    mock_response = [
        StudentPerformanceSummary(
            student_identifier="student1",
            total_assessments=5,
            average_score=85.5,
            average_max_score=100,
            average_percentage=85.5,
            latest_assessment_date=datetime.utcnow()
        )
    ]
    mock_assessment_service.get_student_performance_summary = AsyncMock(return_value=mock_response)

    # Test
    params = {
        "student_identifiers": ["student1"],
        "assignment_identifier": "assignment1",
        "from_date": (datetime.utcnow() - timedelta(days=30)).isoformat(),
        "to_date": datetime.utcnow().isoformat()
    }
    response = client.get("/assessments/students/performance", params=params)
    
    # Assert
    assert response.status_code == 200
    assert len(response.json()) == 1
    mock_assessment_service.get_student_performance_summary.assert_called_once()

def test_update_assessment_score_success(mock_assessment_service):
    # Setup mock
    mock_assessment_service.update_assessment_score = AsyncMock(return_value=True)

    # Test
    response = client.patch(
        "/assessments/test123/score",
        json={"new_score": 90}
    )
    
    # Assert
    assert response.status_code == 204
    mock_assessment_service.update_assessment_score.assert_called_once_with("test123", 90)

def test_update_assessment_score_not_found(mock_assessment_service):
    # Setup mock
    mock_assessment_service.update_assessment_score = AsyncMock(return_value=False)

    # Test
    response = client.patch(
        "/assessments/nonexistent/score",
        json={"new_score": 90}
    )
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Assessment not found"

def test_delete_assessment_success(mock_assessment_service):
    # Setup mock
    mock_assessment_service.delete_assessment = AsyncMock(return_value=True)

    # Test
    response = client.delete("/assessments/test123")
    
    # Assert
    assert response.status_code == 204
    mock_assessment_service.delete_assessment.assert_called_once_with("test123")

def test_delete_assessment_not_found(mock_assessment_service):
    # Setup mock
    mock_assessment_service.delete_assessment = AsyncMock(return_value=False)

    # Test
    response = client.delete("/assessments/nonexistent")
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Assessment not found"

def test_get_assessment_statistics(mock_assessment_service):
    # Setup mock
    mock_response = {
        "total_assessments": 100,
        "average_score": 75.5,
        "min_score": 0,
        "max_score": 100,
        "earliest_assessment": (datetime.utcnow() - timedelta(days=365)).isoformat(),
        "latest_assessment": datetime.utcnow().isoformat()
    }
    mock_assessment_service.get_assessment_statistics = AsyncMock(return_value=mock_response)

    # Test
    response = client.get("/assessments/statistics/overview")
    
    # Assert
    assert response.status_code == 200
    assert response.json()["total_assessments"] == 100
    mock_assessment_service.get_assessment_statistics.assert_called_once()
"""
Integration tests for FastAPI backend service in api.py
"""

import pytest
from fastapi.testclient import TestClient
from api import app

@pytest.fixture(scope="module")
def api_client():
    with TestClient(app) as client:
        yield client

def test_fastapi_root_endpoint(api_client):
    """Verify root endpoint returns service info."""
    response = api_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "documentation" in data

def test_fastapi_health_endpoint(api_client):
    """Verify health endpoint reports healthy status and model loaded."""
    response = api_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert data["feature_count"] == 8

def test_fastapi_predict_valid_payload(api_client):
    """Verify predict endpoint successfully processes student payload."""
    payload = {
        "student_id": "EDU-TEST-101",
        "name": "Integration Student",
        "major": "Cyber Security",
        "grade_level": "Senior",
        "attendance_rate": 84.0,
        "gpa": 3.1,
        "assignment_completion_rate": 88.0,
        "midterm_score": 79.0,
        "study_hours_per_week": 14.0,
        "lms_engagement_score": 75.0,
        "participation_score": 72.0,
        "stress_level": 5,
        "tuition_status": "Paid"
    }
    response = api_client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_risk"] in ["High", "Medium", "Low"]
    assert "success_score" in data
    assert "placement_risk" in data
    assert isinstance(data["indicators"], list)
    assert isinstance(data["recommendations"], list)

def test_fastapi_predict_pydantic_validation(api_client):
    """Verify Pydantic input validation blocks out-of-range values with 422."""
    invalid_payload = {
        "attendance_rate": 150.0,  # Invalid: > 100
        "gpa": 5.0                 # Invalid: > 4.0
    }
    response = api_client.post("/predict", json=invalid_payload)
    assert response.status_code == 422

def test_fastapi_cohort_kpis_endpoint(api_client):
    """Verify /cohort/kpis returns valid aggregate statistics."""
    response = api_client.get("/cohort/kpis")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1200
    assert "high_risk_cnt" in data
    assert "avg_gpa" in data

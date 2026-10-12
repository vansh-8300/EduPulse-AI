"""
Unit tests for prescriptive recommendation engine in src/recommendations.py
"""

from src.recommendations import generate_recommendations
from src.model_utils import predict_placement_risk

def test_high_risk_emergency_recommendations(high_risk_student_dict):
    """Verify high-risk student receives high-priority advisor consultation and metric actions."""
    risk_pred = {"predicted_risk": "High"}
    recs = generate_recommendations(high_risk_student_dict, risk_pred)

    assert len(recs) >= 2
    # First recommendation should be Emergency Advisor Consultation
    assert recs[0]["category"] == "Emergency Intervention"
    assert "High Priority" in recs[0]["priority"]

    categories = [r["category"] for r in recs]
    assert "Attendance Recovery" in categories
    assert "Academic Tutoring" in categories
    assert "Wellness & Health" in categories
    assert "Financial Services" in categories

def test_low_risk_enrichment_recommendations():
    """Verify strong student with no risk indicators gets honors / leadership recommendation."""
    strong_student = {
        "student_id": "EDU-2026-STAR",
        "name": "Super Performer",
        "major": "Computer Science",
        "grade_level": "Freshman",
        "attendance_rate": 96.0,
        "gpa": 3.92,
        "assignment_completion_rate": 98.0,
        "midterm_score": 95.0,
        "study_hours_per_week": 22.0,
        "lms_engagement_score": 92.0,
        "stress_level": 2,
        "tuition_status": "Paid"
    }
    risk_pred = {"predicted_risk": "Low"}
    placement_pred = {"placement_risk": "Low", "placement_score": 95.0, "placement_reasons": []}

    recs = generate_recommendations(strong_student, risk_pred, placement_pred)
    assert len(recs) == 1
    assert recs[0]["category"] == "Enrichment"
    assert "Growth" in recs[0]["priority"]

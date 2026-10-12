"""
Shared Pytest Fixtures for EduPulse AI Test Suite
"""

import os
import sys
import pytest
import pandas as pd

# Add workspace root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data_loader import load_student_data
from src.model_utils import load_model

@pytest.fixture(scope="session")
def dataset():
    """Load the canonical 1,200 student dataset."""
    return load_student_data("data/students_1200.csv")

@pytest.fixture(scope="session")
def model_artifact():
    """Load the trained Random Forest model artifact."""
    return load_model("models/risk_model.pkl")

@pytest.fixture
def sample_student_dict():
    """Sample student dictionary with realistic metrics."""
    return {
        "student_id": "EDU-2026-TEST",
        "name": "Jordan Lee",
        "major": "Computer Science",
        "grade_level": "Junior",
        "attendance_rate": 88.5,
        "gpa": 3.42,
        "assignment_completion_rate": 92.0,
        "midterm_score": 85.0,
        "study_hours_per_week": 16.0,
        "lms_engagement_score": 80.0,
        "participation_score": 78.0,
        "stress_level": 4,
        "tuition_status": "Paid"
    }

@pytest.fixture
def high_risk_student_dict():
    """Sample high-risk student dictionary."""
    return {
        "student_id": "EDU-2026-HIGH",
        "name": "Taylor Swift",
        "major": "Data Science",
        "grade_level": "Sophomore",
        "attendance_rate": 55.0,
        "gpa": 1.95,
        "assignment_completion_rate": 50.0,
        "midterm_score": 45.0,
        "study_hours_per_week": 6.0,
        "lms_engagement_score": 38.0,
        "participation_score": 40.0,
        "stress_level": 9,
        "tuition_status": "Pending"
    }

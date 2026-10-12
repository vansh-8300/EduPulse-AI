"""
Unit tests for data loader and dataset integrity utilities in src/data_loader.py
"""

import pandas as pd
import pytest
from src.data_loader import load_student_data, get_filtered_students, get_cohort_kpis

def test_dataset_exists_and_loads(dataset):
    """Ensure the dataset loads and contains exactly 1,200 rows."""
    assert isinstance(dataset, pd.DataFrame)
    assert len(dataset) == 1200
    assert dataset.shape[1] == 14

def test_dataset_schema_and_types(dataset):
    """Verify expected columns exist with valid data types."""
    required_cols = [
        "student_id", "name", "grade_level", "major",
        "attendance_rate", "gpa", "assignment_completion_rate",
        "midterm_score", "study_hours_per_week", "lms_engagement_score",
        "participation_score", "stress_level", "tuition_status", "risk_level"
    ]
    for col in required_cols:
        assert col in dataset.columns, f"Missing required column: {col}"

    assert pd.api.types.is_numeric_dtype(dataset["attendance_rate"])
    assert pd.api.types.is_numeric_dtype(dataset["gpa"])
    assert pd.api.types.is_numeric_dtype(dataset["stress_level"])

def test_dataset_integrity_no_nulls_no_duplicates(dataset):
    """Verify zero null values and zero duplicate student records or IDs."""
    assert dataset.isnull().sum().sum() == 0, "Dataset contains unexpected nulls"
    assert dataset.duplicated().sum() == 0, "Dataset contains duplicate rows"
    assert dataset["student_id"].duplicated().sum() == 0, "Duplicate student IDs detected"

def test_filter_by_major_and_grade(dataset):
    """Verify filtering by major and grade level subsets properly."""
    filtered = get_filtered_students(dataset, major="Computer Science", grade_level="Junior")
    assert len(filtered) > 0
    assert (filtered["major"] == "Computer Science").all()
    assert (filtered["grade_level"] == "Junior").all()

def test_filter_by_risk_level(dataset):
    """Verify filtering by risk level."""
    high_risk = get_filtered_students(dataset, risk_level="High")
    assert len(high_risk) > 0
    assert (high_risk["risk_level"] == "High").all()

def test_filter_search_with_special_regex_characters(dataset):
    """Verify that regex special characters in search input do not crash search."""
    # Parentheses, brackets, question marks should be treated as literal strings
    res1 = get_filtered_students(dataset, search_query="(")
    assert isinstance(res1, pd.DataFrame)
    res2 = get_filtered_students(dataset, search_query="[")
    assert isinstance(res2, pd.DataFrame)
    res3 = get_filtered_students(dataset, search_query=".*+")
    assert isinstance(res3, pd.DataFrame)

def test_cohort_kpis_normal_and_empty(dataset):
    """Verify KPI computations on full cohort and on empty slices."""
    kpis = get_cohort_kpis(dataset)
    assert kpis["total"] == 1200
    assert 0 <= kpis["high_risk_pct"] <= 100
    assert 0 <= kpis["avg_gpa"] <= 4.0
    assert 0 <= kpis["avg_success_score"] <= 100

    # Test empty dataframe edge case
    empty_df = dataset.iloc[0:0]
    empty_kpis = get_cohort_kpis(empty_df)
    assert empty_kpis["total"] == 0
    assert empty_kpis["high_risk_cnt"] == 0
    assert empty_kpis["avg_success_score"] == 0

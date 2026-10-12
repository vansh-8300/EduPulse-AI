"""
Data Loader Utility for EduPulse AI
Provides dataset caching, filtering, and summary metrics.
"""

import os
import pandas as pd

DATA_PATH = "data/students_1200.csv"

def load_student_data(filepath=DATA_PATH):
    """Load student dataset from CSV."""
    if not os.path.exists(filepath):
        # Fallback if run directly before data generation
        from generate_data import main as generate_main
        generate_main()

    df = pd.read_csv(filepath)
    return df

def get_filtered_students(df, major=None, grade_level=None, risk_level=None, search_query=None):
    """Filter student dataframe based on selected dashboard controls."""
    filtered = df.copy()

    if major and major != "All Majors":
        filtered = filtered[filtered["major"] == major]

    if grade_level and grade_level != "All Grades":
        filtered = filtered[filtered["grade_level"] == grade_level]

    if risk_level and risk_level != "All Risk Levels":
        filtered = filtered[filtered["risk_level"] == risk_level]

    if search_query:
        query = search_query.strip().lower()
        filtered = filtered[
            filtered["name"].str.lower().str.contains(query, regex=False) |
            filtered["student_id"].str.lower().str.contains(query, regex=False)
        ]

    return filtered

def get_cohort_kpis(df):
    """Calculate key summary performance indicators for the cohort."""
    total_students = len(df)
    if total_students == 0:
        return {
            "total": 0, "high_risk_cnt": 0, "high_risk_pct": 0, "avg_gpa": 0,
            "avg_attendance": 0, "avg_assignment": 0, "avg_success_score": 0
        }


    high_risk_cnt = (df["risk_level"] == "High").sum()
    high_risk_pct = (high_risk_cnt / total_students) * 100

    avg_gpa = df["gpa"].mean()
    avg_attendance = df["attendance_rate"].mean()
    avg_assignment = df["assignment_completion_rate"].mean()

    # Calculate cohort average Student Success Score (0-100)
    success_scores = (
        df["attendance_rate"] * 0.25 +
        (df["gpa"] / 4.0 * 100) * 0.25 +
        df["assignment_completion_rate"] * 0.20 +
        df["midterm_score"] * 0.15 +
        (10 - df["stress_level"]) * 10 * 0.15
    )
    avg_success = round(success_scores.mean(), 1)

    return {
        "total": total_students,
        "high_risk_cnt": int(high_risk_cnt),
        "high_risk_pct": round(high_risk_pct, 1),
        "avg_gpa": round(avg_gpa, 2),
        "avg_attendance": round(avg_attendance, 1),
        "avg_assignment": round(avg_assignment, 1),
        "avg_success_score": avg_success
    }

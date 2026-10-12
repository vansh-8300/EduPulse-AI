"""
Model Utilities for EduPulse AI
Handles model loading, inference, risk probability calculation, and feature indicator explanations.
"""

import os
import joblib
import pandas as pd

MODEL_PATH = "models/risk_model.pkl"

FEATURE_NAMES_REMAPPED = {
    "attendance_rate": "Attendance Rate (%)",
    "gpa": "GPA (4.0 Scale)",
    "assignment_completion_rate": "Assignment Completion (%)",
    "midterm_score": "Midterm Score (%)",
    "study_hours_per_week": "Study Hours / Week",
    "lms_engagement_score": "LMS Portal Engagement",
    "participation_score": "Class Participation",
    "stress_level": "Stress Level (1-10)"
}

def verify_model_integrity(filepath):
    """Verify SHA-256 checksum of model artifact against trusted hash file if present."""
    hash_path = filepath + ".sha256"
    if not os.path.exists(hash_path):
        return True
    import hashlib
    with open(hash_path, "r", encoding="utf-8") as f:
        expected_hash = f.read().strip()
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        hasher.update(f.read())
    computed_hash = hasher.hexdigest()
    if computed_hash != expected_hash:
        raise ValueError(
            f"Model integrity check failed for '{filepath}'. "
            f"Expected SHA-256 {expected_hash[:12]}..., got {computed_hash[:12]}..."
        )
    return True

def load_model(filepath=MODEL_PATH):
    """Load model artifact dictionary from pickle file after verifying SHA-256 integrity."""
    if not os.path.exists(filepath):
        from train_model import train_risk_model
        return train_risk_model()

    verify_model_integrity(filepath)
    artifact = joblib.load(filepath)
    return artifact


def predict_student_risk(student_data, artifact=None):
    """
    Predict risk level and probability distribution for a student record.
    student_data can be a pandas Series or dictionary containing feature values.
    """
    if artifact is None:
        artifact = load_model()

    model = artifact["model"]
    feature_cols = artifact["features"]

    # Prepare feature vector with input validation
    if isinstance(student_data, dict):
        missing = [c for c in feature_cols if c not in student_data]
        if missing:
            raise ValueError(f"Missing required feature columns for prediction: {missing}")
        input_df = pd.DataFrame([student_data])[feature_cols]
    else:
        missing = [c for c in feature_cols if c not in student_data.index]
        if missing:
            raise ValueError(f"Missing required feature columns for prediction: {missing}")
        input_df = pd.DataFrame([student_data[feature_cols].to_dict()])[feature_cols]

    input_df = input_df.astype(float)

    predicted_class = model.predict(input_df)[0]
    probabilities = model.predict_proba(input_df)[0]
    prob_dict = dict(zip(model.classes_, probabilities))

    high_p = round(prob_dict.get("High", 0.0) * 100, 1)
    med_p = round(prob_dict.get("Medium", 0.0) * 100, 1)
    low_p = round(prob_dict.get("Low", 0.0) * 100, 1)
    success_score = max(0.0, min(100.0, round(100.0 - (high_p * 0.85 + med_p * 0.35), 1)))

    return {
        "predicted_risk": predicted_class,
        "probabilities": prob_dict,
        "high_risk_prob": high_p,
        "medium_risk_prob": med_p,
        "low_risk_prob": low_p,
        "success_score": success_score
    }

def predict_placement_risk(student_data):
    """
    Predict placement readiness risk level and score for career/internship placement.
    """
    gpa = float(student_data.get("gpa", 3.0))
    assignment = float(student_data.get("assignment_completion_rate", 80.0))
    lms = float(student_data.get("lms_engagement_score", 70.0))
    grade = str(student_data.get("grade_level", "Junior"))
    study_hours = float(student_data.get("study_hours_per_week", 15.0))

    reasons = []

    # Calculate Placement Readiness Score (0 to 100)
    placement_score = round(
        (gpa / 4.0 * 100) * 0.35 +
        assignment * 0.25 +
        lms * 0.20 +
        min(100.0, study_hours / 25.0 * 100) * 0.20,
        1
    )

    if gpa < 2.5:
        reasons.append("GPA is below technical screening threshold (2.5)")
    if assignment < 70.0:
        reasons.append("Assignment completion rate is below industry prep threshold (70%)")
    if lms < 65.0:
        reasons.append("LMS engagement indicates low activity in technical modules")

    if gpa < 2.4 or (grade in ["Junior", "Senior"] and assignment < 68.0):
        placement_risk = "High"
    elif gpa < 2.95 or lms < 68.0 or assignment < 78.0:
        placement_risk = "Medium"
    else:
        placement_risk = "Low"

    return {
        "placement_risk": placement_risk,
        "placement_score": max(0.0, min(100.0, placement_score)),
        "placement_reasons": reasons
    }


def explain_student_indicators(student_data, artifact=None):
    """
    Analyze key indicators contributing to a student's risk prediction.
    Compares student metrics against cohort averages, weighted by Random Forest feature importance.
    """
    if artifact is None:
        artifact = load_model()

    feature_cols = artifact["features"]
    importances = artifact["feature_importances"]
    cohort_stats = artifact["cohort_stats"]

    indicators = []

    for feat in feature_cols:
        val = float(student_data[feat])
        mean_val = cohort_stats[feat]["mean"]
        std_val = cohort_stats[feat]["std"] if cohort_stats[feat]["std"] > 0 else 1.0
        imp = importances.get(feat, 0.1)

        # Stress level: higher is worse; for others: lower is worse
        if feat == "stress_level":
            z_score = (val - mean_val) / std_val
            is_risk = z_score > 0.5
            is_strength = z_score < -0.5
        else:
            z_score = (val - mean_val) / std_val
            is_risk = z_score < -0.5
            is_strength = z_score > 0.5

        impact_score = abs(z_score) * imp * 100

        if is_risk:
            status = "Risk Driver"
            badge = "🔴 Critical" if abs(z_score) > 1.2 else "🟡 Concern"
        elif is_strength:
            status = "Positive Strength"
            badge = "🟢 Strong"
        else:
            status = "Average"
            badge = "⚪ Normal"

        pretty_name = FEATURE_NAMES_REMAPPED.get(feat, feat)

        indicators.append({
            "feature_key": feat,
            "feature_name": pretty_name,
            "student_value": val,
            "cohort_avg": round(mean_val, 1),
            "z_score": round(z_score, 2),
            "importance": round(imp * 100, 1),
            "impact_score": round(impact_score, 1),
            "status": status,
            "badge": badge
        })

    # Sort indicators by impact score descending
    indicators.sort(key=lambda x: x["impact_score"], reverse=True)
    return indicators

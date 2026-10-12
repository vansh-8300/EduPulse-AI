"""
Unit tests for machine learning inference and model utilities in src/model_utils.py
"""

import pytest
import pandas as pd
from src.model_utils import (
    load_model,
    verify_model_integrity,
    predict_student_risk,
    predict_placement_risk,
    explain_student_indicators
)

def test_model_artifact_loading_and_integrity(model_artifact):
    """Ensure the model artifact dictionary contains required keys and verified SHA-256."""
    assert "model" in model_artifact
    assert "features" in model_artifact
    assert "classes" in model_artifact
    assert "feature_importances" in model_artifact
    assert "cohort_stats" in model_artifact

    assert verify_model_integrity("models/risk_model.pkl") is True

def test_predict_student_risk_output_contract(model_artifact, sample_student_dict):
    """Verify inference output structure, probability constraints, and success score range."""
    pred = predict_student_risk(sample_student_dict, model_artifact)

    assert "predicted_risk" in pred
    assert pred["predicted_risk"] in ["High", "Medium", "Low"]
    assert "high_risk_prob" in pred
    assert "medium_risk_prob" in pred
    assert "low_risk_prob" in pred
    assert "success_score" in pred
    assert 0.0 <= pred["success_score"] <= 100.0

    # Ensure probabilities sum approximately to 100%
    total_prob = pred["high_risk_prob"] + pred["medium_risk_prob"] + pred["low_risk_prob"]
    assert 99.0 <= total_prob <= 101.0

def test_predict_student_risk_missing_features_raises_error(model_artifact):
    """Verify that passing an incomplete student record raises a clear ValueError."""
    incomplete_student = {"name": "Test", "gpa": 3.0}
    with pytest.raises(ValueError, match="Missing required feature columns"):
        predict_student_risk(incomplete_student, model_artifact)

def test_predict_placement_risk_thresholds(high_risk_student_dict, sample_student_dict):
    """Verify placement risk classification and scoring."""
    high_place = predict_placement_risk(high_risk_student_dict)
    assert high_place["placement_risk"] == "High"
    assert len(high_place["placement_reasons"]) > 0

    norm_place = predict_placement_risk(sample_student_dict)
    assert norm_place["placement_risk"] in ["Low", "Medium"]
    assert 0.0 <= norm_place["placement_score"] <= 100.0

def test_explain_student_indicators_z_scores_and_weights(model_artifact, sample_student_dict):
    """Verify feature explanation indicators and sorting."""
    indicators = explain_student_indicators(sample_student_dict, model_artifact)
    assert len(indicators) == len(model_artifact["features"])

    for ind in indicators:
        assert "feature_key" in ind
        assert "feature_name" in ind
        assert "z_score" in ind
        assert "impact_score" in ind
        assert "status" in ind
        assert "badge" in ind

    # Check descending order by impact score
    for i in range(len(indicators) - 1):
        assert indicators[i]["impact_score"] >= indicators[i + 1]["impact_score"]

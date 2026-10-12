"""
EduPulse AI - FastAPI High-Performance Backend Service
Provides RESTful endpoints for ML risk predictions, explainable indicators, and support recommendations.
"""

from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.data_loader import load_student_data, get_cohort_kpis
from src.model_utils import load_model, predict_student_risk, explain_student_indicators, predict_placement_risk
from src.recommendations import generate_recommendations

# Global artifact container
ml_artifact = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler to load ML model artifact once on startup."""
    global ml_artifact
    try:
        ml_artifact = load_model()
        print("[INFO] FastAPI Lifespan: Random Forest ML model artifact successfully loaded into memory.")
    except Exception as e:
        print(f"[ERROR] FastAPI Lifespan: Failed to load model artifact: {e}")
        ml_artifact = None
    yield
    ml_artifact = None

# Initialize FastAPI Application
app = FastAPI(
    title="EduPulse AI - Student Analytics & Success API",
    description="RESTful API service providing real-time Random Forest risk prediction, indicator impact explanations, and personalized academic intervention recommendations.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Pydantic Data Models ---
class StudentPredictRequest(BaseModel):
    student_id: Optional[str] = Field("EDU-SAMPLE-001", description="Student Unique Identifier")
    name: Optional[str] = Field("Sample Student", description="Student Full Name")
    major: Optional[str] = Field("Computer Science", description="Department / Major")
    grade_level: Optional[str] = Field("Junior", description="Grade Level (Freshman, Sophomore, Junior, Senior)")
    attendance_rate: float = Field(..., ge=0.0, le=100.0, examples=[85.0], description="Attendance Percentage (0-100)")
    gpa: float = Field(..., ge=0.0, le=4.0, examples=[3.2], description="GPA on 4.0 Scale")
    assignment_completion_rate: float = Field(..., ge=0.0, le=100.0, examples=[90.0], description="Assignment Completion Percentage (0-100)")
    midterm_score: float = Field(..., ge=0.0, le=100.0, examples=[78.0], description="Midterm Score Percentage (0-100)")
    study_hours_per_week: float = Field(..., ge=0.0, le=168.0, examples=[15.0], description="Study Hours per Week")
    lms_engagement_score: float = Field(..., ge=0.0, le=100.0, examples=[80.0], description="LMS Portal Engagement Score (0-100)")
    participation_score: float = Field(..., ge=0.0, le=100.0, examples=[75.0], description="Class Participation Score (0-100)")
    stress_level: int = Field(..., ge=1, le=10, examples=[4], description="Stress Level Scale (1-10)")
    tuition_status: Optional[str] = Field("Paid", description="Tuition Payment Status (Paid / Pending)")


class StudentPredictResponse(BaseModel):
    student_id: Optional[str]
    name: Optional[str]
    predicted_risk: str
    high_risk_prob: float
    medium_risk_prob: float
    low_risk_prob: float
    success_score: float
    placement_risk: str
    placement_score: float
    placement_reasons: List[str]
    indicators: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]


class HealthCheckResponse(BaseModel):
    status: str
    service: str
    version: str
    model_loaded: bool
    feature_count: int


# --- API Endpoints ---
@app.get("/", summary="API Root Overview")
def read_root():
    return {
        "message": "Welcome to EduPulse AI RESTful API Service",
        "documentation": "/docs",
        "health_check": "/health"
    }


@app.get("/health", response_model=HealthCheckResponse, summary="Service Health Check")
def health_check():
    global ml_artifact
    if ml_artifact is None:
        try:
            ml_artifact = load_model()
        except Exception:
            pass

    is_loaded = ml_artifact is not None
    feature_count = len(ml_artifact["features"]) if is_loaded and "features" in ml_artifact else 0

    return HealthCheckResponse(
        status="healthy" if is_loaded else "degraded",
        service="EduPulse AI FastAPI Service",
        version="1.0.0",
        model_loaded=is_loaded,
        feature_count=feature_count
    )


@app.post("/predict", response_model=StudentPredictResponse, summary="Predict Student Risk & Support Plan")
def predict_student(request: StudentPredictRequest):
    global ml_artifact
    if ml_artifact is None:
        try:
            ml_artifact = load_model()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Machine Learning model artifact is unavailable: {e}"
            )

    student_data = request.model_dump()

    try:
        # 1. Execute ML Risk Prediction
        risk_pred = predict_student_risk(student_data, ml_artifact)
        
        # 2. Execute Placement Readiness Evaluation
        placement_pred = predict_placement_risk(student_data)

        # 3. Execute Explainable Feature Indicator Impact Analysis
        indicators = explain_student_indicators(student_data, ml_artifact)

        # 4. Generate Personalized Support Recommendations
        recommendations = generate_recommendations(student_data, risk_pred, placement_pred)

        return StudentPredictResponse(
            student_id=request.student_id,
            name=request.name,
            predicted_risk=risk_pred["predicted_risk"],
            high_risk_prob=risk_pred["high_risk_prob"],
            medium_risk_prob=risk_pred["medium_risk_prob"],
            low_risk_prob=risk_pred["low_risk_prob"],
            success_score=risk_pred["success_score"],
            placement_risk=placement_pred["placement_risk"],
            placement_score=placement_pred["placement_score"],
            placement_reasons=placement_pred["placement_reasons"],
            indicators=indicators,
            recommendations=recommendations
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error executing prediction pipeline: {e}"
        )


@app.get("/cohort/kpis", summary="Get Cohort Performance KPIs")
def get_kpis():
    try:
        df = load_student_data()
        kpis = get_cohort_kpis(df)
        return kpis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compute cohort KPIs: {e}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)

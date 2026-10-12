# 🎓 EduPulse AI - Student Analytics & Success Platform

> **Early Academic Risk Detection & Intelligent Support Recommendation Engine**

EduPulse AI is an end-to-end Machine Learning powered educational analytics platform designed to help educators, academic advisors, and institutional administrators identify early signs of academic risk and deliver personalized, actionable support interventions to students.

---

### 🌐 Quick Links & Access Points

| Link | Destination | Description |
|---|---|---|
| 🌐 **View Prototype** | [Open Prototype](https://vansh-8300.github.io/EduPulse-AI/) | Interactive System Architecture Showcase |
| 🚀 **Live Dashboard** | [Launch EduPulse AI](https://vansh-8300-edupulse-ai-app-upe9tn.streamlit.app/) | Interactive Streamlit application |
| 💻 **View Source Code** | [GitHub Repository](https://github.com/vansh-8300/EduPulse-AI) | Project source code |
| 📦 **Legacy Prototype** | [Open Backup](https://vansh-8300.github.io/EduPulse-AI/prototype_backup.html) | Archived prototype backup |

> ℹ️ **Streamlit Deployment:** The live interactive dashboard is deployed and running on [Streamlit Community Cloud](https://vansh-8300-edupulse-ai-app-upe9tn.streamlit.app/).


> ⚠️ **Hackathon & Prototype Disclaimer**: The dataset (`students_1200.csv`) is synthetically generated for demonstration purposes, and the trained model is a proof-of-concept prototype. It is not validated for real-world institutional or high-stakes academic decision-making.

---

## 🌟 Key Features

* **📊 Cohort Analytics Overview**: Real-time cohort KPIs (Total Students, High Risk %, Avg GPA, Avg Attendance, Assignment Completion) accompanied by Plotly visual analytics (Risk Distribution, GPA vs. Attendance Scatter, Department & Grade Level Risk Breakdowns).
* **🎓 Student Risk Predictor & Deep-Dive**: Search and inspect individual student profiles to view Machine Learning risk predictions (`High`, `Medium`, `Low`), class probabilities, placement readiness scores, and feature indicator z-score impact badges.
* **🛠️ Personalized Recommendation Engine**: Context-aware intervention generator that maps low metrics to specific recovery actions (e.g., bi-weekly advisor coaching, peer tutoring, LMS orientation, wellness counseling, financial aid assistance).
* **🔮 Interactive What-If Simulator**: Real-time scenario planning tool allowing advisors to adjust student parameters (attendance, study hours, assignment completion, stress level) and visually compare simulated vs. baseline risk probabilities.
* **📁 Student Data Explorer**: Interactive directory featuring multi-attribute filtering (Major, Grade Level, Risk Level) and instant formula-sanitized CSV data export.

---

## 🛠️ Technology Stack

* **Core Language**: Python 3.14
* **Interactive Web Framework**: Streamlit (v1.65.0)
* **Primary Hosting Platform**: Streamlit Community Cloud (* **Live Dashboard**: [Launch EduPulse AI](https://vansh-8300-edupulse-ai-app-upe9tn.streamlit.app/))
* **Static Prototype Host**: GitHub Pages ([https://vansh-8300.github.io/EduPulse-AI/](https://vansh-8300.github.io/EduPulse-AI/))
* **Machine Learning**: Scikit-Learn (v1.9.1) - Random Forest Classifier
* **Data Processing & Analytics**: Pandas, NumPy
* **Data Visualization**: Plotly Express & Plotly Graph Objects
* **Model Serialization**: Joblib with SHA-256 integrity checksum verification

---

## 🤖 Model Approach & Architecture

### Data Generation & Feature Engineering
Synthetic data generator (`generate_data.py`) generates 1,200 student academic profiles based on latent capability indices and correlated metrics:
* **Academic Metrics**: Attendance Rate (%), GPA (4.0 scale), Assignment Completion Rate (%), Midterm Score (%), Study Hours/Week.
* **Engagement & Well-being**: LMS Portal Engagement, Class Participation, Stress Level (1-10 scale), Tuition Payment Status.

### Machine Learning Classifier
* **Algorithm**: `RandomForestClassifier` (120 estimators, max depth 10, class-balanced weights).
* **Training Pipeline**: `train_model.py` performs an 80/20 stratified split (`train_test_split`) to maintain risk class proportions.
* **Performance**: Achieves **90.00% evaluation accuracy** across 3 risk tiers (`High`, `Medium`, `Low`).

---

## 📁 Repository Structure

```
EduPulse_AI/
├── app.py                  # Main Streamlit interactive web application
├── api.py                  # FastAPI REST backend microservice (optional API layer)
├── generate_data.py        # Synthetic dataset generator script
├── train_model.py          # Machine learning model training script
├── requirements.txt        # Python dependency specifications
├── index.html              # Main GitHub Pages interactive architecture showcase
├── architecture.html       # Standalone architecture showcase page
├── prototype_backup.html   # Preserved backup of legacy presentation prototype
├── .gitignore              # Git ignore rules for virtualenvs & cache
├── README.md               # Project documentation & setup guide
├── tests/                  # Automated pytest test suite
│   ├── conftest.py         # Pytest fixtures & mock data setup
│   ├── test_data_loader.py # Data loader, schema & regex filter tests
│   ├── test_model_utils.py # Model integrity, prediction & explanation tests
│   ├── test_recommendations.py # Prescriptive intervention engine tests
│   ├── test_api_endpoints.py # FastAPI TestClient integration tests
│   ├── test_auth_helpers.py # Firebase auth mock tests & error mappings
│   └── test_security_audit.py # Automated secret scanning & gitignore tests
├── data/
│   └── students_1200.csv   # Generated student dataset (1,200 records)
├── models/
│   ├── risk_model.pkl      # Saved Random Forest model artifact
│   └── risk_model.pkl.sha256 # SHA-256 integrity checksum
└── src/
    ├── __init__.py         # Package initializer
    ├── data_loader.py      # Data loading, filtering & KPI computation
    ├── model_utils.py       # Model loading, inference & indicator explanation
    └── recommendations.py  # Personalized academic intervention logic
```

---

## 🚀 Local Setup & Quickstart

### 1. Clone the Repository
```bash
git clone https://github.com/vansh-8300/EduPulse-AI.git
cd EduPulse-AI
```

### 2. Set Up Virtual Environment & Dependencies
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Generate Data & Train Model (Optional / Pre-packaged)
```bash
# Generate 1,200 synthetic student records
python generate_data.py

# Train the Random Forest model
python train_model.py
```

### 4. Run the Automated Test Suite
```bash
pytest tests/ -v
```

### 5. Optional Secrets Configuration
EduPulse AI works out-of-the-box with pre-configured client authentication for evaluation. For custom Firebase projects, you can configure your API key in `.streamlit/secrets.toml` (which is excluded from Git):
```toml
FIREBASE_API_KEY = <YOUR_FIREBASE_API_KEY>
```
Or via an environment variable:
```bash
export FIREBASE_API_KEY=<YOUR_FIREBASE_API_KEY>
```

### 6. Run the Streamlit Dashboard Locally
```bash
python -m streamlit run app.py
```
Open your browser and navigate to `http://localhost:8501`.

### 7. Run the Optional FastAPI Backend Service
```bash
uvicorn api:app --reload --port 8000
```
API documentation will be available at `http://localhost:8000/docs`.

---

## ☁️ Streamlit Community Cloud Deployment Guide

EduPulse AI is configured for one-click deployment on **Streamlit Community Cloud** ([https://share.streamlit.io/](https://share.streamlit.io/)). Follow these steps to host your live interactive dashboard:

### Deployment Steps:
1. **Sign in to Streamlit Community Cloud**:
   Go to [https://share.streamlit.io/](https://share.streamlit.io/) and log in with your GitHub account.

2. **Create New App**:
   Click the **"New app"** / **"Create app"** button in your dashboard workspace.

3. **Configure Repository Settings**:
   - **Repository**: `vansh-8300/EduPulse-AI`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL** (Optional custom subdomain): e.g. `edupulse-ai`

4. **Deploy Application**:
   Click **"Deploy!"**. Streamlit Community Cloud will automatically install dependencies from `requirements.txt` and launch `app.py`.

5. **Live Application URL**:
   The interactive dashboard is deployed and live at [https://vansh-8300-edupulse-ai-app-upe9tn.streamlit.app/](https://vansh-8300-edupulse-ai-app-upe9tn.streamlit.app/).

---

## ⚠️ Limitations & Future Roadmap

* **Synthetic Data Base**: Current model is trained on realistic synthetic student data. Future iterations will support direct LMS database integration (e.g., Canvas, Blackboard API via OAuth 2.0).
* **Demographic Bias Protection**: Intentionally excludes demographic attributes to prevent bias in academic risk prediction.
* **Longitudinal Tracking**: Future releases will incorporate time-series modeling to track student metric trends across multiple semesters.

---

## 🔐 Production Deployment & Security Requirements

Prior to deploying EduPulse AI in a live university environment with real student records:
1. **Authentication & FERPA Authorization**: Implement Single Sign-On (OAuth 2.0 / SAML 2.0 via Azure AD or Google Workspace) and strict Role-Based Access Control (RBAC) to ensure students can access only their own metrics while advisors access assigned cohorts.
2. **Model Deserialization Integrity**: SHA-256 checksum verification is enforced via `verify_model_integrity()` in `src/model_utils.py` prior to `joblib.load()`.
3. **CSV Export Sanitization**: Spreadsheet formula trigger escaping (`=`, `+`, `-`, `@`) is applied to CSV downloads to prevent spreadsheet code execution attacks.
4. **FastAPI Microservice Layer**: For REST API integration, `api.py` provides validated `/health` and `/predict` endpoints using Pydantic request validation.
